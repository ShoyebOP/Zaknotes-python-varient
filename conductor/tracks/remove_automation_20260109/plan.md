# Plan: Remove Browser Automation and UI Elements

## Phase 1: Logic Replacement & Placeholder Implementation
- [x] Task: Create `tests/test_placeholders.py` to verify that `zaknotes.py` functions (e.g., `refresh_browser_profile`, `launch_manual_browser`) can be called without error and produce expected log output. 1bf68a4
- [x] Task: Modify `zaknotes.py` to remove imports of `BrowserDriver`, `AIStudioBot`, `process_job` and replace their usage with log messages (e.g., "Browser automation placeholder triggered"). 1bf68a4
- [x] Task: Verify that `zaknotes.py` no longer references the to-be-deleted modules. 1bf68a4
- [x] Task: Conductor - User Manual Verification 'Logic Replacement & Placeholder Implementation' (Protocol in workflow.md) 1bf68a4

## Phase 2: Selenium to Playwright Migration
- [ ] Task: Create `tests/test_find_vimeo_url.py` to test the current Vimeo URL extraction logic (Red Phase).
- [ ] Task: Refactor `src/find_vimeo_url.py` to use `playwright` instead of `selenium`.
- [ ] Task: Verify that `src/find_vimeo_url.py` correctly extracts Vimeo URLs using Playwright.
- [ ] Task: Remove `selenium` from `requirements.txt`.
- [ ] Task: Conductor - User Manual Verification 'Selenium to Playwright Migration' (Protocol in workflow.md)

## Phase 3: Component Removal
- [ ] Task: Delete `src/browser_driver.py`.
- [ ] Task: Delete `src/bot_engine.py`.
- [ ] Task: Delete `src/ui_elements/` directory.
- [ ] Task: Delete `tests/` directory (excluding the newly created `test_placeholders.py` and `test_find_vimeo_url.py`). *I will back up these specific test files, delete the rest of `tests/`, and restore them.*
- [ ] Task: Conductor - User Manual Verification 'Component Removal' (Protocol in workflow.md)

## Phase 4: Cleanup & Verification
- [ ] Task: Audit `requirements.txt` and remove any dependencies that are now strictly unused (like `webdriver-manager` if present).
- [ ] Task: Final verification that the application starts and video download references are intact.
- [ ] Task: Conductor - User Manual Verification 'Cleanup & Verification' (Protocol in workflow.md)
