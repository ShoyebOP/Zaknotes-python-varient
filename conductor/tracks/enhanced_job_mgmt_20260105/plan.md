# Plan: Enhanced Job Management and Browser Control

This plan outlines the refactoring of `zaknotes.py` to include a job management sub-menu and a standalone browser launch option, along with necessary logic updates in `JobManager`.

## Phase 1: Job Manager Logic Enhancements [checkpoint: 05ebd85]
- [x] **Task 1: Implement/Verify `cancel_pending` Logic** dbcb301
- [x] **Task 2: Refine Pending Job Retrieval** af7653c
  - **Write Tests**: Verify that `get_pending_from_last_150()` returns the expected jobs for processing.
  - **Implement**: Ensure the method is robust and handles empty history.
- [x] **Task: Conductor - User Manual Verification 'Job Manager Logic Enhancements' (Protocol in workflow.md)** ebe7581

## Phase 2: CLI Menu Refactoring [checkpoint: a3f5f38]
- [x] **Task 1: Implement "Launch Browser" (Option 4)** 456a992
- [x] **Task 2: Shift "Exit" to Option 5** 456a992
  - **Implement**: Update the menu loop and conditional logic in `zaknotes.py`.
- [x] **Task: Conductor - User Manual Verification 'CLI Menu Refactoring' (Protocol in workflow.md)** 0fa3bdd

## Phase 3: Job Sub-Menu Integration [checkpoint: 6e96dd5]
- [x] **Task 1: Implement Job Sub-Menu Loop** a945c5f
- [x] **Task 2: Integrate Sub-Menu Logic with JobManager** a945c5f
- [x] **Task: Conductor - User Manual Verification 'Job Sub-Menu Integration' (Protocol in workflow.md)** 0eb880e

## Phase 4: Push to Remote & Cleanup [checkpoint: ad4d3a4]
- [x] **Task 1: Final End-to-End Verification** ea0a881
  - Manually verify all menu paths and `history.json` updates.
- [x] **Task 2: Push Commits to GitHub** ea0a881
  - **Action**: Execute `git push origin main` to ensure all changes reach the remote repository.
- [x] **Task: Conductor - User Manual Verification 'Push to Remote & Cleanup' (Protocol in workflow.md)** ea0a881
