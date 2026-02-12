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
-   **Enhanced Queue Management:** Provides granular control over job processing, allowing users to start new jobs, cancel tasks, or resume existing queued jobs.
-   **Automated Notion Integration:** Automatically pushes generated notes to a configured Notion database, converting Markdown to Notion-compatible blocks (including LaTeX math and tables).
-   **Granular Resumption Logic:** Automatically resumes interrupted jobs from the exact point of failure (e.g., specific transcription chunk) by tracking persistent intermediate states.
-   **API Quota & Debug Transparency:** Includes proactive API quota counting and extensive, truncated debug logging for all Gemini API interactions to ensure reliability and visibility.
- **Intelligent Media Download:** Utilizes domain-specific rules and specialized headers (for Facebook, YouTube, MediaDelivery, etc.) via `yt-dlp` to ensure reliable content extraction.
- **Customizable Browser Identity:** Allows users to configure a custom Browser User-Agent to improve compatibility and avoid rate-limiting on platforms like YouTube.
- **AI-Powered Generation:** Utilizes the Gemini API (gemini-2.5-flash and gemini-3-flash-preview) for transcription and note generation with optimized system instructions.
- **Enhanced Transcription Accuracy:** Updated transcription prompts to enforce "Clean Verbatim" output, removing filler words while strictly preserving meaningful academic content and maintaining the original language (e.g., Bangla/English code-switching).
- **API Request Reliability:** Robust timeout and retry mechanism for all API calls, with mandatory round-robin key rotation to ensure high availability and prevent single-key rate-limiting.
- **API Key Management:** Robust system for managing multiple Gemini API keys with quota tracking, mandatory rotation, and automatic key cycling on exhaustion.
- **Smart Chunking:** Duration-based audio splitting (using configurable `segment_time`) and 10-second delays between processing to respect API rate limits.
-   **Interactive Workspace Cleanup:** Provides granular control over temporary files, allowing users to purge everything or target only completed/cancelled jobs.
- **Dynamic Resource Scaling:** Automatically detects system CPU/RAM to optimize FFmpeg processing speed (low, balanced, high modes).
- **Clean Output:** Saves final notes as raw Markdown files in a dedicated `notes/` directory.
- **Legacy Note Migration:** Includes a utility to batch-process and push existing local Markdown notes to Notion.
-   **TUI (Planned):** A terminal user interface for seamless interaction.

## Target Audience
-   Students and learners who want to digitize and summarize their class material.
-   Linux users who prefer CLI tools and automation.