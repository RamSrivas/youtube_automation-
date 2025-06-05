import requests
import json
from moviepy.editor import *
import textwrap
import os
import random
import yt_dlp
from gtts import gTTS
import pygame
import numpy as np
import os 
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")


try:
    from PIL import Image, ImageDraw, ImageFont
    # Handle ANTIALIAS deprecation
    if hasattr(Image, 'ANTIALIAS'):
        ANTIALIAS = Image.ANTIALIAS
    else:
        ANTIALIAS = Image.LANCZOS
except ImportError:
    Image = None
    ImageDraw = None
    ImageFont = None
    ANTIALIAS = None

class BrainRotVideoGenerator:
    def _init_(self, groq_api_key):
        self.groq_api_key = groq_api_key
        self.groq_url = "https://api.groq.com/openai/v1/chat/completions"
        self.background_videos_dir = "background_videos"
        self.audio_effects_dir = "audio_effects"
        self.output_dir = "output_videos"
        
        # Create directories
        os.makedirs(self.background_videos_dir, exist_ok=True)
        os.makedirs(self.audio_effects_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
        
    def generate_brainrot_content(self):
        """Generate brain rot content using Groq API"""
        prompts = [
            "Write a shocking 'fun fact' about ancient civilizations that sounds crazy but educational. Keep it under 50 words.",
            "Create a mind-blowing conspiracy theory about everyday objects that's obviously fake but entertaining. Under 50 words.",
            "Write a 'sigma grindset' motivational quote that's so over the top it's funny. Under 30 words.",
            "Create a fake 'leaked' conversation between two historical figures about modern technology. Under 60 words.",
            "Write a 'life hack' that's completely absurd but sounds convincing. Under 40 words."
        ]
        
        headers = {
            "Authorization": f"Bearer {self.groq_api_key}",
            "Content-Type": "application/json"
        }
        
        prompt = random.choice(prompts)
        
        data = {
            "model": "llama3-8b-8192",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 100
        }
        
        try:
            response = requests.post(self.groq_url, headers=headers, json=data)
            response.raise_for_status()
            content = response.json()['choices'][0]['message']['content']
            return content.strip()
        except Exception as e:
            print(f"Error generating content: {e}")
            return "Default brain rot content here"
    
    def create_text_clip(self, text, duration=5):
        """Create a text clip with brain rot styling"""
        # Wrap text for better display
        wrapped_text = textwrap.fill(text, width=20)
        
        # Create main text clip - fixed parameter issue
        main_text = TextClip(
            wrapped_text,
            fontsize=50,
            color='white',
            font='Arial-Bold'
        ).set_duration(duration).set_position('center')
                
        # Add shadow effect
        shadow_text = TextClip(
            wrapped_text,
            fontsize=50,
            color='black',
            font='Arial-Bold'
        ).set_duration(duration).set_position(('center', 'center')).set_opacity(0.3)
        
        # Add some brain rot effects - flashing text
        def blink_effect(get_frame, t):
            frame = get_frame(t)
            if int(t * 8) % 2:  # Blink every 1/8 second
                return frame
            else:
                return frame * 0.7  # Dim the text
        
        main_text = main_text.fl(blink_effect)
        
        return CompositeVideoClip([shadow_text, main_text])
    
    def add_brain_rot_effects(self, video_clip):
        """Add visual brain rot effects"""
        # Add random zoom ins
        def zoom_effect(get_frame, t):
            frame = get_frame(t)
            zoom_factor = 1 + 0.1 * np.sin(t * 4)  # Pulsing zoom
            return frame
        
        video_clip = video_clip.fl(zoom_effect)
        
        # Add screen shake effect
        def shake_effect(get_frame, t):
            frame = get_frame(t)
            if random.random() < 0.1:  # 10% chance per frame
                # Add slight shake
                shake_x = random.randint(-5, 5)
                shake_y = random.randint(-5, 5)
                # You'd implement actual shake here
            return frame
        
        return video_clip
    
    def download_gameplay_footage(self):
        """Download gameplay footage from YouTube"""
        gameplay_urls = [
            "https://www.youtube.com/watch?v=VIDEO_ID_HERE",  # Replace with actual Subway Surfers gameplay
            # Add more URLs here
        ]
        
        ydl_opts = {
            'format': 'best[height<=720]',
            'outtmpl': f'{self.background_videos_dir}/%(title)s.%(ext)s',
            'noplaylist': True,
        }
        
        print("Downloading gameplay footage...")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            for url in gameplay_urls:
                try:
                    ydl.download([url])
                    print(f"Downloaded: {url}")
                except Exception as e:
                    print(f"Error downloading {url}: {e}")
    
    def get_random_background_video(self):
        """Get a random background video from downloaded footage"""
        video_files = [f for f in os.listdir(self.background_videos_dir) if f.endswith(('.mp4', '.webm', '.mkv'))]
        
        if not video_files:
            print("No background videos found. Creating default background...")
            return self.create_default_background()
        
        random_video = random.choice(video_files)
        video_path = os.path.join(self.background_videos_dir, random_video)
        
        # Load and crop video to vertical format
        bg_video = VideoFileClip(video_path)
        
        # Crop to vertical (9:16 aspect ratio)
        w, h = bg_video.size
        target_w = int(h * 9/16)
        
        if target_w <= w:
            # Crop horizontally
            x_center = w // 2
            x1 = x_center - target_w // 2
            bg_video = bg_video.crop(x1=x1, x2=x1+target_w)
        else:
            # Add black bars if needed
            bg_video = bg_video.resize((target_w, h))
        
        # Resize to standard vertical resolution
        bg_video = bg_video.resize((1080, 1920))
        
        return bg_video
    
    def create_default_background(self):
        """Create a default animated background if no gameplay footage"""
        def make_frame(t):
            # Create a moving gradient background
            colors = [
                [255, 0, 128],  # Pink
                [0, 255, 255],  # Cyan
                [255, 255, 0],  # Yellow
            ]
            
            # Create animated gradient
            frame = np.zeros((1920, 1080, 3), dtype=np.uint8)
            
            # Create a simple animated pattern
            for y in range(1920):
                for x in range(1080):
                    # Create animated rainbow effect
                    color_phase = (x + y + t * 50) % 360
                    r = int(128 + 127 * np.sin(np.radians(color_phase)))
                    g = int(128 + 127 * np.sin(np.radians(color_phase + 120)))
                    b = int(128 + 127 * np.sin(np.radians(color_phase + 240)))
                    frame[y, x] = [r, g, b]
            
            return frame
        
        return VideoClip(make_frame, duration=60).resize((1080, 1920))
    
    def generate_high_quality_audio(self, text):
        """Generate high-quality audio from text using gTTS"""
        tts = gTTS(text=text, lang='en', slow=False)
        audio_path = f"{self.audio_effects_dir}/narration.mp3"
        tts.save(audio_path)
        
        # Load and enhance audio
        audio_clip = AudioFileClip(audio_path)
        
        # Add some audio effects for brain rot style
        try:
            audio_clip = audio_clip.fx(speedx, 1.1)  # Slightly faster
        except:
            pass  # Skip if speedx doesn't work
        
        return audio_clip
    
    def add_brain_rot_audio_effects(self, base_audio):
        """Add brain rot style audio effects"""
        # You can add sound effects here
        effect_files = [
            "vine_boom.mp3",
            "fart_sound.mp3",
            "airhorn.mp3",
            "bruh_sound.mp3"
        ]
        
        # Random chance to add sound effects
        if random.random() < 0.7:  # 70% chance
            effect_times = [random.uniform(0, base_audio.duration-1) for _ in range(2)]
            
            for effect_time in effect_times:
                effect_file = random.choice(effect_files)
                effect_path = os.path.join(self.audio_effects_dir, effect_file)
                
                if os.path.exists(effect_path):
                    effect_audio = AudioFileClip(effect_path).set_start(effect_time)
                    base_audio = CompositeAudioClip([base_audio, effect_audio])
        
        return base_audio
    
    def add_sound_effects(self, video_clip):
        """Add basic sound effects (you'd want to add actual audio files)"""
        # For now, just return the video. You can add AudioFileClip here
        # audio = AudioFileClip("path_to_audio.mp3").set_duration(video_clip.duration)
        # return video_clip.set_audio(audio)
        return video_clip
    
    def create_video(self, output_filename="brainrot_video.mp4"):
        """Main function to create the brain rot video"""
        print("Generating brain rot content...")
        content = self.generate_brainrot_content()
        print(f"Generated content: {content}")
        
        # Create background
        background = self.get_random_background_video()
        
        # Ensure background has the right duration
        background = background.subclip(0, min(15, background.duration))
        
        # Create text overlay
        text_clip = self.create_text_clip(content, duration=15)
        
        # Combine background and text
        final_video = CompositeVideoClip([background, text_clip])
        
        # Add sound effects
        final_video = self.add_sound_effects(final_video)
        
        # Set duration
        final_video = final_video.set_duration(15)
        
        print("Rendering video...")
        output_path = os.path.join(self.output_dir, output_filename)
        final_video.write_videofile(
            output_path,
            fps=24,
            audio_codec='aac' if final_video.audio else None,
            verbose=False,
            logger=None
        )
        
        print(f"Video created: {output_path}")
        return output_path

# Usage example
if __name__ == "_main_":
    # Initialize the generator
    GROQ_API_KEY = "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"  # Get from https://console.groq.com/
    
    generator = BrainRotVideoGenerator(GROQ_API_KEY)
    
    # Generate multiple videos
    for i in range(3):
        try:
            video_file = generator.create_video(f"brainrot_video_{i+1}.mp4")
            print(f"Created: {video_file}")
        except Exception as e:
            print(f"Error creating video {i+1}: {e}")

# Additional automation script for posting (basic structure)
class SocialMediaPoster:
    def _init_(self):
        pass
    
    def upload_to_youtube_shorts(self, video_path, title, description):
        """Upload to YouTube Shorts using YouTube API"""
        # You'll need to implement YouTube API integration
        # This requires OAuth setup and youtube-data-api
        print(f"Would upload {video_path} to YouTube with title: {title}")
    
    def upload_to_instagram_reels(self, video_path, caption):
        """Upload to Instagram Reels"""
        # You'll need Instagram Graph API or third-party services
        print(f"Would upload {video_path} to Instagram with caption: {caption}")
