# Implementation Plan: `audio_vimeo_fix_20260425`

## Phase 1: Investigation & Reproductions
- [ ] Task: Investigate the "Double Duration" issue by analyzing `yt-dlp` logs and `ffprobe` output for problematic HLS/Vimeo URLs.
- [ ] Task: Confirm the redundant `optimize_audio` call locations and impact on the pipeline.
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Investigation & Reproductions' (Protocol in workflow.md)

## Phase 2: Audio Processor Refactor (TDD)
- [ ] Task: Create tests to detect redundant optimization calls.
- [ ] Task: Refactor `src/audio_processor.py` to decouple optimization from transcription preparation.
- [ ] Task: Refactor `src/pipeline.py` to call `optimize_audio` only once and pass the result correctly.
- [ ] Task: Verify that `optimize_audio` is called exactly once and logs are correct.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Audio Processor Refactor (TDD)' (Protocol in workflow.md)

## Phase 3: Vimeo Downloader Update (TDD)
- [ ] Task: Write tests for `downloader.py` covering the direct Vimeo URL case (without cookies, with headers).
- [ ] Task: Update `src/downloader.py` to hardcode Referer/Origin for `player.vimeo.com` and disable cookies.
- [ ] Task: Verify direct Vimeo downloads with the new logic.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Vimeo Downloader Update (TDD)' (Protocol in workflow.md)

## Phase 4: Final Validation & Fixes
- [ ] Task: Implement any identified fixes for the "Double Duration" issue (e.g., adding `ffprobe` flags).
- [ ] Task: Run full test suite and verify >80% coverage.
- [ ] Task: Conductor - User Manual Verification 'Phase 4: Final Validation & Fixes' (Protocol in workflow.md)
