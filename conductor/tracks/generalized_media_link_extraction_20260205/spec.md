# Specification: Generalized Media Link Extraction and Downloader Enhancement

## Overview
Generalize the link extraction script, rename it to `src/link_extractor.py`, and update `src/downloader.py` to use a `match/case` structure with improved logic for YouTube, Apar's Classroom, and unknown domains.

## Functional Requirements

### 1. Link Extractor Refactor (`src/link_extractor.py`)
- **Rename:** Move `src/find_vimeo_url.py` to `src/link_extractor.py`.
- **New Flags:**
  - `-yt`: Search only for YouTube links (logic from `bookmarlet-youtube.js`).
  - `-md`: Search only for MediaDelivery links (logic from `bookmarlet-apar.js`).
- **Default Behavior:** Continue searching for Vimeo and Vidinfra links if no flags are provided.
- **Cookie Handling:** Load all cookies from the file without domain-specific filtering.
- **Multiple Links Handling:**
  - Display numbered list if multiple unique links are found.
  - Prompt user with a 30-second timeout; default to the first link if no input.

### 2. Downloader Updates (`src/downloader.py`)
- **Refactor:** Use `match/case` for rule selection.
- **Rules:**
  1. **Facebook** (`facebook.com`, `fb.watch`): Direct download.
  2. **YouTube** (`youtube.com`, `youtu.be`, `youtube-nocookie.com`): Direct download using fallback command.
  3. **Apar's Classroom** (`aparsclassroom`):
     - Extract `mediadelivery.net` link using `src/link_extractor.py -md`.
     - Download using custom headers:
       - Referer: `https://academic.aparsclassroom.com/`
       - Origin: `https://academic.aparsclassroom.com`
       - User-Agent: `Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36`
  4. **EdgeCourseBD** (`edgecoursebd`): Use `src/link_extractor.py` (default) to find Vimeo/Vidinfra link, then download.
  5. **Fallback (Unknown Domain):**
     - Pass URL to `src/link_extractor.py -yt`.
     - If a YouTube link is found, download it using the fallback command.
     - If NO link is found, mark job status as `no_link_found`.

### 3. Job Management
- Implement `no_link_found` status in `JobManager`.
- Ensure `no_link_found` jobs are ignored during retries or when processing old jobs.

### 4. Cleanup
- Update all references to `find_vimeo_url.py` to `link_extractor.py`.
- Delete `bookmarlet-apar.js` and `bookmarlet-youtube.js`.

## Acceptance Criteria
- YouTube domains are downloaded directly without extraction.
- Unknown domains trigger a `-yt` extraction attempt.
- Apar's Classroom correctly uses the `-md` extraction and specialized download command.
- `no_link_found` status is correctly applied and respected.
