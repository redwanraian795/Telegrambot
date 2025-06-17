import os
import yt_dlp
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def simple_download_test(url, quality='best'):
    """Simplified download function for testing"""
    downloads_dir = "downloads"
    os.makedirs(downloads_dir, exist_ok=True)
    
    # Clear existing files for clean test
    try:
        for file in os.listdir(downloads_dir):
            file_path = os.path.join(downloads_dir, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
    except:
        pass
    
    # Configure yt-dlp options
    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'outtmpl': os.path.join(downloads_dir, '%(title)s.%(ext)s'),
        'quiet': True,
        'no_warnings': True,
    }
    
    if quality == 'audio':
        ydl_opts.update({
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        })
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"Downloading from: {url}")
            ydl.download([url])
            
            # Find downloaded file
            files = [f for f in os.listdir(downloads_dir) if os.path.isfile(os.path.join(downloads_dir, f))]
            
            if files:
                downloaded_file = os.path.join(downloads_dir, files[0])
                file_size = os.path.getsize(downloaded_file)
                print(f"Success! Downloaded: {files[0]} ({file_size} bytes)")
                return downloaded_file
            else:
                print("Error: No files found after download")
                return None
                
    except Exception as e:
        print(f"Download failed: {str(e)}")
        return None

if __name__ == "__main__":
    # Test with a simple YouTube video
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Rick Roll for testing
    result = simple_download_test(test_url)
    print(f"Test result: {result}")