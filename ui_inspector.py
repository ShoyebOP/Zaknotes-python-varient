from browser_driver import BrowserDriver
from playwright.sync_api import sync_playwright
import time

def inspect_ui():
    driver = BrowserDriver()
    print("🚀 Launching Browser for UI Inspection...")
    
    # Increased timeout for your slow system
    page = driver.get_ai_studio_page()
    
    if not page:
        print("❌ Failed to connect.")
        return

    print("⏳ Waiting 5 seconds for page to fully render...")
    page.wait_for_timeout(5000)
    
    print("📸 Scanning page elements...")
    
    output = []
    output.append("=== BUTTONS ===")
    try:
        buttons = page.get_by_role("button").all()
        for b in buttons:
            if b.is_visible():
                txt = b.text_content().strip().replace("\n", " ")
                output.append(f"Button: '{txt}'")
    except: pass

    output.append("\n=== INPUTS / TEXTAREAS ===")
    try:
        inputs = page.get_by_role("textbox").all()
        for i in inputs:
            if i.is_visible():
                ph = i.get_attribute("placeholder") or "No Placeholder"
                output.append(f"Input: Placeholder='{ph}'")
    except: pass
    
    output.append("\n=== SPECIFIC TEXT SEARCH ===")
    # Searching for things you mentioned
    targets = ["System Instructions", "Model", "Gemini", "Run", "Upload", "Transcriptor"]
    for t in targets:
        count = page.get_by_text(t).count()
        output.append(f"Found '{t}': {count} times")

    # Save to file
    with open("ui_dump.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(output))
        
    print("✅ Scan Complete. Saved to 'ui_dump.txt'.")
    print("👋 You can close the browser now.")

if __name__ == "__main__":
    inspect_ui()