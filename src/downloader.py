import os
import subprocess
import shlex
import sys
from urllib.parse import urlparse

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

def run_command(cmd_str):
    print(f"Executing: {cmd_str}")
    process = subprocess.run(shlex.split(cmd_str), capture_output=True, text=True)
    if process.returncode != 0:
        print(f"❌ Error: {process.stderr}")
        raise Exception(process.stderr)
    return process.stdout.strip()

def download_audio(job):
    url = job['url']
    name = job['name']
    
    # Clean filename
    safe_name = name.replace(" ", "_").replace("/", "-")
    filename_tmpl = f"{safe_name}.%(ext)s"
    
    # Paths: Save final to 'downloads', temp stuff to 'temp'
    paths_arg = f'--paths "home:{DOWNLOAD_DIR}" --paths "temp:{TEMP_DIR}"'
    
    cookie_file = get_cookie_path()
    cookie_arg = f'--cookies "{cookie_file}"' if cookie_file else ""

    print(f"\n⬇️  Starting Download: {name}")
    
    domain = urlparse(url).netloc.lower()
    
    # Common UA
    ua = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

    # Match domain or characteristic parts of the URL
    match_found = False
    
    # 1. FACEBOOK
    if any(x in url for x in ["facebook.com", "fb.watch"]):
        print(">> Mode: Facebook")
        cmd = (
            f'{YT_DLP_BASE} {CONCURRENCY} {EJS_ARGS} --no-part --no-keep-fragments '
            f'{cookie_arg} {paths_arg} '
            f'-f "{SMART_FORMAT}" '
            f'-x --audio-format mp3 '
            f'-o "{filename_tmpl}" "{url}"'
        )
        run_command(cmd)
        match_found = True

    # 2. YOUTUBE
    elif any(x in url for x in ["youtube.com", "youtu.be", "youtube-nocookie.com"]):
        print(">> Mode: YouTube")
        cmd = (
            f'{YT_DLP_BASE} {CONCURRENCY} {EJS_ARGS} '
            f'-f "{SMART_FORMAT}" '
            f'--extract-audio --audio-format mp3 --audio-quality 5 '
            f'--continue {cookie_arg} {paths_arg} '
            f'-o "{filename_tmpl}" '
            f'--add-header "Referer: https://www.youtube.com/" '
            f'--add-header "User-Agent: {ua}" '
            f'"{url}"'
        )
        run_command(cmd)
        match_found = True

    # 3. MEDIADELIVERY (Apar's Classroom)
    elif "mediadelivery.net" in url:
        print(">> Mode: MediaDelivery")
        cmd = (
            f'{YT_DLP_BASE} {CONCURRENCY} {EJS_ARGS} --no-part --no-keep-fragments '
            f'{cookie_arg} {paths_arg} --no-playlist '
            f'-f "{SMART_FORMAT}" '
            f'-x --audio-format mp3 '
            f'--add-header "Referer: https://academic.aparsclassroom.com/" '
            f'--add-header "Origin: https://academic.aparsclassroom.com" '
            f'--add-header "User-Agent: {ua}" '
            f'-o "{filename_tmpl}" "{url}"'
        )
        run_command(cmd)
        match_found = True

    # 4. EDGECOURSEBD
    elif "edgecoursebd" in url:
        print(">> Mode: EdgeCourseBD (Running Scraper...)")
        
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "link_extractor.py")
        scraper_cmd = f'"{sys.executable}" "{script_path}" --url "{url}"'
        if cookie_file:
            scraper_cmd += f' --cookies "{cookie_file}"'
            
        try:
            vimeo_url = run_command(scraper_cmd)
            print(f"   Found Vimeo URL: {vimeo_url}")
            
            cmd = (
                f'{YT_DLP_BASE} {CONCURRENCY} {EJS_ARGS} --no-part --no-keep-fragments '
                f'--referer "{url}" '
                f'{cookie_arg} {paths_arg} '
                f'-f "{SMART_FORMAT}" '
                f'-x --audio-format mp3 '
                f'-o "{filename_tmpl}" "{vimeo_url}"'
            )
            run_command(cmd)
            match_found = True
        except Exception as e:
            print(f"❌ Scraper failed: {e}")
            raise e

    # 5. FALLBACK
    if not match_found:
        print(">> Mode: Default/Fallback")
        cmd = (
            f'{YT_DLP_BASE} {CONCURRENCY} {EJS_ARGS} '
            f'-f "{SMART_FORMAT}" '
            f'--extract-audio --audio-format mp3 --audio-quality 5 '
            f'--continue {cookie_arg} {paths_arg} '
            f'-o "{filename_tmpl}" '
            f'--add-header "Referer: https://www.youtube.com/" '
            f'--add-header "User-Agent: {ua}" '
            f'"{url}"'
        )
        try:
            run_command(cmd)
        except Exception as e:
            print(f"❌ Fallback download failed: {e}")
            raise e
    
    final_output = f"{DOWNLOAD_DIR}/{safe_name}.mp3"
    print(f"✅ Download Complete: {final_output}")
    return final_output
