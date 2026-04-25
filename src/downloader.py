import os
import subprocess
import shlex
import sys
from typing import List
from urllib.parse import urlparse
from src.config_manager import ConfigManager

# CONFIGURATION
DOWNLOAD_DIR = "downloads"
TEMP_DIR = "temp"
COOKIES_DIR = "cookies"
DEFAULT_COOKIE = os.path.join(COOKIES_DIR, "bangi.txt") 

# SMART FORMAT STRATEGY
SMART_FORMAT = "best[height=240]/best[height=360]/best[height=480]/best[height=540]/bestaudio/best"

# CONCURRENCY SETTING
CONCURRENCY = "-N 16"

# Ensure we use the VENV yt-dlp
YT_DLP_BASE = f'"{sys.executable}" -m yt_dlp'

# EJS Configuration for YouTube
EJS_ARGS = '--js-runtime node'

# Ensure directories exist
os.makedirs(DOWNLOAD_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(COOKIES_DIR, exist_ok=True)

def get_cookie_path(client_id="default"):
    specific = os.path.join(COOKIES_DIR, f"{client_id}.txt")
    if os.path.exists(specific):
        return specific
    if os.path.exists(DEFAULT_COOKIE):
        return DEFAULT_COOKIE
    return None

def run_command(cmd_args: List[str]):
    print(f"Executing: {' '.join(shlex.quote(arg) for arg in cmd_args)}")
    process = subprocess.run(cmd_args, capture_output=True, text=True)
    if process.returncode != 0:
        print(f"❌ Error: {process.stderr}")
        raise Exception(process.stderr)
    return process.stdout.strip()

def get_expected_audio_path(job):
    name = job['name']
    safe_name = name.replace(" ", "_").replace("/", "-")
    return os.path.join(DOWNLOAD_DIR, f"{safe_name}.mp3")

def download_audio(job):
    url = job['url']
    name = job['name']
    
    config = ConfigManager()
    ua = config.get("user_agent")
    
    # Clean filename
    safe_name = name.replace(" ", "_").replace("/", "-")
    filename_tmpl = f"{safe_name}.%(ext)s"
    
    cookie_file = get_cookie_path()

    print(f"\n⬇️  Starting Download: {name}")
    
    # Base command as a list
    # Use sys.executable -m yt_dlp to ensure we use the venv's version
    base_cmd = [sys.executable, "-m", "yt_dlp"]
    
    common_args = [
        "--js-runtime", "node",
        "--no-cache-dir",
        "--no-mtime",
        "--no-playlist",
        "--paths", f"home:{DOWNLOAD_DIR}",
        "--paths", f"temp:{TEMP_DIR}",
        "-f", SMART_FORMAT,
        "-o", filename_tmpl
    ]
    
    if cookie_file:
        common_args.extend(["--cookies", cookie_file])

    match_found = False
    
    # 1. FACEBOOK
    if any(x in url for x in ["facebook.com", "fb.watch"]):
        print(">> Mode: Facebook")
        cmd = base_cmd + ["-N", "16", "--no-part", "--no-keep-fragments"] + common_args + [
            "-x", "--audio-format", "mp3", url
        ]
        run_command(cmd)
        match_found = True

    # 2. YOUTUBE
    elif any(x in url for x in ["youtube.com", "youtu.be", "youtube-nocookie.com"]):
        print(">> Mode: YouTube")
        cmd = base_cmd + ["-N", "4"] + common_args + [
            "--extract-audio", "--audio-format", "mp3", "--audio-quality", "0", # 0 is best
            "--continue",
            "--add-header", "Referer: https://www.youtube.com/",
            "--add-header", f"User-Agent: {ua}",
            url
        ]
        run_command(cmd)
        match_found = True

    # 3. MEDIADELIVERY (Apar's Classroom)
    elif "mediadelivery.net" in url:
        print(">> Mode: MediaDelivery")
        cmd = base_cmd + ["-N", "16", "--no-part", "--no-keep-fragments", "--no-playlist"] + common_args + [
            "-x", "--audio-format", "mp3",
            "--add-header", "Referer: https://academic.aparsclassroom.com/",
            "--add-header", "Origin: https://academic.aparsclassroom.com",
            "--add-header", f"User-Agent: {ua}",
            url
        ]
        run_command(cmd)
        match_found = True

    # 4. Vimeo (EdgeCourseBD vimeo_url directly)
    elif "player.vimeo.com" in url:
        print(">> Mode: Vimeo Url (Direct)")
        # SPEC: Disable cookies for direct Vimeo URLs and use vimeo.com headers
        cmd = base_cmd + ["-N", "16", "--no-part", "--no-keep-fragments", "--no-playlist"] + common_args + [
            "-x", "--audio-format", "mp3",
            "--add-header", "Referer: https://edgecoursebd.com/",
            "--add-header", "Origin: https://edgecoursebd.com",
            "--add-header", f"User-Agent: {ua}",
            url
        ]
        # Remove --cookies if present in common_args (which are part of cmd)
        # Since common_args is a list, we need to find and remove both '--cookies' and its value
        if "--cookies" in cmd:
            idx = cmd.index("--cookies")
            cmd.pop(idx) # remove --cookies
            cmd.pop(idx) # remove the cookie file path
            
        run_command(cmd)
        match_found = True


    # 5. EDGECOURSEBD
    elif "edgecoursebd" in url:
        print(">> Mode: EdgeCourseBD (Running Scraper...)")
        
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "link_extractor.py")
        scraper_cmd = [sys.executable, script_path, "--url", url]
        if cookie_file:
            scraper_cmd.extend(["--cookies", cookie_file])
        if ua:
            scraper_cmd.extend(["--user-agent", ua])
            
        try:
            vimeo_url = run_command(scraper_cmd)
            print(f"   Found Vimeo URL: {vimeo_url}")
            
            cmd = base_cmd + ["-N", "16", "--no-part", "--no-keep-fragments", "--downloader", "ffmpeg", "--hls-use-mpegts", "--referer", url] + common_args + [
                "-x", "--audio-format", "mp3", vimeo_url
            ]
            run_command(cmd)
            match_found = True
        except Exception as e:
            print(f"❌ Scraper failed: {e}")
            raise e

    # 6. FALLBACK
    if not match_found:
        print(">> Mode: Default/Fallback")
        cmd = base_cmd + ["-N", "16"] + common_args + [
            "--extract-audio", "--audio-format", "mp3", "--audio-quality", "5",
            "--continue",
            "--add-header", "Referer: https://www.youtube.com/",
            "--add-header", f"User-Agent: {ua}",
            url
        ]
        try:
            run_command(cmd)
        except Exception as e:
            print(f"❌ Fallback download failed: {e}")
            raise e
    
    final_output = f"{DOWNLOAD_DIR}/{safe_name}.mp3"
    print(f"✅ Download Complete: {final_output}")
    return final_output
