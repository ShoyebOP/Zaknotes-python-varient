# Implementation Plan: Local Media Processing & Audio Processing Optimization

## Phase 1: Local File Processing (Scaffolding & Scoping)
- [ ] Task: Create `uploads/` directory with `.gitkeep`
- [ ] Task: Update `zaknotes.py` CLI to support `--local` flag
- [ ] Task: Implement `LocalMediaManager` to list and map files in `uploads/`
- [ ] Task: Write Tests for `LocalMediaManager` (mapping logic, file listing)
- [ ] Task: Conductor - User Manual Verification 'Phase 1' (Protocol in workflow.md)

## Phase 2: Pipeline Integration & Refactoring
- [ ] Task: Refactor `Pipeline` in `src/pipeline.py` to handle local files (bypass download)
- [ ] Task: Update `JobManager` to track status of local file jobs
- [ ] Task: Write Tests for `Pipeline` with local file input
- [ ] Task: Conductor - User Manual Verification 'Phase 2' (Protocol in workflow.md)

## Phase 3: Audio Processing Optimization (Bugfix)
- [ ] Task: Analyze current redundant audio processing in `src/audio_processor.py`
- [ ] Task: Consolidate silence removal, frequency adjustment, and bitrate optimization into a single FFmpeg pass
- [ ] Task: Write Tests for optimized `AudioProcessor` (verifying output quality and single-pass behavior)
- [ ] Task: Conductor - User Manual Verification 'Phase 3' (Protocol in workflow.md)

## Phase 4: Cleanup & Final Integration
- [ ] Task: Extend `src/cleanup_service.py` to support purging the `uploads/` directory
- [ ] Task: Update main `zaknotes.py` entry point to include the new cleanup option
- [ ] Task: Write Tests for `CleanupService` with the `uploads/` directory
- [ ] Task: Final end-to-end integration test (local file to note generation)
- [ ] Task: Conductor - User Manual Verification 'Phase 4' (Protocol in workflow.md)
