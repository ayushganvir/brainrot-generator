import yaml
import logging
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeVideoClip, TextClip
import random
from openai import OpenAI
import os
import re

# Update the config loading to use the correct path
current_dir = os.path.dirname(os.path.abspath(__file__))
# Accessing configuration values

""" TurboReel-Moviepy imports """
from ..src.video_editor import VideoEditor
from ..src.captions.caption_handler import CaptionHandler

""" MediaChain imports """

# MediaChain Script
from core.script.script_generation import generate_script
# MediaChain Audio
from core.audio.text_to_speech.tts_generation import generate_text_to_speech
from core.audio.speech_to_text.stt_generation import generate_speech_to_text
from core.image.utils.image_timestamps import generate_image_timestamps
# MediaChain Image
from core.image.generation.image_generation import generate_image

class RedditStoryGenerator:
    def __init__(self, openai_api_key: str):
        self.video_editor: VideoEditor = VideoEditor()
        self.caption_handler: CaptionHandler = CaptionHandler()
        self.openai_api_key = openai_api_key

    async def create_reddit_question_clip(self, reddit_question: str, video_height: int = 720) -> tuple[TextClip, str]:
        """Create a text clip for the Reddit question and generate its audio."""
        try:
            logging.info(f"[CREATE_QUESTION] Generating TTS audio for question")
            logging.info(f"[CREATE_QUESTION] Text: '{reddit_question[:50]}...'")
            
            # Generate audio for the Reddit question
            reddit_question_audio_path: str = generate_text_to_speech("openai", self.openai_api_key, reddit_question, voice="echo")
            
            if not reddit_question_audio_path:
                logging.error(f"[CREATE_QUESTION] ✗ Failed to generate TTS audio")
                return None, None
                
            logging.info(f"[CREATE_QUESTION] ✓ Audio generated: {reddit_question_audio_path}")
            
            # Getting audio duration for further processing
            reddit_question_audio_clip: AudioFileClip = AudioFileClip(reddit_question_audio_path)
            reddit_question_audio_duration: float = reddit_question_audio_clip.duration
            reddit_question_audio_clip.close()
            logging.info(f"[CREATE_QUESTION] Audio duration: {reddit_question_audio_duration:.2f}s")

            # Calculate text clip size based on video width
            text_width = int((video_height * 9 / 16) * 0.7)
            text_height = int(text_width * 0.35)
            fontsize = int(video_height * 0.03)
            
            logging.info(f"[CREATE_QUESTION] Creating text overlay: {text_width}x{text_height}px, font size {fontsize}px")

            # Create a text clip for the Reddit question
            reddit_question_text_clip = TextClip(
                reddit_question,
                fontsize=fontsize,
                color='black',
                bg_color='white',
                size=(text_width, text_height),
                method='caption',
                align='center'
            ).set_duration(reddit_question_audio_duration)
            
            logging.info(f"[CREATE_QUESTION] ✓ Question clip created successfully")

            return reddit_question_text_clip, reddit_question_audio_path
        except Exception as e:
            logging.error(f"[CREATE_QUESTION] ✗ Error creating Reddit question clip: {e}", exc_info=True)
            return None, None

    async def generate_video(self, video_path_or_url: str = '', 
                            video_path: str = '', 
                            video_url: str = '', 
                            video_topic: str = '',
                            captions_settings: dict = {},
                            add_images: bool = True,
                            loop_if_short: bool = True
                            ) -> dict:
        """Generate a video based on the provided topic or ready-made script.

        Args:
            video_path_or_url (str): 'video_path' or 'video_url', depending on which one is provided.
            video_path (str): The path of the video if provided.
            video_url (str): The URL of the video to download.
            video_topic (str): The topic of the video if script type is 'based_on_topic'.        
            captions_settings (dict): The settings for the captions. (font, color, etc)
            loop_if_short (bool): Automatically loop video if too short (default: True)

        Returns:
            dict: A dictionary with the status of the video generation and a message.
        """
        clips_to_close = []
        logging.info("="*80)
        logging.info("[GENERATE_VIDEO] Starting video generation process")
        logging.info("="*80)
        
        try:
            # Validation
            logging.info("[VALIDATE] Validating input parameters")
            if not video_path_or_url:
                raise ValueError("video_path_or_url cannot be empty.")

            if not video_path and not video_url:
                raise ValueError("Either video_path or video_url must be provided.")

            if not video_topic:
                raise ValueError("For 'based_on_topic', the video topic should not be null.")
            
            logging.info(f"[VALIDATE] ✓ Input parameters valid")
            logging.info(f"[VALIDATE]   - Mode: {video_path_or_url}")
            logging.info(f"[VALIDATE]   - Topic: {video_topic}")
            logging.info(f"[VALIDATE]   - Add images: {add_images}")
            logging.info(f"[VALIDATE]   - Loop if short: {loop_if_short}")
            
            """ Download or getting video """
            logging.info("[VIDEO_INPUT] Loading background video")
            video_path: str = video_path if video_path_or_url == 'video_path' else self.video_editor.download_video(video_url)
            if not video_path:
                logging.error("[VIDEO_INPUT] ✗ Failed to get video path")
                return {"status": "error", "message": "No video path provided."}
            
            logging.info(f"[VIDEO_INPUT] ✓ Video path: {video_path}")
            
            # Get video dimensions and duration
            logging.info("[VIDEO_INPUT] Reading video properties")
            with VideoFileClip(video_path) as video:
                video_width, video_height = video.w, video.h
                background_video_length = video.duration
            
            logging.info(f"[VIDEO_INPUT] ✓ Video properties:")
            logging.info(f"[VIDEO_INPUT]   - Resolution: {video_width}x{video_height}")
            logging.info(f"[VIDEO_INPUT]   - Duration: {background_video_length:.2f}s")

            """ Handle Script Generation and Process """
            # Generate the script or use the provided script
            logging.info("[SCRIPT] Generating story script using AI")
            script: dict = generate_script("openai", self.openai_api_key, video_topic, model="gpt-3.5-turbo-0125")
            
            if not script:
                logging.error("[SCRIPT] ✗ Failed to generate script")
                return {"status": "error", "message": "Failed to generate script."}
            
            logging.info(f"[SCRIPT] ✓ Script generated: {len(str(script))} characters")

            """ Define video length for each clip (question and story) """
            # Initialize Reddit clips
            logging.info("[QUESTION] Creating question clip with audio")
            reddit_question_text_clip, reddit_question_audio_path = await self.create_reddit_question_clip(video_topic, video_height)
            
            if not reddit_question_audio_path:
                logging.error("[QUESTION] ✗ Failed to create question clip")
                return {"status": "error", "message": "Failed to create question clip."}
            
            reddit_question_audio_clip: AudioFileClip = AudioFileClip(reddit_question_audio_path)
            reddit_question_audio_duration: float = reddit_question_audio_clip.duration
            clips_to_close.append(reddit_question_audio_clip)
            
            logging.info(f"[QUESTION] ✓ Question audio created: {reddit_question_audio_duration:.2f}s")
            
            # Initialize Background video
            logging.info("[VIDEO] Loading background video clip")
            background_video_clip: VideoFileClip = VideoFileClip(video_path)
            clips_to_close.append(background_video_clip)
            
            logging.info(f"[VIDEO] ✓ Background video loaded")
            
            ## Initialize Story Audio
            logging.info("[AUDIO] Generating story narration audio")
            story_audio_path: str = generate_text_to_speech("openai", self.openai_api_key, script, voice="echo")
            if not story_audio_path:
                logging.error("[AUDIO] ✗ Failed to generate audio")
                return {"status": "error", "message": "Failed to generate audio."}

            story_audio_clip: AudioFileClip = AudioFileClip(story_audio_path)
            clips_to_close.append(story_audio_clip)
            story_audio_length: float = story_audio_clip.duration
            
            logging.info(f"[AUDIO] ✓ Story audio generated: {story_audio_length:.2f}s")
        
            # Calculate total required duration
            total_audio_duration = reddit_question_audio_duration + story_audio_length
            logging.info(f"[TIMING] Calculating video timing")
            logging.info(f"[TIMING]   - Question duration: {reddit_question_audio_duration:.2f}s")
            logging.info(f"[TIMING]   - Story duration: {story_audio_length:.2f}s")
            logging.info(f"[TIMING]   - Total audio needed: {total_audio_duration:.2f}s")
            logging.info(f"[TIMING]   - Background available: {background_video_length:.2f}s")
            
            # Check if background video is long enough, loop if needed
            if background_video_length < total_audio_duration:
                if loop_if_short:
                    logging.warning(f"[TIMING] ⚠️ Background video too short ({background_video_length:.2f}s < {total_audio_duration:.2f}s)")
                    logging.info(f"[TIMING] 🔄 Auto-looping video to meet duration requirement")
                    
                    # Loop the video to required duration (add 5 seconds buffer)
                    target_duration = total_audio_duration + 5.0
                    looped_video_path = self.video_editor.loop_video_to_duration(video_path, target_duration)
                    
                    if not looped_video_path:
                        error_msg = "Failed to loop video to required duration"
                        logging.error(f"[TIMING] ✗ {error_msg}")
                        return {"status": "error", "message": error_msg}
                    
                    # Update video_path to use looped version
                    video_path = looped_video_path
                    background_video_length = target_duration
                    
                    # Close and reopen the background video clip with looped version
                    background_video_clip.close()
                    clips_to_close.remove(background_video_clip)
                    
                    background_video_clip = VideoFileClip(video_path)
                    clips_to_close.append(background_video_clip)
                    
                    logging.info(f"[TIMING] ✓ Video looped successfully, new duration: {background_video_length:.2f}s")
                else:
                    error_msg = (
                        f"Background video too short! "
                        f"Required: {total_audio_duration:.2f}s, "
                        f"Available: {background_video_length:.2f}s. "
                        f"Please upload a video at least {total_audio_duration:.0f} seconds long."
                    )
                    logging.error(f"[TIMING] ✗ {error_msg}")
                    return {"status": "error", "message": error_msg}
            
            # Calculate video times to cut clips
            max_start_time: float = background_video_length - total_audio_duration
            
            if max_start_time < 0:
                # This should never happen due to check above, but just in case
                logging.warning(f"[TIMING] max_start_time is negative ({max_start_time:.2f}s), using 0")
                start_time = 0.0
            else:
                start_time: float = random.uniform(0, max_start_time)
            
            end_time: float = start_time + total_audio_duration
            
            logging.info(f"[TIMING] ✓ Cut times calculated:")
            logging.info(f"[TIMING]   - Start: {start_time:.2f}s")
            logging.info(f"[TIMING]   - End: {end_time:.2f}s")
            logging.info(f"[TIMING]   - Cut duration: {end_time - start_time:.2f}s")
            
            """ Cut video once """
            logging.info(f"[CUT] Cutting background video")
            cut_video_path: str = self.video_editor.cut_video(video_path, start_time, end_time)
            
            if not cut_video_path:
                logging.error("[CUT] ✗ Failed to cut video - returned None")
                return {"status": "error", "message": "Failed to cut video. Check if the file is corrupted or the format is supported."}
            
            if not os.path.exists(cut_video_path):
                logging.error(f"[CUT] ✗ Cut video path does not exist: {cut_video_path}")
                return {"status": "error", "message": "Cut video file was not created."}
            
            logging.info(f"[CUT] ✓ Video cut successfully: {cut_video_path}")
            
            cut_video_clip = VideoFileClip(cut_video_path)
            clips_to_close.append(cut_video_clip)
            logging.info(f"[CUT] ✓ Cut video clip loaded, duration: {cut_video_clip.duration:.2f}s")

            """ Handle reddit question video """
            logging.info("[QUESTION_VIDEO] Composing question video segment")
            reddit_question_video = cut_video_clip.subclip(0, reddit_question_audio_duration)
            reddit_question_video = reddit_question_video.set_audio(reddit_question_audio_clip)
            logging.info(f"[QUESTION_VIDEO] Cropping to 9:16 aspect ratio")
            reddit_question_video = self.video_editor.crop_video_9_16(reddit_question_video)

            # Add the text clip to the video
            logging.info(f"[QUESTION_VIDEO] Adding text overlay to question video")
            reddit_question_video = CompositeVideoClip([
                reddit_question_video,
                reddit_question_text_clip.set_position(('center', 'center'))
            ])
            logging.info(f"[QUESTION_VIDEO] ✓ Question video segment complete: {reddit_question_video.duration:.2f}s")

            """ Handle story video """
            logging.info("[STORY_VIDEO] Composing story video segment")
            logging.info(f"[STORY_VIDEO] Extracting story segment from {reddit_question_audio_duration:.2f}s onwards")
            story_video = cut_video_clip.subclip(reddit_question_audio_duration)
            story_video = story_video.set_audio(story_audio_clip)
            logging.info(f"[STORY_VIDEO] Cropping to 9:16 aspect ratio")
            story_video = self.video_editor.crop_video_9_16(story_video)
            logging.info(f"[STORY_VIDEO] ✓ Story video base prepared: {story_video.duration:.2f}s")

            font_size = video_width * 0.025
            logging.info(f"[CAPTIONS] Caption font size calculated: {font_size:.1f}px")

            # Generate subtitles
            logging.info(f"[CAPTIONS] Generating word-by-word captions")
            logging.info(f"[CAPTIONS] Caption settings: color={captions_settings.get('color', 'white')}, shadow={captions_settings.get('shadow_color', 'black')}")
            story_subtitles_path, story_subtitles_clips = await self.caption_handler.process(
                story_audio_path,
                captions_settings.get('color', 'white'),
                captions_settings.get('shadow_color', 'black'),
                captions_settings.get('font_size', font_size),
                captions_settings.get('font', 'LEMONMILK-Bold.otf')
            )
            logging.info(f"[CAPTIONS] ✓ Captions generated: {len(story_subtitles_clips)} caption clips")

            # Generate images if enabled
            if add_images:
                logging.info(f"[IMAGES] Analyzing script for image placement")
                image_timestamps = generate_image_timestamps("openai", self.openai_api_key, script, model="gpt-3.5-turbo-0125")
                logging.info(f"[IMAGES] ✓ Image timestamps generated: {len(image_timestamps)} images planned")
                
                logging.info(f"[IMAGES] Generating and adding AI images to video")
                story_video = await self.video_editor.add_images_to_video(story_video, image_timestamps)
                logging.info(f"[IMAGES] ✓ Images added to story video")
            else:
                logging.info(f"[IMAGES] Skipping image generation (disabled)")
            
            logging.info(f"[COMPOSITION] Adding captions overlay to story video")
            story_video = self.video_editor.add_captions_to_video(story_video, story_subtitles_clips)
            logging.info(f"[COMPOSITION] ✓ Captions overlaid on story video")
            
            # Combine clips
            logging.info(f"[COMPOSITION] Combining question and story segments")
            logging.info(f"[COMPOSITION]   - Question segment: 0s to {reddit_question_audio_duration:.2f}s")
            logging.info(f"[COMPOSITION]   - Story segment: {reddit_question_audio_duration:.2f}s to end")
            combined_clips = CompositeVideoClip([
                reddit_question_video,
                story_video.set_start(reddit_question_audio_duration)
            ])
            logging.info(f"[COMPOSITION] ✓ Final composition ready: {combined_clips.duration:.2f}s total")

            logging.info(f"[RENDER] Starting final video render (this may take several minutes)")
            final_video_output_path = self.video_editor.render_final_video(combined_clips)
            logging.info(f"[RENDER] ✓ Video rendered successfully")
            
            # Cleanup: Ensure temporary files are removed
            logging.info(f"[CLEANUP] Removing temporary files")
            self.video_editor.cleanup_files([story_audio_path, cut_video_path, story_subtitles_path, reddit_question_audio_path])
            logging.info(f"[CLEANUP] ✓ Temporary files cleaned up")
            
            logging.info("="*80)
            logging.info(f"[SUCCESS] ✓✓✓ VIDEO GENERATION COMPLETE ✓✓✓")
            logging.info(f"[SUCCESS] Output: {final_video_output_path}")
            logging.info("="*80)
            
            return {"status": "success", "message": "Video generated successfully.", "output_path": final_video_output_path}
        
        except Exception as e:
            logging.error("="*80)
            logging.error(f"[ERROR] ✗✗✗ VIDEO GENERATION FAILED ✗✗✗")
            logging.error(f"[ERROR] Exception: {str(e)}")
            logging.error("="*80)
            logging.exception("Full traceback:")
            return {"status": "error", "message": f"Error in video generation: {str(e)}"}
        finally:
            # Close all clips
            logging.info("[CLEANUP] Closing video/audio clips")
            for clip in clips_to_close:
                try:
                    clip.close()
                except Exception as e:
                    logging.warning(f"[CLEANUP] Could not close clip: {e}")
