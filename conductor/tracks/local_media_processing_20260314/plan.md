# Implementation Plan: Local Media Processing & Audio Processing Optimization

## Phase 1: Local File Processing (Scaffolding & Scoping) [checkpoint: 5aaa15b]
- [x] Task: Create `uploads/` directory with `.gitkeep` fbc465d
- [x] Task: Update `zaknotes.py` CLI to support `--local` flag 254774f
- [x] Task: Implement `LocalMediaManager` to list and map files in `uploads/` 6a0f515
- [x] Task: Write Tests for `LocalMediaManager` (mapping logic, file listing) 6a0f515
- [x] Task: Conductor - User Manual Verification 'Phase 1' (Protocol in workflow.md)

## Phase 2: Pipeline Integration & Refactoring [checkpoint: aa82861]
- [x] Task: Refactor `Pipeline` in `src/pipeline.py` to handle local files (bypass download)
- [x] Task: Update `JobManager` to track status of local file jobs
- [x] Task: Write Tests for `Pipeline` with local file input
- [x] Task: Conductor - User Manual Verification 'Phase 2' (Protocol in workflow.md)


## Phase 3: Audio Processing Optimization (Bugfix) [checkpoint: d8652ad]
- [x] Task: Analyze current redundant audio processing in `src/audio_processor.py`
- [x] Task: Consolidate silence removal, frequency adjustment, and bitrate optimization into a single FFmpeg pass
- [x] Task: Write Tests for optimized `AudioProcessor` (verifying output quality and single-pass behavior)
- [x] Task: Conductor - User Manual Verification 'Phase 3' (Protocol in workflow.md)

## Phase 4: Cleanup & Final Integration [checkpoint: 9f767e1]
- [x] Task: Extend `src/cleanup_service.py` to support purging the `uploads/` directory
- [x] Task: Update main `zaknotes.py` entry point to include the new cleanup option
- [x] Task: Write Tests for `CleanupService` with the `uploads/` directory
- [x] Task: Final end-to-end integration test (local file to note generation)
- [x] Task: Conductor - User Manual Verification 'Phase 4' (Protocol in workflow.md)
