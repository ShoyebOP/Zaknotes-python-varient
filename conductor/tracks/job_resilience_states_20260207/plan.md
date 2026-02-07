# Implementation Plan: Enhanced Job Resilience, State Tracking, and Cleanup

## Phase 1: API Quota & Debug Logging Enhancements [checkpoint: 16b62e2]
Goal: Improve transparency and accuracy of API usage and responses.

- [x] Task: Update `APIKeyManager` to increment quota proactively before requests. fecca61
- [x] Task: Enhance `GeminiAPIWrapper` with extensive debug logging and truncated response output. fecca61
- [x] Task: Conductor - User Manual Verification 'Phase 1: API Quota & Debug Logging' (Protocol in workflow.md) 16b62e2

## Phase 2: Granular State Tracking [checkpoint: ebe3ac6]
Goal: Implement persistent intermediate states in the job management system.

- [x] Task: Update `JobManager` state definitions to include intermediate processing steps (DOWNLOADED, SILENCE_REMOVED, CHUNKED, etc.). e3bfc45
- [x] Task: Implement per-chunk transcription state tracking in `JobManager`. e3bfc45
- [x] Task: Conductor - User Manual Verification 'Phase 2: Granular State Tracking' (Protocol in workflow.md) ebe3ac6

## Phase 3: Pipeline Resumption Logic [checkpoint: 38ee98d]
Goal: Modify the main pipeline to utilize new states for resuming interrupted jobs.

- [x] Task: Refactor `Pipeline` to check for existing state/files and skip completed steps. d45d4b6
- [x] Task: Implement transcription resumption logic (skip already transcribed chunks). d45d4b6
- [x] Task: Conductor - User Manual Verification 'Phase 3: Pipeline Resumption Logic' (Protocol in workflow.md) 38ee98d

## Phase 4: Interactive Cleanup
Goal: Provide users with granular control over workspace cleanup.

- [x] Task: Update `CleanupService` to support filtered purging (All vs. Completed/Cancelled Only). 3bf8bc2
- [x] Task: Update CLI in `zaknotes.py` to present interactive cleanup options. 3bf8bc2
- [ ] Task: Conductor - User Manual Verification 'Phase 4: Interactive Cleanup' (Protocol in workflow.md)
