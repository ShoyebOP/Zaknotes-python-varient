# Implementation Plan: Generalized Media Link Extraction and Downloader Enhancement

## Phase 1: Link Extractor Generalization (TDD)
- [x] Task: Rename `src/find_vimeo_url.py` to `src/link_extractor.py` and update imports. e469cd1
- [x] Task: Write tests for `link_extractor.py` covering Vimeo/Vidinfra extraction. d3c32e9
- [x] Task: Implement interactive selection with timeout in `link_extractor.py`. d3c32e9
- [x] Task: Generalize cookie loading in `link_extractor.py` to load all cookies without domain filtering. d3c32e9
- [x] Task: Conductor - User Manual Verification 'Phase 1: Link Extractor Generalization' (Protocol in workflow.md) d3c32e9
- [~] Task: Remove -yt and -md logic and tests from Phase 1.

## Phase 2: Downloader Refactor and Enhancement (TDD)
- [ ] Task: Update `JobManager` in `src/job_manager.py` to support `no_link_found` status and filter it out.
- [ ] Task: Write tests for `src/downloader.py` covering new `match/case` structure and specialized rules.
- [ ] Task: Refactor `download_audio` in `src/downloader.py` to use `match/case`.
- [ ] Task: Implement MediaDelivery rule (`mediadelivery.net`) with specialized headers.
- [ ] Task: Implement fallback rule with direct download attempt and `no_link_found` handling.
- [ ] Task: Ensure all `yt-dlp` calls use `cookies/bangi.txt` (or appropriate cookie path).
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Downloader Refactor and Enhancement' (Protocol in workflow.md)

## Phase 3: Cleanup and Finalization
- [ ] Task: Delete `bookmarlet-apar.js` and `bookmarlet-youtube.js`.
- [ ] Task: Perform final verification of the entire pipeline.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Cleanup and Finalization' (Protocol in workflow.md)
