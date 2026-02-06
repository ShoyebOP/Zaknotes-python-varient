# Implementation Plan - User-Agent Management & Download Reliability Improvements

## Phase 1: Configuration and UI [checkpoint: 1972c0e]
- [x] Task: Update `ConfigManager` to support `user_agent` with a default value. f1337fb
    - [x] Add `user_agent` to `DEFAULT_CONFIG` in `src/config_manager.py`.
    - [x] Ensure it persists correctly in `config.json`.
- [x] Task: Implement `configure_user_agent` in `zaknotes.py` and add it to the main menu. cde215d
    - [x] Create a new function `configure_user_agent()` similar to `configure_audio_chunking()`.
    - [x] Add the option to the `main_menu()`.
- [x] Task: Conductor - User Manual Verification 'Phase 1: Configuration and UI' (Protocol in workflow.md)

## Phase 2: User-Agent Integration [checkpoint: c220570]
- [x] Task: Modify `src/downloader.py` to fetch User-Agent from `ConfigManager` and apply it to all `yt-dlp` templates. b5960f2
    - [x] Update `download_audio` to use the configured User-Agent instead of a hardcoded one.
- [x] Task: Update `src/link_extractor.py` to accept a `--user-agent` argument and use it in Playwright. b5960f2
    - [x] Add `--user-agent` to `argparse`.
    - [x] Pass the value to `browser.new_context()`.
- [x] Task: Update `src/downloader.py` to pass the configured User-Agent to `src/link_extractor.py`. b5960f2
    - [x] Update the `scraper_cmd` construction in the EdgeCourseBD mode.
- [x] Task: Conductor - User Manual Verification 'Phase 2: User-Agent Integration' (Protocol in workflow.md)

## Phase 3: Cleanup Service Improvement
- [x] Task: Update `FileCleanupService.cleanup_all_temp_files` to recursively clean `downloads/temp`. d210156
    - [x] Modify `src/cleanup_service.py` to include `downloads/temp` in the cleanup logic.
    - [x] Ensure directory structure preservation (keeping `.gitkeep`).
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Cleanup Service Improvement' (Protocol in workflow.md)

## Phase 4: Download Reliability Fixes
- [ ] Task: Adjust YouTube download command in `src/downloader.py`.
    - [ ] Remove or reduce `-N 16` concurrency for YouTube domain to avoid 403 errors.
- [ ] Task: Update EdgeCourseBD/Vimeo download commands in `src/downloader.py`.
    - [ ] Inject `--downloader ffmpeg --hls-use-mpegts` for these domains to handle HLS streams correctly.
- [ ] Task: Conductor - User Manual Verification 'Phase 4: Download Reliability Fixes' (Protocol in workflow.md)

## Phase 5: Documentation
- [ ] Task: Update `README.md` with comprehensive troubleshooting for download errors.
    - [ ] Add sections for 403 Forbidden, HLS stream issues, and general `yt-dlp` tips.
- [ ] Task: Conductor - User Manual Verification 'Phase 5: Documentation' (Protocol in workflow.md)
