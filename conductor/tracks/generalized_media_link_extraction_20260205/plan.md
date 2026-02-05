# Implementation Plan: Generalized Media Link Extraction and Downloader Enhancement

## Phase 1: Link Extractor Generalization (TDD)
- [~] Task: Rename `src/find_vimeo_url.py` to `src/link_extractor.py` and update imports.
- [ ] Task: Write tests for `link_extractor.py` covering Vimeo, YouTube (`-yt`), and MediaDelivery (`-md`) extraction.
- [ ] Task: Implement `-yt` flag logic (from `bookmarlet-youtube.js`) in `link_extractor.py`.
- [ ] Task: Implement `-md` flag logic (from `bookmarlet-apar.js`) in `link_extractor.py`.
- [ ] Task: Implement interactive selection with timeout in `link_extractor.py`.
- [ ] Task: Generalize cookie loading in `link_extractor.py` to load all cookies without domain filtering.
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Link Extractor Generalization' (Protocol in workflow.md)

## Phase 2: Downloader Refactor and Enhancement (TDD)
- [ ] Task: Update `JobManager` in `src/job_manager.py` to support `no_link_found` status and filter it out.
- [ ] Task: Write tests for `src/downloader.py` covering new `match/case` structure and specialized rules.
- [ ] Task: Refactor `download_audio` in `src/downloader.py` to use `match/case`.
- [ ] Task: Implement Apar's Classroom rule using `link_extractor.py -md` and the specialized `yt-dlp` command.
- [ ] Task: Implement fallback rule using `link_extractor.py -yt` and `no_link_found` handling.
- [ ] Task: Ensure all `yt-dlp` calls use `cookies/bangi.txt` (or appropriate cookie path).
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Downloader Refactor and Enhancement' (Protocol in workflow.md)

## Phase 3: Cleanup and Finalization
- [ ] Task: Delete `bookmarlet-apar.js` and `bookmarlet-youtube.js`.
- [ ] Task: Perform final verification of the entire pipeline.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Cleanup and Finalization' (Protocol in workflow.md)
