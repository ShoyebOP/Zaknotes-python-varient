# Plan: Enhanced Reliability and Job Retry Logic

## Phase 1: UI Stability & Root Cause Investigation
Focus: Identifying and fixing why the bot stalls during model/system instruction selection.

- [x] Task: Investigate `src/ui_elements/` and `src/bot_engine.py` to identify cause of selection hangs.
- [x] Task: Implement direct fix for Model/System Instruction selection logic. 1931a5c
- [x] Task: Write/Update unit tests for UI interaction components to ensure stability. b82bc75
- [x] Task: Verify fix manually by running the bot through multiple model selection cycles. 3b4f13e
- [ ] Task: Conductor - User Manual Verification 'UI Stability & Root Cause Investigation' (Protocol in workflow.md)

## Phase 2: AI Response Reliability
Focus: Preventing empty PDFs by ensuring the AI has finished generating content.

- [ ] Task: Implement 2-second mandatory sleep after file upload completion in `src/bot_engine.py`.
- [ ] Task: Implement AI response growth monitoring loop in `src/bot_engine.py`.
    - Sub-task: Logic to detect response block visibility.
    - Sub-task: Loop to compare content length every 1 second.
    - Sub-task: Implement 15-second inactivity timeout to stop waiting.
- [ ] Task: Write unit tests for the growth monitoring logic (using mocks for response content).
- [ ] Task: Conductor - User Manual Verification 'AI Response Reliability' (Protocol in workflow.md)

## Phase 3: Job Management & Retry Logic
Focus: Updating the queue system to automatically retry failed jobs.

- [ ] Task: Update `src/job_manager.py` to include `failed` status in the list of jobs to be processed.
- [ ] Task: Modify job selection logic in the CLI menu to group `pending` and `failed` jobs together for the user.
- [ ] Task: Ensure `cancelled` jobs are explicitly ignored in all processing queries.
- [ ] Task: Write unit tests in `tests/test_job_manager_logic.py` for the updated queue selection logic.
- [ ] Task: Conductor - User Manual Verification 'Job Management & Retry Logic' (Protocol in workflow.md)

## Phase 4: Fallback Recovery System
Focus: Implementing a "hard reset" mechanism if UI interactions fail despite the fix.

- [ ] Task: Implement browser session restart logic in `src/bot_engine.py` upon interaction timeout.
    - Sub-task: Catch timeout/interaction exceptions during setup.
    - Sub-task: Logic to close current Playwright/Chromium instance and re-initialize.
- [ ] Task: Verify recovery flow by simulating a selection failure.
- [ ] Task: Conductor - User Manual Verification 'Fallback Recovery System' (Protocol in workflow.md)
