# Initial Concept
Class-to-Notes Engine

# Product Guide

## Project Overview
The "Class-to-Notes Engine" is a Linux CLI tool designed to automate the conversion of online class URLs into study-ready Markdown notes. It leverages the Gemini API for high-quality audio transcription and note generation.

## Core Goals
-   **Automate Note Taking:** Streamline the process of turning video/audio content into study notes.
-   **Reliable AI Integration:** Use the official Gemini API for consistent and fast note generation.
-   **High-Quality Markdown Output:** Generate well-formatted Markdown notes ready for any study workflow.
-   **User-Friendly Interface:** Provide a CLI (and eventually a TUI) for easy operation on Linux.

## Key Features
- **Enhanced Queue Management:** Provides granular control over job processing, allowing users to start new jobs, cancel tasks, or resume existing queued jobs.
- **Local Media Processing:** Support for processing local media files placed in the `uploads/` folder via the interactive menu, bypassing the download step.
- **Automated Notion Integration:** Automatically pushes generated notes to a configured Notion database, converting Markdown to Notion-compatible blocks (including LaTeX math and tables).
- **Granular Resumption Logic:** Automatically resumes interrupted jobs from the exact point of failure (e.g., specific transcription chunk) by tracking progress in persistent, job-named intermediate text files.
- **API Quota & Debug Transparency:** Includes proactive API quota counting and extensive, truncated debug logging for all Gemini API interactions to ensure reliability and visibility.
- **Intelligent Media Download:** Utilizes domain-specific rules and specialized headers (for Facebook, YouTube, MediaDelivery, etc.) via `yt-dlp` to ensure reliable content extraction.
- **Customizable Browser Identity:** Allows users to configure a custom Browser User-Agent to improve compatibility and avoid rate-limiting on platforms like YouTube.
- **AI-Powered Generation:** Utilizes internal Gemini CLI authentication and `v1internal` endpoints for high-limit transcription and note generation. Supports a customizable "Model Picker" for every step.
- **Enhanced Transcription & Optimization:** Single-pass audio optimization (silence removal, bitrate, mono, 16kHz) and updated transcription prompts for high accuracy and multilingual support.
- **API Request Reliability:** Robust timeout and retry mechanism for all API calls, including **indefinite retries for rate-limit (429) and empty transcription errors** with exponential backoff.
- **Gemini CLI Account Management:** Robust system for managing multiple Gemini CLI account authorizations with PKCE OAuth2 flow, manual remote support, and automatic token refresh every 90 minutes.
- **Smart Chunking:** Duration-based audio splitting (default 30 minutes, configurable via menu) to optimize transcription workflow and respect API payload limits.
-   **Interactive Workspace Cleanup:** Provides granular control over temporary files, allowing users to purge everything or target only completed/cancelled jobs.
- **Dynamic Resource Scaling:** Automatically detects system CPU/RAM to optimize FFmpeg processing speed (low, balanced, high modes).
- **Clean Output:** Saves final notes as raw Markdown files in a dedicated `notes/` directory.
- **Legacy Note Migration:** Includes a utility to batch-process and push existing local Markdown notes to Notion.
-   **TUI (Planned):** A terminal user interface for seamless interaction.

## Target Audience
-   Students and learners who want to digitize and summarize their class material.
-   Linux users who prefer CLI tools and automation.
