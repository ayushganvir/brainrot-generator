# Reddit Post - BrainRot Generator

## 📋 Copy-Paste Ready Posts

### Version 1: Full Post (r/SideProject, r/Python, r/webdev)

**Title:**
```
🎬 I built an AI tool that turns dialogue scripts into viral videos + a Chrome extension that lets you grab images from ANY website
```

**Body:**
```markdown
Hey everyone! 👋

I just finished a project I'm pretty excited about - **BrainRot Generator**. It's a complete pipeline for creating those viral dialogue videos (think Peter & Stewie format).

## What makes it different?

Most video generators require you to manually download images, save them, upload them... it's tedious. So I built a **Chrome extension** that lets you:

1. Parse your dialogue script in the web app
2. Open the extension side panel
3. Browse to ANY website (Google Images, Reddit, Twitter, whatever)
4. **Drag a box** over the area you want to capture
5. Image is automatically grabbed and synced to your video

No downloads, no right-clicking, no manual uploads. Just drag and done.

## The full feature set:

🎙️ **AI Voices** - ElevenLabs integration for natural-sounding dialogue  
🖼️ **Smart Image Capture** - Chrome extension with drag-to-select from any webpage  
🎥 **Auto Video Generation** - Combines voices, images, captions, and background  
📱 **Instagram Upload** - Direct upload to Reels/Feed  
⚡ **Real-time Sync** - Extension and web app update instantly  

## Technical highlights:

The Chrome extension was the trickiest part:
- Had to handle device pixel ratios (1x, 2x, 3x displays)
- Viewport coordinate scaling for accurate captures
- Transparent selection box (no blue tint in screenshots)
- Real-time bidirectional sync between extension and Flask backend
- Works on all websites (respects CORS)

Backend is FastAPI + MoviePy for video processing, ElevenLabs for voices, and Instagram Graph API for uploads.

## Try it out:

**GitHub**: https://github.com/ayushganvir/brainrot-generator

The README has full setup instructions. You'll need:
- Python 3.8+
- ElevenLabs API key (for voices)
- Chrome browser (for the extension)

## Demo workflow:

```
1. Write script: "Peter: This is cool! Stewie: Indeed."
2. Parse → Assign voices → Preview audio
3. Open extension → Browse web → Drag to select images
4. Generate video → Download or upload to Instagram
```

Would love feedback from the community! What features would you add? Any bugs you find?

---

**Tech Stack**: FastAPI, Python, MoviePy, ElevenLabs, Chrome Extension Manifest V3, Instagram Graph API

**License**: MIT (free to use/modify)
```

---

### Version 2: Short Post (r/InternetIsBeautiful, r/chrome_extensions)

**Title:**
```
Chrome extension that lets you drag-to-select and capture images from any website (for AI video generation)
```

**Body:**
```markdown
Built a Chrome extension as part of a larger project (AI dialogue video generator).

**What it does:**
- Drag a box over any area on ANY webpage
- Captures that exact region as an image
- Auto-syncs to a web app for video generation
- Works on all screen DPIs (handles retina displays correctly)

**Use case:**
Creating dialogue videos with images from the web. Instead of downloading images manually, you just drag-select them directly from Google Images, Reddit, Twitter, etc.

**Technical bits:**
- Transparent selection box (no blue tint in captures)
- Viewport-aware coordinate scaling
- Real-time sync via polling
- Side panel UI (stays visible while browsing)

**GitHub**: https://github.com/ayushganvir/brainrot-generator

The extension is in the `chrome-extension` folder. Full project includes AI voices, video generation, and Instagram upload.

Feedback welcome!
```

---

### Version 3: Ultra-Short (r/coolgithubprojects)

**Title:**
```
BrainRot Generator - Turn dialogue scripts into viral videos with AI voices and web-scraped images
```

**Body:**
```markdown
**Features:**
- 🎙️ AI voice generation (ElevenLabs)
- 🖼️ Chrome extension for drag-to-select image capture from any website
- 🎥 Automated video creation with captions
- 📱 Direct Instagram upload

**Tech**: Python, FastAPI, MoviePy, Chrome Extension API

**GitHub**: https://github.com/ayushganvir/brainrot-generator

**Coolest part**: The Chrome extension lets you grab images by dragging a box over them on any webpage - no manual downloads needed!
```

---

## 🎯 Posting Strategy

### Best Subreddits (in order of priority):

1. **r/SideProject** (Use Version 1)
   - Best for full project showcases
   - Engaged community
   - Post on weekdays 9-11 AM EST

2. **r/Python** (Use Version 1, emphasize Python/FastAPI)
   - Focus on technical implementation
   - Mention MoviePy, async processing
   - Include code snippets if asked

3. **r/webdev** (Use Version 1, emphasize full-stack)
   - Highlight FastAPI + vanilla JS
   - Mention real-time sync architecture
   - Show Chrome extension integration

4. **r/chrome_extensions** (Use Version 2)
   - Focus entirely on the extension
   - Deep dive into technical challenges
   - Share extension code snippets

5. **r/InternetIsBeautiful** (Use Version 2)
   - Must have live demo/video
   - Focus on user experience
   - Keep it simple and visual

6. **r/coolgithubprojects** (Use Version 3)
   - Short and sweet
   - Link-focused
   - Post multiple times (weekly)

### Timing:
- **Best days**: Tuesday, Wednesday, Thursday
- **Best times**: 9-11 AM EST, 2-4 PM EST
- **Avoid**: Weekends, late nights, Mondays

### Engagement Tips:
1. **Respond quickly** to all comments (first hour is crucial)
2. **Be helpful** - answer technical questions thoroughly
3. **Share insights** - what you learned, challenges faced
4. **Add value** - offer to help others build similar things
5. **Stay humble** - "Would love feedback" not "Check out my amazing project"

### What to prepare:
- [ ] Demo GIF/video (30 seconds max)
- [ ] Screenshots of UI
- [ ] Example output video
- [ ] Quick setup guide
- [ ] Troubleshooting FAQ

---

## 📸 Visual Assets Needed

### For Maximum Engagement:

1. **Demo GIF** (required for r/InternetIsBeautiful)
   - Show extension in action
   - Drag-to-select an image
   - Show it appearing in web app
   - 10-30 seconds, <5MB

2. **Screenshots**:
   - Main web interface
   - Extension side panel
   - Generated video example
   - Before/after comparison

3. **Example Video**:
   - Upload to YouTube/Streamable
   - Show full workflow
   - 1-2 minutes max

### Tools to create them:
- **GIFs**: ScreenToGif, LICEcap, Kap
- **Screen recording**: OBS, QuickTime, Loom
- **Editing**: Kapwing, Canva

---

## 🚀 Post-Launch Checklist

### Before posting:
- [ ] Test the setup process from scratch
- [ ] Update README with clear instructions
- [ ] Add LICENSE file (MIT)
- [ ] Create .env.example file
- [ ] Test Chrome extension on fresh install
- [ ] Prepare demo assets
- [ ] Write FAQ based on expected questions

### After posting:
- [ ] Monitor comments every 30 minutes (first 3 hours)
- [ ] Respond to all questions within 1 hour
- [ ] Fix any bugs reported immediately
- [ ] Update README based on feedback
- [ ] Thank people for stars/feedback
- [ ] Cross-post to other subreddits (wait 24 hours between)

### If it goes viral:
- [ ] Add "Featured on Reddit" badge to README
- [ ] Create CONTRIBUTING.md
- [ ] Set up GitHub Discussions
- [ ] Consider adding analytics (optional)
- [ ] Plan next features based on feedback

---

## 💬 Common Questions (Prepare Answers)

**Q: Can I use this commercially?**
A: Yes! MIT license means you can use it for anything.

**Q: Do I need to pay for APIs?**
A: ElevenLabs has a free tier (10k characters/month). OpenAI is optional.

**Q: Does the extension work on all websites?**
A: Yes, but some sites block screenshots (banking, DRM content). Works on 99% of sites.

**Q: Can I add my own voices?**
A: Yes! Just add your ElevenLabs voice ID to the config.

**Q: Why not use TikTok/YouTube instead of Instagram?**
A: Instagram Graph API is easier to work with. TikTok/YouTube coming soon!

**Q: Is this legal?**
A: For personal use, yes. For commercial use, respect copyright of images you capture.

---

## 🎁 Bonus: Product Hunt Launch

If Reddit goes well, consider Product Hunt:

**Tagline**: "Turn dialogue scripts into viral videos with AI voices and web-scraped images"

**Description**: 
```
BrainRot Generator is a complete pipeline for creating viral dialogue videos. 

The game-changer is the Chrome extension - instead of manually downloading images, you can drag-to-select them from any website and they automatically sync to your video.

Perfect for content creators, marketers, and anyone who wants to create engaging short-form content without the tedious manual work.
```

**Maker Comment**:
```
Hey Product Hunt! 👋

I built this because I was tired of the manual process of creating dialogue videos. The Chrome extension was born out of frustration with downloading images one by one.

Would love your feedback! What features should I add next?
```

---

**Good luck with your launch! 🚀**


## Full Post

Hey Reddit! 👋

I just finished building **BrainRot Generator** - a complete pipeline for creating those viral dialogue videos you see everywhere.

### What it does:
- 🎙️ **AI Voice Generation**: Paste any dialogue script, assign ElevenLabs voices to speakers
- 🖼️ **Chrome Extension**: Drag-to-select images from ANY webpage (no manual downloads!)
- 🎥 **Auto Video Creation**: Combines voices, images, background video, and animated captions
- 📱 **Instagram Upload**: Direct upload to your Instagram account

### The Chrome Extension is the coolest part:
Instead of manually downloading images, you can:
1. Parse your script in the web app
2. Open the extension side panel
3. Browse to any website
4. Drag to select screen areas for each dialogue line
5. Images sync in real-time back to the app!

It handles device pixel ratios, viewport scaling, and works on all websites. The selection box is transparent so you get clean captures.

### Tech Stack:
- FastAPI + Python backend
- ElevenLabs for AI voices
- MoviePy for video processing
- Chrome Extension (Manifest V3) with side panel UI
- Instagram Graph API integration

### Try it out:
**GitHub**: [Your Repo URL Here]

Would love feedback from the community! What features would you add?

---

## Short Version (for subreddits with character limits)

Built an AI video generator that turns dialogue scripts into viral videos! 

Features:
✅ AI voices (ElevenLabs)
✅ Chrome extension for drag-to-select image capture from any website
✅ Auto-generates videos with captions
✅ Direct Instagram upload

Tech: FastAPI, MoviePy, Chrome Extension API, Instagram Graph API

GitHub: [Your Repo URL]

---

## Suggested Subreddits to Post:
- r/SideProject
- r/webdev
- r/Python
- r/chrome_extensions
- r/InternetIsBeautiful
- r/programming
- r/learnprogramming
- r/coolgithubprojects
- r/opensource
- r/dataisbeautiful (if you make a demo video)

## Tips for Posting:
1. Add a demo video/GIF showing the extension in action
2. Include screenshots of the UI
3. Be ready to answer technical questions
4. Post during peak hours (9-11 AM EST)
5. Engage with comments quickly
6. Consider posting to Product Hunt as well!
