from playwright.sync_api import sync_playwright
import os

# Common Brave paths
POSSIBLE_PATHS = [
    "/usr/bin/brave-browser",
    "/usr/bin/brave",
    "/snap/bin/brave",
    "/opt/brave.com/brave/brave-browser"
]

# Find your Brave executable
executable_path = None
for path in POSSIBLE_PATHS:
    if os.path.exists(path):
        executable_path = path
        break

if not executable_path:
    print("❌ Could not find Brave executable.")
    exit(1)

# Point to your custom profile folder
user_data_dir = os.path.join(os.getcwd(), "browser_profile")

def run_recorder():
    print(f"🚀 Launching Recorder with Brave: {executable_path}")
    print("⚠️  Ensure all other Brave windows are CLOSED.")

    with sync_playwright() as p:
        # launch_persistent_context lets us use a profile AND a custom executable
        context = p.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            executable_path=executable_path,
            headless=False,  # Must be visible
            viewport={"width": 1280, "height": 720},
            args=["--no-first-run"] 
        )

        page = context.pages[0]
        page.goto("https://aistudio.google.com/prompts/new_chat")

        print("\n" + "="*50)
        print("   🔴 RECORDER ACTIVE")
        print("="*50)
        print("1. A 'Playwright Inspector' window should appear.")
        print("   (If you don't see it, look for it in your taskbar).")
        print("2. Click the 'Record' button (Red Circle) in that window.")
        print("3. Perform your clicks in the browser:")
        print("   - Click Model selector -> Gemini 2.5 Pro")
        print("   - Click System Instructions -> Transcriptor")
        print("4. Copy the code generated in the Inspector.")
        print("=================================================")

        # This freezes the script and opens the Inspector UI
        page.pause() 
        
        context.close()

if __name__ == "__main__":
    run_recorder()