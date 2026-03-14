# Specification: Local Media Processing & Audio Processing Optimization

## Overview
Currently, Zaknotes only supports processing media via URL submissions. This track introduces a new `--local` processing mode that allows users to upload media files directly to a designated `uploads/` folder and process them into study-ready Markdown notes. Additionally, the audio processing pipeline will be optimized to eliminate redundant re-encoding steps.

## Functional Requirements
- **Local File Mode:** Introduce a `--local` CLI flag.
- **Uploads Directory:** Files should be placed in an `uploads/` folder in the project root.
- **Processing Logic:** 
    - If `--local` is used without a specific name, Zaknotes will process ALL files in the `uploads/` folder sequentially.
    - If names are provided (e.g., `python zaknotes.py --local "Biology Lecture" "History Lecture"`), Zaknotes will map these names chronologically to the files found in `uploads/` (first name to first file, second to second, etc.).
- **Naming Logic:**
    - By default, the generated note's filename will be the same as the source media filename (without extension).
    - If a specific name is provided as an input, that name will replace the default filename for the note.
- **Supported File Types:** Primary focus on `mp3` and `mp4`.
- **File Management:** Files are kept in the `uploads/` folder after processing. A new cleanup option (or extension to the existing cleanup service) will be provided to clear the `uploads/` folder.
- **Pipeline Integration:** Local file processing will reuse the existing transcription and note generation pipeline, bypassing the download/link extraction steps.

## Performance Optimization (Bugfix)
- **Single Audio Pass:** Currently, the audio file is processed twice (once for silence removal/re-encoding and possibly again later). Optimize the `audio_processor.py` to ensure silence removal, bitrate optimization, and frequency adjustment are performed in a single FFmpeg pass.

## Non-Functional Requirements
- **Efficiency:** Skip `yt-dlp` download for local files; proceed directly to audio processing/transcription.
- **Reliability:** Ensure robust error handling if the `uploads/` folder is empty or contains unsupported file types.

## Acceptance Criteria
- [ ] Users can place an `.mp3` or `.mp4` file in `uploads/` and run `python zaknotes.py --local` to generate a note.
- [ ] Multiple files in `uploads/` are processed sequentially when `--local` is used.
- [ ] Providing names with `--local` (e.g., `python zaknotes.py --local "Biology Lecture"`) correctly names the output note and maps to the uploaded file.
- [ ] The existing `cleanup_service` (or a similar tool) can be used to purge the `uploads/` folder.
- [ ] Local processing handles interruptions using the same resumption logic as URL-based jobs.
- [ ] FFmpeg logs (if enabled) confirm that audio optimization (silence removal, bitrate, frequency) happens in a single pass.

## Out of Scope
- Direct file uploading via a web UI (this is a CLI/Codespace-focused feature).
- Support for complex matching (e.g., fuzzy matching or partial name matching).
