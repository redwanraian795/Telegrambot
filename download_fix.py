import os
import yt_dlp
import time
from pathlib import Path

def robust_download(url, quality='best', downloads_dir='downloads'):
    """Robust download function with reliable file detection"""
    
    # Ensure downloads directory exists
    os.makedirs(downloads_dir, exist_ok=True)
    
    # Clear old files to avoid confusion
    try:
        for file in os.listdir(downloads_dir):
            file_path = os.path.join(downloads_dir, file)
            if os.path.isfile(file_path):
                # Remove files older than 1 hour
                if time.time() - os.path.getmtime(file_path) > 3600:
                    os.remove(file_path)
    except:
        pass
    
    # Configure yt-dlp with simple, reliable options
    if quality == 'audio':
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(downloads_dir, '%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True,
        }
    else:
        ydl_opts = {
            'format': 'best[ext=mp4]/best',
            'outtmpl': os.path.join(downloads_dir, '%(title)s.%(ext)s'),
            'quiet': True,
        }
    
    # Record existing files
    files_before = set()
    try:
        files_before = set(os.listdir(downloads_dir))
    except:
        pass
    
    # Download
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        return None, f"Download failed: {str(e)}"
    
    # Find new files
    try:
        files_after = set(os.listdir(downloads_dir))
        new_files = files_after - files_before
        
        if new_files:
            # Return the first new file
            new_file = list(new_files)[0]
            filepath = os.path.join(downloads_dir, new_file)
            if os.path.exists(filepath):
                return filepath, None
        
        # Fallback: return most recent file if no new files detected
        if files_after:
            most_recent = max(files_after, 
                            key=lambda f: os.path.getmtime(os.path.join(downloads_dir, f)))
            filepath = os.path.join(downloads_dir, most_recent)
            # Only return if file is very recent (last 2 minutes)
            if time.time() - os.path.getmtime(filepath) < 120:
                return filepath, None
        
        return None, "No downloaded file found"
        
    except Exception as e:
        return None, f"Error finding file: {str(e)}"

# Test function
if __name__ == "__main__":
    test_url = "https://www.youtube.com/watch?v=jNQXAC9IVRw"
    filepath, error = robust_download(test_url)
    if filepath:
        print(f"Success: {filepath}")
        print(f"Size: {os.path.getsize(filepath)} bytes")
    else:
        print(f"Failed: {error}")