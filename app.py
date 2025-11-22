import asyncio
import os
import sys
import logging
import json
from typing import List
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import shutil
from pathlib import Path
import uuid
from datetime import datetime
from pydantic import BaseModel

# Add mediachain to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'mediachain'))

from mediachain.examples.moviepy_engine.reddit_stories.generate_reddit_story import RedditStoryGenerator
from script_parser import parse_dialogue_script, validate_two_speakers
from instagram_manager import InstagramManager
from elevenlabs_utils import get_available_voices, generate_dialogue_audio, concatenate_audio_segments

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Reddit Story Video Generator",
    description="Generate AI-powered Reddit story videos with custom backgrounds",
    version="1.0.0"
)

# Initialize Instagram Manager
instagram_manager = InstagramManager()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create directories for uploads and outputs
UPLOAD_DIR = Path("uploads")
OUTPUT_DIR = Path("outputs")
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# Configuration
AVATAR_SIZE = 700  # Fixed height in pixels for speaker avatars
DEFAULT_VIDEOS_DIR = Path("default_videos")  # Directory containing default background videos

# Mount static files (for serving the frontend)
app.mount("/static", StaticFiles(directory="static", html=True), name="static")
app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")

# Public URL for Instagram to access videos (e.g., ngrok url)
PUBLIC_URL = os.getenv("PUBLIC_URL", "http://localhost:8000")

# Store processing status
processing_status = {}

# Store extension session data (dialogue + images)
extension_sessions = {}


def add_dialogue_images_to_video(
    video_clip,
    dialogue_images_map: dict,
    audio_segments: list
) -> list:
    """
    Add user-uploaded images to video at dialogue timing.
    Images positioned at top third, similar to DALL-E.
    
    Args:
        video_clip: The video clip to add images to
        dialogue_images_map: Dictionary mapping dialogue index to image path
        audio_segments: List of audio segment dicts with timing info
        
    Returns:
        List of image clips to overlay
    """
    from moviepy.editor import ImageClip, AudioFileClip
    
    if not dialogue_images_map:
        return []
    
    logger.info(f"[IMAGE_OVERLAY] Adding {len(dialogue_images_map)} dialogue images to video")
    
    image_clips = []
    
    # Calculate cumulative timing for each dialogue
    cumulative_time = 0.0
    dialogue_timings = []
    previous_speaker = None
    
    for idx, segment in enumerate(audio_segments):
        start_time = cumulative_time
        
        # Add 1s gap if speaker changed
        if idx > 0 and segment['speaker'] != previous_speaker:
            cumulative_time += 1.0
            start_time = cumulative_time
        
        # Get audio duration
        audio_path = segment['audio_path']
        if audio_path and os.path.exists(audio_path):
            audio_clip = AudioFileClip(audio_path)
            duration = audio_clip.duration
            audio_clip.close()
        else:
            # Fallback: estimate duration based on text length (rough estimate)
            text_length = len(segment.get('text', ''))
            duration = max(2.0, text_length / 15.0)  # ~15 chars per second speaking rate
            logger.warning(f"[IMAGE_OVERLAY] Using estimated duration for segment {idx}: {duration:.2f}s")
        
        end_time = cumulative_time + duration
        dialogue_timings.append({
            'index': idx,
            'start': start_time,
            'end': end_time,
            'duration': duration,
            'speaker': segment['speaker']
        })
        cumulative_time = end_time
        previous_speaker = segment['speaker']
    
    # Add image clips
    for dialogue_idx, image_path in dialogue_images_map.items():
        if dialogue_idx >= len(dialogue_timings):
            logger.warning(f"[IMAGE_OVERLAY] Skipping image for dialogue {dialogue_idx} - index out of range")
            continue
        
        timing = dialogue_timings[dialogue_idx]
        start_time = timing['start']
        
        # Calculate end time: until next image or max 5 seconds
        end_time = timing['end']
        
        # Check if there's a next image
        next_image_idx = None
        for idx in range(dialogue_idx + 1, len(dialogue_timings)):
            if idx in dialogue_images_map:
                next_image_idx = idx
                break
        
        if next_image_idx:
            # End at the start of next image
            end_time = min(end_time, dialogue_timings[next_image_idx]['start'])
        
        # Cap at 5 seconds max
        duration = min(end_time - start_time, 5.0)
        
        logger.info(f"[IMAGE_OVERLAY] Dialogue {dialogue_idx}: {start_time:.2f}s - {start_time + duration:.2f}s ({duration:.2f}s)")
        
        try:
            # Create image clip (positioned at top third like DALL-E)
            image_clip = (ImageClip(image_path)
                         .set_duration(duration)
                         .set_position(('center', 70))
                         .resize(height=video_clip.h / 3)
                         .set_start(start_time))
            
            image_clips.append(image_clip)
        except Exception as e:
            logger.error(f"[IMAGE_OVERLAY] Error adding image for dialogue {dialogue_idx}: {e}")
    
    logger.info(f"[IMAGE_OVERLAY] ✓ Added {len(image_clips)} image clips")
    return image_clips


def add_speaker_avatars_to_video(
    video_clip,
    speaker_avatars: dict,
    audio_segments: list,
    speakers_list: list
) -> list:
    """
    Add speaker avatar images that appear when each speaker is talking.
    Square avatars positioned at bottom corners.
    
    Args:
        video_clip: The video clip
        speaker_avatars: Dict mapping speaker name to avatar image path
        audio_segments: List of audio segment dicts
        speakers_list: List of speaker names [speaker1, speaker2]
        
    Returns:
        List of avatar clips
    """
    from moviepy.editor import ImageClip, AudioFileClip
    
    if not speaker_avatars:
        return []
    
    logger.info(f"[AVATAR] Adding speaker avatars to video")
    
    avatar_clips = []
    
    # Calculate timing for each segment
    cumulative_time = 0.0
    previous_speaker = None
    
    # Fixed positioning constants
    # AVATAR_SIZE is defined globally
    logger.info(f"[AVATAR] Using AVATAR_SIZE: {AVATAR_SIZE}")
    MARGIN = 20  # Margin from edges
    BOTTOM_OFFSET = 100  # Distance from bottom
    
    for idx, segment in enumerate(audio_segments):
        speaker = segment['speaker']
        
        # Skip if no avatar for this speaker
        if speaker not in speaker_avatars:
            cumulative_time_before = cumulative_time
            
            # Calculate duration to advance cumulative_time
            audio_path = segment['audio_path']
            if audio_path and os.path.exists(audio_path):
                audio_clip = AudioFileClip(audio_path)
                duration = audio_clip.duration
                audio_clip.close()
            else:
                text_length = len(segment.get('text', ''))
                duration = max(2.0, text_length / 15.0)
            
            # Add 1s gap if speaker changed
            if idx > 0 and segment['speaker'] != previous_speaker:
                cumulative_time += 1.0
            
            cumulative_time += duration
            previous_speaker = speaker
            continue
        
        # Add 1s gap if speaker changed
        if idx > 0 and segment['speaker'] != previous_speaker:
            cumulative_time += 1.0
        
        start_time = cumulative_time
        
        # Get audio duration
        audio_path = segment['audio_path']
        if audio_path and os.path.exists(audio_path):
            audio_clip = AudioFileClip(audio_path)
            duration = audio_clip.duration
            audio_clip.close()
        else:
            # Fallback estimation
            text_length = len(segment.get('text', ''))
            duration = max(2.0, text_length / 15.0)
        
        cumulative_time += duration
        
        # Determine position based on speaker
        try:
            speaker_index = speakers_list.index(speaker)
        except ValueError:
            logger.warning(f"[AVATAR] Speaker {speaker} not in speakers list, skipping")
            previous_speaker = speaker
            continue
        
        if len(speakers_list) == 1:
            # Single speaker: Center bottom
            position = ('center', video_clip.h - AVATAR_SIZE - BOTTOM_OFFSET)
        elif speaker_index == 0:
            # Speaker 1 (of 2): Bottom left
            position = (MARGIN, video_clip.h - AVATAR_SIZE - BOTTOM_OFFSET)
        else:
            # Speaker 2 (of 2): Bottom right
            position = (video_clip.w - AVATAR_SIZE - MARGIN, 
                       video_clip.h - AVATAR_SIZE - BOTTOM_OFFSET)
        
        logger.info(f"[AVATAR] {speaker} at {start_time:.2f}s-{start_time+duration:.2f}s, pos={position}")
        
        try:
            # Create square avatar clip (no circular mask, just resize to square)
            avatar_clip = (ImageClip(speaker_avatars[speaker])
                          .set_duration(duration)
                          .resize(height=AVATAR_SIZE)
                          .set_position(position)
                          .set_start(start_time))
            
            avatar_clips.append(avatar_clip)
            
        except Exception as e:
            logger.error(f"[AVATAR] Error adding avatar for {speaker}: {e}")
        
        previous_speaker = speaker
    
    logger.info(f"[AVATAR] ✓ Added {len(avatar_clips)} avatar clips")
    return avatar_clips


@app.get("/")
async def root():
    """Serve the main HTML page"""
    return FileResponse("static/index.html")


@app.get("/script")
async def script_mode():
    """Serve the script mode HTML page"""
    return FileResponse("static/script_mode.html")


@app.post("/api/generate-video")
async def generate_video(
    video: UploadFile = File(...),
    topic: str = Form(...),
    add_images: bool = Form(True),
    loop_if_short: bool = Form(True),
    font_color: str = Form("white"),
    shadow_color: str = Form("black")
):
    """
    Generate a Reddit story video from uploaded video file
    
    Args:
        video: Uploaded video file
        topic: The story topic/question
        add_images: Whether to add AI-generated images
        font_color: Caption font color
        shadow_color: Caption shadow color
    """
    job_id = str(uuid.uuid4())
    processing_status[job_id] = {"status": "processing", "progress": 0}
    
    logger.info("="*80)
    logger.info(f"[JOB {job_id}] New video generation request")
    logger.info("="*80)
    
    try:
        # Validate file
        logger.info(f"[JOB {job_id}] Validating uploaded file: {video.filename}")
        if not video.filename.endswith(('.mp4', '.mov', '.avi', '.mkv')):
            logger.error(f"[JOB {job_id}] Invalid file format: {video.filename}")
            raise HTTPException(status_code=400, detail="Invalid video format. Use MP4, MOV, AVI, or MKV")
        
        # Save uploaded video
        video_filename = f"{job_id}_{video.filename}"
        video_path = UPLOAD_DIR / video_filename
        
        logger.info(f"[JOB {job_id}] Saving uploaded video to {video_path}")
        file_size = 0
        with video_path.open("wb") as buffer:
            chunk_size = 1024 * 1024  # 1MB chunks
            while chunk := video.file.read(chunk_size):
                buffer.write(chunk)
                file_size += len(chunk)
        
        logger.info(f"[JOB {job_id}] ✓ Video saved: {file_size / (1024*1024):.2f} MB")
        
        processing_status[job_id]["progress"] = 10
        processing_status[job_id]["message"] = "Video uploaded, starting generation..."
        
        # Initialize generator
        logger.info(f"[JOB {job_id}] Initializing RedditStoryGenerator")
        openai_api_key = os.getenv('OPENAI_API_KEY')
        if not openai_api_key:
            logger.error(f"[JOB {job_id}] OPENAI_API_KEY not configured")
            raise HTTPException(status_code=500, detail="OPENAI_API_KEY not set in environment")
        
        reddit_generator = RedditStoryGenerator(openai_api_key=openai_api_key)
        
        processing_status[job_id]["progress"] = 20
        processing_status[job_id]["message"] = "Generating script..."
        
        # Generate video
        captions_settings = {
            'color': font_color,
            'shadow_color': shadow_color
        }
        
        logger.info(f"[JOB {job_id}] Starting video generation")
        logger.info(f"[JOB {job_id}] Topic: {topic}")
        logger.info(f"[JOB {job_id}] Add images: {add_images}")
        logger.info(f"[JOB {job_id}] Loop if short: {loop_if_short} (type: {type(loop_if_short).__name__})")
        logger.info(f"[JOB {job_id}] Caption color: {font_color}, shadow: {shadow_color}")
        
        # Verify loop_if_short is actually a boolean
        if not isinstance(loop_if_short, bool):
            logger.warning(f"[JOB {job_id}] Converting loop_if_short from {type(loop_if_short)} to bool")
            loop_if_short = str(loop_if_short).lower() in ('true', '1', 'yes', 'on')
        
        result = await reddit_generator.generate_video(
            video_path_or_url='video_path',
            video_path=str(video_path),
            video_topic=topic,
            captions_settings=captions_settings,
            add_images=add_images,
            loop_if_short=loop_if_short
        )
        
        processing_status[job_id]["progress"] = 100
        
        if result["status"] == "success":
            output_file = result["output_path"]
            processing_status[job_id]["status"] = "completed"
            processing_status[job_id]["output_path"] = output_file
            
            logger.info(f"[JOB {job_id}] ✓✓✓ SUCCESS ✓✓✓")
            logger.info(f"[JOB {job_id}] Output: {output_file}")
            
            # Clean up uploaded video
            video_path.unlink(missing_ok=True)
            logger.info(f"[JOB {job_id}] Cleaned up uploaded file")
            
            return JSONResponse({
                "status": "success",
                "job_id": job_id,
                "message": "Video generated successfully!",
                "download_url": f"/api/download/{Path(output_file).name}"
            })
        else:
            processing_status[job_id]["status"] = "failed"
            error_msg = result.get("message", "Failed to generate video")
            logger.error(f"[JOB {job_id}] ✗ Generation failed: {error_msg}")
            
            return JSONResponse({
                "status": "error",
                "job_id": job_id,
                "message": error_msg
            }, status_code=500)
    
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"[JOB {job_id}] ✗✗✗ EXCEPTION ✗✗✗")
        logger.error(f"[JOB {job_id}] {str(e)}")
        logger.exception("Full traceback:")
        
        processing_status[job_id]["status"] = "failed"
        processing_status[job_id]["error"] = str(e)
        
        # Clean up uploaded file on error
        if video_path and video_path.exists():
            video_path.unlink(missing_ok=True)
            logger.info(f"[JOB {job_id}] Cleaned up uploaded file after error")
        
        raise HTTPException(status_code=500, detail=f"Error generating video: {str(e)}")


@app.get("/api/status/{job_id}")
async def get_status(job_id: str):
    """Get the status of a video generation job"""
    if job_id not in processing_status:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return JSONResponse(processing_status[job_id])


@app.get("/api/download/{filename}")
async def download_video(filename: str):
    """Download the generated video"""
    # Look in common output directories
    possible_paths = [
        Path(filename),
        OUTPUT_DIR / filename,
        Path("outputs") / filename,
        Path("final_videos") / filename,
        Path("mediachain/examples/moviepy_engine/outputs") / filename,
        Path("mediachain/examples/moviepy_engine/final_videos") / filename
    ]
    
    for file_path in possible_paths:
        if file_path.exists():
            return FileResponse(
                path=str(file_path),
                media_type="video/mp4",
                filename=f"reddit_story_{filename}"
            )
    
    raise HTTPException(status_code=404, detail="Video file not found")


@app.delete("/api/cleanup/{job_id}")
async def cleanup_job(job_id: str):
    """Clean up job data and files"""
    if job_id in processing_status:
        del processing_status[job_id]
    return JSONResponse({"status": "success", "message": "Job cleaned up"})


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Reddit Story Video Generator",
        "version": "1.0.0"
    }


@app.get("/api/voices/elevenlabs")
async def get_elevenlabs_voices():
    """Get all available ElevenLabs voices"""
    try:
        elevenlabs_api_key = os.getenv('ELEVENLABS_API_KEY')
        if not elevenlabs_api_key:
            raise HTTPException(status_code=500, detail="ELEVENLABS_API_KEY not set in environment")
        
        logger.info("[VOICES] Fetching ElevenLabs voices")
        voices = get_available_voices(elevenlabs_api_key)
        
        logger.info(f"[VOICES] ✓ Retrieved {len(voices)} voices")
        return JSONResponse({
            "status": "success",
            "voices": voices,
            "count": len(voices)
        })
        
    except Exception as e:
        logger.error(f"[VOICES] ✗ Error fetching voices: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching voices: {str(e)}")


@app.post("/api/parse-script")
async def parse_script(script: str = Form(...)):
    """Parse a dialogue script and extract speakers"""
    try:
        logger.info("[PARSE] Parsing dialogue script")
        dialogue, speakers = parse_dialogue_script(script)
        
        if not validate_two_speakers(speakers):
            return JSONResponse({
                "status": "error",
                "message": f"Script must have 1 or 2 speakers. Found: {len(speakers)}"
            }, status_code=400)
        
        logger.info(f"[PARSE] ✓ Parsed {len(dialogue)} dialogue segments")
        logger.info(f"[PARSE] Speakers: {', '.join(speakers)}")
        
        return JSONResponse({
            "status": "success",
            "dialogue": dialogue,
            "speakers": speakers,
            "segment_count": len(dialogue)
        })
        
    except Exception as e:
        logger.error(f"[PARSE] ✗ Error parsing script: {e}")
        raise HTTPException(status_code=500, detail=f"Error parsing script: {str(e)}")


@app.post("/api/preview-audio")
async def preview_audio(
    script: str = Form(...),
    speaker1_voice: str = Form(...),
    speaker2_voice: str = Form(...)
):
    """Generate preview audio for the dialogue"""
    try:
        job_id = str(uuid.uuid4())
        logger.info(f"[PREVIEW {job_id}] Generating audio preview")
        
        # Parse script
        dialogue, speakers = parse_dialogue_script(script)
        
        if not validate_two_speakers(speakers):
            raise HTTPException(status_code=400, detail="Script must have 1 or 2 speakers")
        
        # Get API key
        elevenlabs_api_key = os.getenv('ELEVENLABS_API_KEY')
        if not elevenlabs_api_key:
            raise HTTPException(status_code=500, detail="ELEVENLABS_API_KEY not set")
        
        # Map voices
        voice_mapping = {
            speakers[0]: speaker1_voice
        }
        if len(speakers) > 1:
            voice_mapping[speakers[1]] = speaker2_voice
        
        logger.info(f"[PREVIEW {job_id}] Voice mapping: {voice_mapping}")
        
        # Generate audio segments
        audio_result = generate_dialogue_audio(elevenlabs_api_key, dialogue, voice_mapping)
        
        if audio_result["count"] == 0:
            raise HTTPException(status_code=500, detail="Failed to generate audio")
        
        # Concatenate segments (with 1s gaps between speaker changes)
        preview_audio_path = f"/tmp/elevenlabs_audio/preview_{job_id}.mp3"
        
        concatenated_path = concatenate_audio_segments(audio_result["segments"], preview_audio_path)
        
        if not concatenated_path:
            raise HTTPException(status_code=500, detail="Failed to concatenate audio")
        
        logger.info(f"[PREVIEW {job_id}] ✓ Preview audio generated")
        
        # Store audio segments data for reuse (avoid regenerating on video creation)
        processing_status[f"preview_{job_id}"] = {
            "audio_path": concatenated_path,
            "segments": audio_result["segments"],
            "dialogue": dialogue,
            "speakers": speakers,
            "voice_mapping": voice_mapping
        }
        
        # Return FileResponse with custom headers for reuse
        response = FileResponse(
            path=concatenated_path,
            media_type="audio/mpeg",
            filename=f"preview_{job_id}.mp3"
        )
        response.headers["X-Audio-Path"] = concatenated_path
        response.headers["X-Preview-Job-Id"] = job_id  # Send job_id for data retrieval
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[PREVIEW] ✗ Error generating preview: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error generating preview: {str(e)}")


@app.post("/api/generate-video-script")
async def generate_video_script_mode(
    script: str = Form(...),
    speaker1_voice: str = Form(...),
    speaker2_voice: str = Form(...),
    video: UploadFile = File(None),  # Make video optional
    loop_if_short: bool = Form(True),
    font_color: str = Form('white'),
    shadow_color: str = Form('black'),
    preview_audio_path: str = Form(None),
    preview_job_id: str = Form(None),
    dialogue_images: List[UploadFile] = File(None),
    image_indices: str = Form(None),
    speaker1_avatar: UploadFile = File(None),
    speaker2_avatar: UploadFile = File(None)
):
    """
    Generate video using custom script with ElevenLabs voices
    
    Args:
        script: Dialogue script with speakers
        speaker1_voice: ElevenLabs voice ID for speaker 1
        speaker2_voice: ElevenLabs voice ID for speaker 2
        video: Uploaded video file (optional - will use random default if not provided)
        loop_if_short: Auto-loop if video is short
        font_color: Caption text color
        shadow_color: Caption shadow color
        preview_audio_path: Path to preview audio (if already generated)
        dialogue_images: List of uploaded image files for dialogue
        image_indices: JSON string mapping dialogue index to filename
    """
    job_id = str(uuid.uuid4())
    processing_status[job_id] = {"status": "processing", "progress": 0}
    
    logger.info("="*80)
    logger.info(f"[JOB {job_id}] New SCRIPT-MODE video generation")
    logger.info("="*80)
    
    try:
        # Handle video - either uploaded or random default
        if video and video.filename:
            # Validate uploaded file
            logger.info(f"[JOB {job_id}] Validating uploaded file: {video.filename}")
            if not video.filename.endswith(('.mp4', '.mov', '.avi', '.mkv')):
                logger.error(f"[JOB {job_id}] Invalid file format")
                raise HTTPException(status_code=400, detail="Invalid video format")
            
            # Save uploaded video
            video_filename = f"{job_id}_{video.filename}"
            video_path = UPLOAD_DIR / video_filename
            
            logger.info(f"[JOB {job_id}] Saving uploaded video")
            with video_path.open("wb") as buffer:
                shutil.copyfileobj(video.file, buffer)
        else:
            # Use random default video
            import random
            default_videos = list(DEFAULT_VIDEOS_DIR.glob("*.mp4"))
            
            if not default_videos:
                raise HTTPException(status_code=500, detail="No default videos available")
            
            selected_video = random.choice(default_videos)
            logger.info(f"[JOB {job_id}] No video uploaded, using random default: {selected_video.name}")
            
            # Copy to upload dir for processing
            video_filename = f"{job_id}_{selected_video.name}"
            video_path = UPLOAD_DIR / video_filename
            shutil.copy(selected_video, video_path)
        
        # Parse script
        logger.info(f"[JOB {job_id}] Parsing dialogue script")
        dialogue, speakers = parse_dialogue_script(script)
        
        if not validate_two_speakers(speakers):
            raise HTTPException(status_code=400, detail=f"Script must have 1 or 2 speakers. Found: {len(speakers)}")
        
        logger.info(f"[JOB {job_id}] Speakers: {', '.join(speakers)}")
        logger.info(f"[JOB {job_id}] Dialogue segments: {len(dialogue)}")
        
        # Process uploaded images
        dialogue_images_map = {}
        if dialogue_images and image_indices:
            try:
                # Parse the image indices JSON
                indices_map = json.loads(image_indices)
                logger.info(f"[JOB {job_id}] Processing {len(dialogue_images)} uploaded images")
                
                # Create images directory
                images_dir = Path("/tmp/dialogue_images")
                images_dir.mkdir(exist_ok=True)
                
                # Save each image and map to dialogue index
                for img_file in dialogue_images:
                    # Find the index for this filename
                    dialogue_idx = None
                    for idx, filename in indices_map.items():
                        if filename == img_file.filename:
                            dialogue_idx = int(idx)
                            break
                    
                    if dialogue_idx is not None:
                        # Save image
                        image_filename = f"{job_id}_dialogue_{dialogue_idx}_{img_file.filename}"
                        image_path = images_dir / image_filename
                        
                        with image_path.open("wb") as buffer:
                            shutil.copyfileobj(img_file.file, buffer)
                        
                        dialogue_images_map[dialogue_idx] = str(image_path)
                        logger.info(f"[JOB {job_id}] Saved image for dialogue {dialogue_idx}: {image_path}")
                
                logger.info(f"[JOB {job_id}] ✓ Processed {len(dialogue_images_map)} dialogue images")
            except Exception as e:
                logger.error(f"[JOB {job_id}] Error processing images: {e}")
                # Continue without images
                dialogue_images_map = {}
        else:
            logger.info(f"[JOB {job_id}] No dialogue images provided")
        
        # Save speaker avatars if provided
        speaker_avatars = {}
        if speaker1_avatar:
            try:
                images_dir = Path("/tmp/dialogue_images")
                images_dir.mkdir(exist_ok=True)
                
                avatar1_path = images_dir / f"{job_id}_speaker1_{speaker1_avatar.filename}"
                with avatar1_path.open("wb") as buffer:
                    shutil.copyfileobj(speaker1_avatar.file, buffer)
                
                speaker_avatars[speakers[0]] = str(avatar1_path)
                logger.info(f"[JOB {job_id}] Saved avatar for {speakers[0]}: {avatar1_path}")
            except Exception as e:
                logger.error(f"[JOB {job_id}] Error saving speaker1 avatar: {e}")
        
        if speaker2_avatar:
            try:
                images_dir = Path("/tmp/dialogue_images")
                images_dir.mkdir(exist_ok=True)
                
                avatar2_path = images_dir / f"{job_id}_speaker2_{speaker2_avatar.filename}"
                with avatar2_path.open("wb") as buffer:
                    shutil.copyfileobj(speaker2_avatar.file, buffer)
                
                speaker_avatars[speakers[1]] = str(avatar2_path)
                logger.info(f"[JOB {job_id}] Saved avatar for speaker 2 ({speakers[1]}): {avatar2_path}")
            except Exception as e:
                logger.error(f"[JOB {job_id}] Error saving speaker 2 avatar: {e}")

        # Default avatars for Peter and Stewie if not provided
        for speaker in speakers:
            if speaker not in speaker_avatars:
                speaker_lower = speaker.lower()
                default_avatar_path = None
                
                if "peter" in speaker_lower:
                    default_avatar_path = "/Users/ayushganvir/Documents/code/content_gen/Peter_Griffin.png"
                elif "stewie" in speaker_lower:
                    default_avatar_path = "/Users/ayushganvir/Documents/code/content_gen/Stewie_Griffin.png"
                
                if default_avatar_path and os.path.exists(default_avatar_path):
                    speaker_avatars[speaker] = default_avatar_path
                    logger.info(f"[JOB {job_id}] Using default avatar for {speaker}: {default_avatar_path}")
        
        if speaker_avatars:
            logger.info(f"[JOB {job_id}] ✓ Processed {len(speaker_avatars)} speaker avatars")
        
        # Get ElevenLabs API key
        elevenlabs_api_key = os.getenv('ELEVENLABS_API_KEY')
        if not elevenlabs_api_key:
            raise HTTPException(status_code=500, detail="ELEVENLABS_API_KEY not set")
        
        # Map voices
        voice_mapping = {
            speakers[0]: speaker1_voice
        }
        if len(speakers) > 1:
            voice_mapping[speakers[1]] = speaker2_voice
        
        logger.info(f"[JOB {job_id}] Voice mapping: {voice_mapping}")
        
        # Check if we can reuse preview audio
        audio_result = None
        if preview_audio_path and os.path.exists(preview_audio_path) and preview_job_id:
            # Try to retrieve stored preview data
            preview_key = f"preview_{preview_job_id}"
            if preview_key in processing_status:
                logger.info(f"[JOB {job_id}] ♻️  Reusing preview audio AND segments data: {preview_audio_path}")
                preview_data = processing_status[preview_key]
                concatenated_audio = preview_data["audio_path"]
                audio_result = {
                    "segments": preview_data["segments"],
                    "count": len(preview_data["segments"])
                }
                logger.info(f"[JOB {job_id}] ✓ Retrieved {audio_result['count']} audio segments from preview")
            else:
                logger.warning(f"[JOB {job_id}] Preview data not found, will regenerate audio")
                concatenated_audio = None
                preview_audio_path = None
        
        if not preview_audio_path or not audio_result:
            # Generate audio segments with ElevenLabs
            logger.info(f"[JOB {job_id}] Generating audio with ElevenLabs (no preview available)")
            audio_result = generate_dialogue_audio(elevenlabs_api_key, dialogue, voice_mapping)
            
            if audio_result["count"] == 0:
                raise HTTPException(status_code=500, detail="Failed to generate audio")
            
            # Concatenate audio segments (with 1s gaps between speaker changes)
            final_audio_path = f"/tmp/elevenlabs_audio/final_{job_id}.mp3"
            
            concatenated_audio = concatenate_audio_segments(audio_result["segments"], final_audio_path)
            
            if not concatenated_audio:
                raise HTTPException(status_code=500, detail="Failed to concatenate audio")
            
            logger.info(f"[JOB {job_id}] ✓ Audio generated: {concatenated_audio}")
        
        # Get OpenAI API key for caption generation (using Whisper STT for accurate timing)
        openai_api_key = os.getenv('OPENAI_API_KEY')
        if not openai_api_key:
            raise HTTPException(status_code=500, detail="OPENAI_API_KEY not set (needed for Whisper captions)")
        
        logger.info(f"[JOB {job_id}] Starting video composition with Whisper captions")
        
        # Step 1: Generate captions using Whisper STT on the ElevenLabs audio
        logger.info(f"[JOB {job_id}] Generating captions via Whisper STT")
        from mediachain.examples.moviepy_engine.src.captions.caption_handler import CaptionHandler
        caption_handler = CaptionHandler()
        
        # Caption settings from form parameters
        logger.info(f"[JOB {job_id}] Caption colors: text={font_color}, shadow={shadow_color}")
        
        # Generate subtitles from the concatenated audio (Whisper automatically gets timing)
        # Using smaller font size (45 instead of 60) and Helvetica with yellow outline
        subtitles_path, caption_clips = await caption_handler.process(
            concatenated_audio,
            captions_color=font_color,
            shadow_color='yellow',  # Yellow outline (hardcoded in VideoCaptioner)
            font_size=45,  # Smaller font
            width=540
        )
        logger.info(f"[JOB {job_id}] ✓ Whisper generated {len(caption_clips)} caption clips with timestamps")
        
        # Step 2: Load and prepare the background video
        from moviepy.editor import VideoFileClip, AudioFileClip, CompositeVideoClip
        from mediachain.examples.moviepy_engine.src.video_editor import VideoEditor
        
        video_editor = VideoEditor()
        
        logger.info(f"[JOB {job_id}] Loading background video")
        background_video = VideoFileClip(str(video_path))
        background_duration = background_video.duration
        
        # Load the audio
        audio_clip = AudioFileClip(concatenated_audio)
        audio_duration = audio_clip.duration
        
        logger.info(f"[JOB {job_id}] Video: {background_duration:.2f}s, Audio: {audio_duration:.2f}s")
        
        # Step 3: Loop video if too short
        if background_duration < audio_duration:
            if loop_if_short:
                logger.info(f"[JOB {job_id}] Video too short, looping to {audio_duration:.2f}s")
                looped_video_path = video_editor.loop_video_to_duration(str(video_path), audio_duration + 5.0)
                if looped_video_path:
                    background_video.close()
                    background_video = VideoFileClip(looped_video_path)
                    background_duration = background_video.duration
                    logger.info(f"[JOB {job_id}] ✓ Video looped to {background_duration:.2f}s")
                else:
                    raise HTTPException(status_code=500, detail="Failed to loop video")
            else:
                raise HTTPException(status_code=400, detail=f"Video too short: {background_duration:.2f}s < {audio_duration:.2f}s")
        
        # Step 4: Crop video to 9:16 aspect ratio
        logger.info(f"[JOB {job_id}] Cropping to 9:16 aspect ratio")
        cropped_video = video_editor.crop_video_9_16(background_video)
        
        # Step 5: Set the audio
        logger.info(f"[JOB {job_id}] Syncing ElevenLabs audio with video")
        video_with_audio = cropped_video.set_audio(audio_clip)
        
        # Step 5.5: Add dialogue images if provided
        image_clips = []
        if dialogue_images_map:
            logger.info(f"[JOB {job_id}] Adding dialogue images to video")
            image_clips = add_dialogue_images_to_video(
                cropped_video,
                dialogue_images_map,
                audio_result["segments"]
            )
            logger.info(f"[JOB {job_id}] ✓ Added {len(image_clips)} image overlays")
        
        # Step 5.5: Add speaker avatars
        avatar_clips = []
        if speaker_avatars:
            logger.info(f"[JOB {job_id}] Adding speaker avatars")
            avatar_clips = add_speaker_avatars_to_video(
                cropped_video,
                speaker_avatars,
                audio_result["segments"],
                speakers
            )
            logger.info(f"[JOB {job_id}] ✓ Added {len(avatar_clips)} avatar overlays")
        
        # Step 6: Add Whisper-generated captions overlay
        logger.info(f"[JOB {job_id}] Adding Whisper-timed captions overlay")
        final_video = CompositeVideoClip([video_with_audio] + image_clips + avatar_clips + caption_clips)
        
        # Cut to audio duration
        final_video = final_video.subclip(0, audio_duration)
        
        # Step 7: Render final video
        output_filename = f"script_mode_{job_id}.mp4"
        output_path = os.path.join(OUTPUT_DIR, output_filename)
        
        logger.info(f"[JOB {job_id}] Rendering final video...")
        final_video.write_videofile(
            output_path,
            codec='libx264',
            audio_codec='aac',
            fps=30,
            preset='medium',
            threads=4
        )
        
        # Step 8: Cleanup
        logger.info(f"[JOB {job_id}] Cleaning up resources")
        background_video.close()
        audio_clip.close()
        cropped_video.close()
        video_with_audio.close()
        final_video.close()
        for clip in caption_clips:
            clip.close()
        
        # Remove uploaded video
        video_path.unlink(missing_ok=True)
        
        logger.info(f"[JOB {job_id}] ✓✓✓ Script mode video generation completed!")
        
        result = {
            "status": "success",
            "message": "Video generated successfully with ElevenLabs audio and Whisper captions!",
            "job_id": job_id,
            "download_url": f"/api/download/{output_filename}"
        }
        
        return JSONResponse(result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[JOB {job_id}] ✗✗✗ EXCEPTION ✗✗✗")
        logger.error(f"[JOB {job_id}] {str(e)}")
        logger.exception("Full traceback:")
        
        processing_status[job_id]["status"] = "failed"
        processing_status[job_id]["error"] = str(e)
        
        if video_path and video_path.exists():
            video_path.unlink(missing_ok=True)
        
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


# Instagram API Routes
class InstagramAuthRequest(BaseModel):
    username: str
    access_token: str
    account_id: str

class InstagramUploadRequest(BaseModel):
    account_id: str
    job_id: str
    caption: str
    cleanup: bool = False


@app.get("/instagram")
async def instagram_dashboard():
    """Serve the Instagram dashboard page"""
    return FileResponse("static/instagram.html")

@app.post("/api/instagram/auth")
async def link_instagram_account(data: InstagramAuthRequest):
    """Link an Instagram account"""
    try:
        instagram_manager.add_account(data.access_token, data.account_id, data.username)
        return JSONResponse({"status": "success"})
    except Exception as e:
        logger.error(f"[INSTAGRAM] Error linking account: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/instagram/accounts")
async def get_instagram_accounts():
    """Get linked Instagram accounts"""
    return JSONResponse(instagram_manager.get_accounts())

@app.delete("/api/instagram/accounts/{account_id}")
async def remove_instagram_account(account_id: str):
    """Remove an Instagram account"""
    if instagram_manager.remove_account(account_id):
        return JSONResponse({"status": "success"})
    raise HTTPException(status_code=404, detail="Account not found")

@app.post("/api/instagram/upload")
async def upload_to_instagram(data: InstagramUploadRequest):
    """Upload a generated video to Instagram"""
    try:
        # Find the video file
        # We need to find where the video is stored based on job_id
        # Assuming standard naming convention or checking output dirs
        video_filename = f"reddit_story_{data.job_id}.mp4" # Standard output name
        
        # Search for the file
        video_path = None
        possible_paths = [
            OUTPUT_DIR / video_filename,
            Path("outputs") / video_filename,
            Path(f"/tmp/final_video_{data.job_id}.mp4") # Sometimes stored here
        ]
        
        # Also check if we can find it via download logic
        for path in possible_paths:
            if path.exists():
                video_path = path
                break
        
        if not video_path:
             # Fallback: try to find any file with job_id in outputs
             for file in OUTPUT_DIR.glob(f"*{data.job_id}*.mp4"):
                 video_path = file
                 break

        if not video_path:
            raise HTTPException(status_code=404, detail="Video file not found for this job")

        # Upload
        # Construct public URL
        video_filename = video_path.name
        video_url = f"{PUBLIC_URL}/outputs/{video_filename}"
        
        logger.info(f"[INSTAGRAM] Uploading video from URL: {video_url}")
        
        result = instagram_manager.upload_video(data.account_id, video_url, data.caption)
        
        # Cleanup if requested
        if data.cleanup:
            logger.info(f"[CLEANUP] Cleaning up files for job {data.job_id}")
            # Delete video
            try:
                os.remove(video_path)
            except Exception as e:
                logger.warning(f"Failed to delete video: {e}")
            
            # Delete intermediate files
            # (This is a basic cleanup, could be more thorough)
            shutil.rmtree(f"/tmp/elevenlabs_audio", ignore_errors=True)
            
            # Remove from processing status
            if data.job_id in processing_status:
                del processing_status[data.job_id]

        return JSONResponse({"status": "success", "result": result})

    except Exception as e:
        logger.error(f"[INSTAGRAM] Error uploading: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/instagram/history")
async def get_upload_history():
    """Get upload history"""
    return JSONResponse(instagram_manager.get_history())


# ============================================================================
# EXTENSION API ENDPOINTS
# ============================================================================

class ExtensionSessionData(BaseModel):
    session_id: str
    dialogue: list
    speakers: list

class ExtensionImageUpload(BaseModel):
    session_id: str
    dialogue_index: int
    image_data: str  # base64 encoded

@app.post("/api/extension/create-session")
async def create_extension_session(data: ExtensionSessionData):
    """Create a new extension session with parsed dialogue"""
    try:
        extension_sessions[data.session_id] = {
            "dialogue": data.dialogue,
            "speakers": data.speakers,
            "images": {},
            "timestamp": datetime.now().isoformat()
        }
        logger.info(f"[EXTENSION] Created session {data.session_id} with {len(data.dialogue)} dialogues")
        return JSONResponse({"status": "success", "session_id": data.session_id})
    except Exception as e:
        logger.error(f"[EXTENSION] Error creating session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/extension/session/{session_id}")
async def get_extension_session(session_id: str):
    """Get extension session data"""
    if session_id not in extension_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return JSONResponse(extension_sessions[session_id])

@app.post("/api/extension/upload-image")
async def upload_extension_image(data: ExtensionImageUpload):
    """Upload image for a specific dialogue"""
    try:
        if data.session_id not in extension_sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Store base64 image data
        extension_sessions[data.session_id]["images"][str(data.dialogue_index)] = data.image_data
        
        logger.info(f"[EXTENSION] Uploaded image for dialogue {data.dialogue_index} in session {data.session_id}")
        
        return JSONResponse({
            "status": "success",
            "dialogue_index": data.dialogue_index,
            "total_images": len(extension_sessions[data.session_id]["images"])
        })
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[EXTENSION] Error uploading image: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/extension/image/{session_id}/{dialogue_index}")
async def delete_extension_image(session_id: str, dialogue_index: int):
    """Delete image for a specific dialogue"""
    try:
        if session_id not in extension_sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        images = extension_sessions[session_id]["images"]
        if str(dialogue_index) in images:
            del images[str(dialogue_index)]
            logger.info(f"[EXTENSION] Deleted image for dialogue {dialogue_index}")
        
        return JSONResponse({"status": "success"})
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[EXTENSION] Error deleting image: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/extension/images/{session_id}")
async def get_extension_images(session_id: str):
    """Get all images for a session"""
    if session_id not in extension_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return JSONResponse(extension_sessions[session_id].get("images", {}))


if __name__ == "__main__":
    import uvicorn
    
    # Create static directory if it doesn't exist
    Path("static").mkdir(exist_ok=True)
    
    print("=" * 60)
    print("🚀 Reddit Story Video Generator API")
    print("=" * 60)
    print(f"📱 Web Interface: http://localhost:8000")
    print(f"📚 API Docs: http://localhost:8000/docs")
    print(f"🏥 Health Check: http://localhost:8000/api/health")
    print("=" * 60)
    print("\nPress Ctrl+C to stop the server\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")



