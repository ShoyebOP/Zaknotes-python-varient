from browser_driver import BrowserDriver
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
import time
import os

# --- CONFIGURATION ---
TARGET_MODEL_NAME = "Gemini 2.5 Pro"
TARGET_MODEL_ID = "model-carousel-row-models/gemini-2.5-pro"
TARGET_SYSTEM_PROMPT = "transcriptor" 

class AIStudioBot:
    def __init__(self):
        self.driver = BrowserDriver()
        self.page = None

    def start_session(self):
        print("🤖 Bot: Connecting to session...")
        if not self.driver.connect(): 
            raise Exception("Could not connect to browser.")
        
        context = self.driver.context
        found = False
        for p in context.pages:
            if "aistudio" in p.url:
                self.page = p
                found = True
                p.bring_to_front()
                break
        
        if not found:
            print("   Opening new AI Studio tab...")
            self.page = context.new_page()
            self.page.goto("https://aistudio.google.com/prompts/new_chat")
        
        self.page.wait_for_load_state("networkidle")

    def select_model(self):
        print(f"🤖 Bot: Checking Model ({TARGET_MODEL_NAME})...")
        try:
            # 1. CHECK CURRENT MODEL
            card = self.page.locator(".model-selector-card").first
            if not card.is_visible():
                 card = self.page.locator("button[data-test-id='model-selector']").first
            
            # Wait a moment for text to populate
            card.wait_for(state="visible", timeout=5000)
            current_text = card.text_content()
            
            if TARGET_MODEL_NAME in current_text:
                print(f"   ✅ Already on {TARGET_MODEL_NAME}. Skipping selection.")
                return

            # 2. OPEN MENU
            print("   Model mismatch. Opening menu...")
            card.click()
            
            # Wait for the "All" button to appear to confirm menu is open
            all_btn = self.page.locator("button[data-test-category-button='']").filter(has_text="All")
            try:
                all_btn.wait_for(state="visible", timeout=5000)
                print("   Menu Open. Clicking 'All'...")
                all_btn.click()
                time.sleep(1) # Wait for list to filter
            except:
                print("   ⚠️ 'All' button not found, assuming list is ready...")

            # 3. FIND & CLICK TARGET
            print(f"   Looking for ID: {TARGET_MODEL_ID}")
            model_btn = self.page.locator(f'button[id="{TARGET_MODEL_ID}"]')
            
            # Force scroll if list is long
            try:
                if model_btn.count() > 0:
                    model_btn.scroll_into_view_if_needed()
                
                # We use a short timeout so we don't get stuck for 30s
                model_btn.click(timeout=5000)
                print(f"   ✅ Switched to {TARGET_MODEL_NAME}")
            except Exception as e:
                print(f"   ❌ Could not click model button: {e}")
                print("   (Is the ID correct? Is it off screen?)")

            # 4. CLOSE PANEL
            try:
                close_btn = self.page.get_by_label("Close panel")
                if close_btn.is_visible():
                    close_btn.click(timeout=2000)
            except: pass
            
            # 5. FINAL VERIFICATION
            time.sleep(1)
            new_text = card.text_content()
            if TARGET_MODEL_NAME not in new_text:
                print(f"   ⚠️ WARNING: Model switch might have failed. Current: {new_text[:20]}...")

        except Exception as e:
            print(f"   ❌ Model selection error: {e}")

    def set_system_prompt(self, prompt_name):
        print(f"🤖 Bot: Setting System Prompt ({prompt_name})...")
        try:
            # 1. Open Sidebar
            self.page.locator("button[data-test-system-instructions-card]").click()
            self.page.wait_for_timeout(1500)

            # 2. Open Dropdown
            dropdown = self.page.locator(".mat-mdc-select-trigger").last
            dropdown.click()
            self.page.wait_for_timeout(1000)

            # 3. Select Option
            option = self.page.locator("mat-option").filter(has_text=prompt_name).first
            
            # Wait for it to be visible
            try:
                option.wait_for(state="visible", timeout=3000)
                option.click()
                print(f"   ✅ Selected: {prompt_name}")
            except:
                print(f"   ❌ Prompt '{prompt_name}' not found in list.")

            # 4. Close Sidebar
            time.sleep(1)
            try:
                close_btn = self.page.get_by_label("Close panel")
                if close_btn.is_visible():
                    close_btn.click()
            except: pass

        except Exception as e:
            print(f"   ❌ System Prompt failed: {e}")

    def close(self):
        self.driver.close()

if __name__ == "__main__":
    bot = AIStudioBot()
    try:
        bot.start_session()
        bot.select_model()
        bot.set_system_prompt(TARGET_SYSTEM_PROMPT)
        print("\n✅ Setup Test Complete.")
    except Exception as e:
        print(f"CRASH: {e}")