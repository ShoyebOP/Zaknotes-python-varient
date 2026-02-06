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
-   **Enhanced Queue Management:** Provides granular control over job processing, allowing users to start new jobs (with optional clearing of pending tasks), cancel old jobs, or resume existing queued tasks.
- **Automated Retry Logic:** Automatically retries failed or interrupted jobs (e.g., from network issues or browser crashes).
- **Intelligent Media Download:** Utilizes domain-specific rules and specialized headers (for Facebook, YouTube, MediaDelivery, etc.) via `yt-dlp` to ensure reliable content extraction.
- **Customizable Browser Identity:** Allows users to configure a custom Browser User-Agent to improve compatibility and avoid rate-limiting on platforms like YouTube.
- **AI-Powered Generation:** Utilizes the Gemini API (gemini-2.5-flash and gemini-3-flash-preview) for transcription and note generation.
- **API Key Management:** Robust system for managing multiple Gemini API keys with quota tracking and automatic key cycling.
- **Smart Chunking:** Duration-based audio splitting (using configurable `segment_time`) and 10-second delays between processing to respect API rate limits.
- **Dynamic Resource Scaling:** Automatically detects system CPU/RAM to optimize FFmpeg processing speed (low, balanced, high modes).
- **Clean Output:** Saves final notes as raw Markdown files in a dedicated `notes/` directory.
-   **TUI (Planned):** A terminal user interface for seamless interaction.

## Target Audience
-   Students and learners who want to digitize and summarize their class material.
-   Linux users who prefer CLI tools and automation.