# Specification: Rclone Remote Pushing Integration (v3)

## Overview
This track introduces a new remote storage method using `rclone`. This feature allows users to automatically push generated Markdown notes to a remote destination (e.g., Google Drive, Dropbox, S3) as soon as they are created.

## Functional Requirements
- **Configuration:**
    - Add a new "Rclone Configuration" section to the interactive CLI menu.
    - Allow users to specify the `rclone` remote name and path (e.g., `remote:path`).
    - **Provide a toggle to enable or disable Rclone directly within this configuration section.**
    - Persist these settings in the system's config file.
- **Coexistence with Notion:**
    - Both Rclone and Notion integration can be enabled at the same time.
    - **Warn the user if they try to enable both integrations simultaneously, informing them that this will add extra steps and may slow down the note-generation process.**
- **Sequential Automated Pushing:**
    - Immediately after a job's Markdown note is generated and saved locally, execute the pushing tasks sequentially (e.g., Notion push followed by Rclone push).
    - Rclone command format: `rclone copy <local_note_path> <remote_destination_path>`.
- **User Feedback:**
    - Display clear success messages when a note is pushed via Rclone.
    - Log and display descriptive error messages if the `rclone` command fails.

## Non-Functional Requirements
- **Resilience:** If the `rclone` push fails, the local pipeline and other integrations (like Notion) should continue, but the failure should be clearly logged.
- **Maintainability:** The implementation should follow the project's existing patterns for service integration (similar to the Notion service).

## Acceptance Criteria
- [ ] Users can configure and toggle Rclone via the CLI menu.
- [ ] A warning is displayed when both Rclone and Notion integrations are enabled.
- [ ] Generated notes are automatically pushed to the configured Rclone destination when enabled.
- [ ] Success/failure of the push is clearly communicated in the CLI output.

## Out of Scope
- Automatic installation or setup of `rclone` (user is responsible for system-level configuration).
- Support for multiple Rclone remotes simultaneously.
- Advanced `rclone` operations like `sync` or `move`.
