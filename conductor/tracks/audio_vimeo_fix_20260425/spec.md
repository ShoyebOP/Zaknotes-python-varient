# Specification: `audio_vimeo_fix_20260425`

## Overview
This track addresses three distinct issues in the audio processing and downloading pipeline:
1.  **Redundant Audio Optimization:** The pipeline currently optimizes the audio twice, leading to redundant processing and duplicate logs.
2.  **Audio Duration Doubling:** An investigation into rare cases where downloaded audio duration is reported as double its actual length.
3.  **Vimeo Direct Download Refinement:** Updating the downloader to handle direct Vimeo URLs with hardcoded referrers and origins, while explicitly disabling cookie usage.

## Functional Requirements

### 1. Remove Redundant Audio Optimization
- Refactor `src/pipeline.py` and `src/audio_processor.py` to ensure `optimize_audio` is called exactly once per job.
- Currently, `ProcessingPipeline.execute_job` calls `AudioProcessor.optimize_audio` and then `AudioProcessor.process_for_transcription`, which calls it again.
- The `AudioProcessor.process_for_transcription` method should be simplified to assume the input is already optimized, or `ProcessingPipeline` should rely on `process_for_transcription` to handle both optimization and chunking.

### 2. Investigate and Fix Audio Duration Doubling
- Analyze the `yt-dlp` and `ffmpeg` interaction for specific edge cases (especially Vimeo/HLS) that might cause incorrect duration reporting.
- Potential fix: Ensure `ffprobe` uses more accurate duration detection (e.g., `-analyze_duration`, `-probesize`).
- Verify if `-c copy` in `split_into_chunks` is safe for the optimized audio format.

### 3. Vimeo Direct Download Update
- In `src/downloader.py`, update the `player.vimeo.com` block.
- Disable cookie usage for direct Vimeo URLs (do not pass `--cookies`).
- Hardcode `Referer` and `Origin` to Vimeo specific values.
- Ensure `ua` (User-Agent) is still passed.

## Non-Functional Requirements
- Maintain existing TDD standards.
- Ensure >80% test coverage for changes.

## Acceptance Criteria
- [ ] `optimize_audio` log appears only once per audio file in the console output.
- [ ] Direct Vimeo downloads function correctly without cookies and with specified headers.
- [ ] Investigation report or fix for the doubled duration issue is provided.
- [ ] All tests pass, including new tests for the Vimeo downloader logic.

## Out of Scope
- Major architectural changes to the pipeline.
- Supporting new platforms not mentioned.
