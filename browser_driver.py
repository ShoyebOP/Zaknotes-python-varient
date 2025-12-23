import subprocess
import os
import time
import socket
import sys
from playwright.sync_api import sync_playwright

# --- CONFIGURATION ---
BROWSER_PATHS = [
    "/usr/bin/chromium",
    "/usr/bin/chromium-browser",
    "/snap/bin/chromium",
    "/usr/bin/google-chrome",
    "/usr/bin/google-chrome-stable",
    "/usr/bin/brave-browser",
    "/usr/bin/brave-browser-stable",
    "/usr/bin/brave",
    "/snap/bin/brave",
    "/opt/brave.com/brave/brave-browser"
]

# Absolute path is safer for string matching in process list
PROFILE_DIR = os.path.abspath(os.path.join(os.getcwd(), "browser_profile"))
DEBUG_PORT = 9222

class BrowserDriver:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None

    def is_port_open(self, port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) == 0

    def verify_correct_profile(self):
        """
        GUARDRAIL: Checks if the browser on port 9222 is actually OURS.
        Returns:
            True  -> Safe (Our profile is running)
            False -> Danger (Another profile is using the port)
            None  -> Port is closed (Nothing running)
        """
        if not self.is_port_open(DEBUG_PORT):
            return None

        try:
            # List all processes with full arguments
            # ps -ef lists UID, PID, ..., CMD
            output = subprocess.check_output(["ps", "-ef"], text=True)
            
            for line in output.splitlines():
                # We look for the browser command AND the port
                if f"remote-debugging-port={DEBUG_PORT}" in line:
                    # Now check if OUR profile path is in the command arguments
                    if PROFILE_DIR in line:
                        return True
                    else:
                        print(f"⚠️  SECURITY ALERT: Found a browser on port {DEBUG_PORT}, but it matches a different profile!")
                        print(f"   Expected: {PROFILE_DIR}")
                        print(f"   Found process: {line[:100]}...") # Print snippet of the rogue process
                        return False
            
            # If we found the port open but couldn't find the process in ps (rare permission issue?), assume unsafe
            return False
            
        except Exception as e:
            print(f"⚠️  Error checking process list: {e}")
            return False

    def launch_browser(self):
        status = self.verify_correct_profile()
        
        if status is False:
            print("\n❌ STOPPING: Port 9222 is occupied by the WRONG browser profile.")
            print("   Please close your main Browser instance running in debug mode.")
            print("   (Or kill the process manually).")
            sys.exit(1) # Hard exit to prevent hijacking main profile
            
        if status is True:
            print("⚡ Dedicated browser is already running. Reconnecting...")
            return True

        print("🚀 Launching Dedicated Chromium Instance...")
        print(f"📂 Profile Location: {PROFILE_DIR}")
        
        # Find Executable
        browser_exe = None
        for path in BROWSER_PATHS:
            if os.path.exists(path):
                browser_exe = path
                break
        
        if not browser_exe:
            raise Exception("❌ Could not find Chromium/Chrome/Brave executable.")

        # Optimization Flags
        cmd = [
            browser_exe,
            f"--remote-debugging-port={DEBUG_PORT}",
            f"--user-data-dir={PROFILE_DIR}",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-extensions",
            "--disable-popup-blocking",
            "--mute-audio",
            "--disable-notifications",
            "--window-size=1000,800", 
            "https://aistudio.google.com/"
        ]

        # Run in background
        subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        print("⏳ Waiting for browser to initialize...")
        for i in range(10):
            if self.is_port_open(DEBUG_PORT):
                # Double check verification just to be 100% sure
                if self.verify_correct_profile():
                    print("✅ Browser detected & Verified!")
                    time.sleep(2)
                    return True
            time.sleep(1)
        
        raise Exception("❌ Browser launched but port 9222 did not open.")

    def connect(self):
        self.launch_browser() 

        print("🔌 Connecting via Playwright...")
        self.playwright = sync_playwright().start()
        
        try:
            self.browser = self.playwright.chromium.connect_over_cdp(f"http://localhost:{DEBUG_PORT}")
            
            if not self.browser.contexts:
                self.context = self.browser.new_context()
            else:
                self.context = self.browser.contexts[0]
                
            return True
        except Exception as e:
            print(f"❌ Connection Failed: {e}")
            return False

    def get_ai_studio_page(self):
        if not self.context:
            if not self.connect(): return None

        for page in self.context.pages:
            if "aistudio.google" in page.url:
                page.bring_to_front()
                return page
        
        print("✨ Opening new AI Studio tab...")
        page = self.context.new_page()
        page.goto("https://aistudio.google.com/")
        return page

    def close(self):
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()