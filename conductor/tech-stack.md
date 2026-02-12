# Tech Stack

## Programming Language
- **Python 3.x:** Primary language for orchestration, browser automation, and pipeline management.

## Browser Automation
- **Playwright (Python):** Used for connecting to an existing Chromium instance (port 9222), automating Google AI Studio, and generating PDF files from HTML.

## AI Platform
- **Gemini API:** Utilizing official Google Generative AI API for transcription and note generation.
- **google-genai:** Official Python SDK for the Gemini API (successor to `google-generativeai`).

## External Integrations
- **Notion API:** Used for automated note storage and organization.
- **notion-client:** Official Python SDK for the Notion API.

## Formatting & Conversion
- **Markdown:** Final output format for generated notes.
- **Pandoc:** (Deprecated) Previously used for converting Markdown to HTML.
- **HTML/CSS:** (Deprecated) Previously used for PDF generation.

## Environment
- **Linux:** Target operating system for the CLI tool.

## Key Dependencies
- `google-genai`: Python library for Gemini API interaction.
- `notion-client`: For Notion API interaction and note storage.
- `yt-dlp`: For video metadata and audio extraction.
- `ffmpeg/ffprobe`: For audio processing, duration retrieval, and silent part removal.
- `pytest`: For automated testing.
- `urllib.parse`: Python standard library for domain and URL parsing.
