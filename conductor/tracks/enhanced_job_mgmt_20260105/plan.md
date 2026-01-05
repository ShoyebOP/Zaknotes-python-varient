# Plan: Enhanced Job Management and Browser Control

This plan outlines the refactoring of `zaknotes.py` to include a job management sub-menu and a standalone browser launch option, along with necessary logic updates in `JobManager`.

## Phase 1: Job Manager Logic Enhancements [checkpoint: 05ebd85]
- [x] **Task 1: Implement/Verify `cancel_pending` Logic** dbcb301
- [x] **Task 2: Refine Pending Job Retrieval** af7653c
  - **Write Tests**: Verify that `get_pending_from_last_150()` returns the expected jobs for processing.
  - **Implement**: Ensure the method is robust and handles empty history.
- [x] **Task: Conductor - User Manual Verification 'Job Manager Logic Enhancements' (Protocol in workflow.md)** ebe7581

## Phase 2: CLI Menu Refactoring
- [ ] **Task 1: Implement "Launch Browser" (Option 4)**
  - **Write Tests**: Define a test to ensure the browser launch command is triggered correctly from the menu.
  - **Implement**: Add Option 4 to `zaknotes.py`. Use `BrowserDriver` to launch the instance and add a blocking `input()` to keep it open.
- [ ] **Task 2: Shift "Exit" to Option 5**
  - **Implement**: Update the menu loop and conditional logic in `zaknotes.py`.
- [ ] **Task: Conductor - User Manual Verification 'CLI Menu Refactoring' (Protocol in workflow.md)**

## Phase 3: Job Sub-Menu Integration
- [ ] **Task 1: Implement Job Sub-Menu Loop**
  - **Write Tests**: Define tests for the sub-menu routing (Options 1-4).
  - **Implement**: Refactor `start_note_generation()` in `zaknotes.py` to display the new sub-menu and route to the correct logic.
- [ ] **Task 2: Integrate Sub-Menu Logic with JobManager**
  - **Implement**: 
    - Option 1: Call `cancel_pending()`, then `add_jobs()`.
    - Option 2: Call `add_jobs()` without cancelling.
    - Option 3: Call `cancel_pending()` and return.
    - Option 4: Call `get_pending_from_last_150()` and start processing.
- [ ] **Task: Conductor - User Manual Verification 'Job Sub-Menu Integration' (Protocol in workflow.md)**

## Phase 4: Push to Remote & Cleanup
- [ ] **Task 1: Final End-to-End Verification**
  - Manually verify all menu paths and `history.json` updates.
- [ ] **Task 2: Push Commits to GitHub**
  - **Action**: Execute `git push origin main` to ensure all changes reach the remote repository.
- [ ] **Task: Conductor - User Manual Verification 'Push to Remote & Cleanup' (Protocol in workflow.md)**
