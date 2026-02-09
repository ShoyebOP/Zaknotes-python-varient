# Specification: Track Cleanup and Backup Branching

## Overview
This track focuses on project maintenance. It involves cleaning up the `tracks.md` registry to remove redundant entries for archived tracks and creating a dedicated branch to preserve the current state of the codebase, which already utilizes the official Google AI SDK.

## Functional Requirements
- **Tracks Registry Cleanup:** 
    - Identify entries in `conductor/tracks.md` that point to the `conductor/archive/` directory.
    - Remove these entries to keep the registry focused on active or pending tracks.
- **Backup Branch Creation:**
    - Create a new Git branch named `genai/Google-AI-SDK` from the current HEAD.
    - This branch serves as a snapshot/backup of the current progress.

## Non-Functional Requirements
- **Registry Integrity:** Ensure `tracks.md` remains a valid Markdown file after removal of entries.
- **Version Control:** The new branch must be created without affecting the current working branch.

## Acceptance Criteria
- [ ] `conductor/tracks.md` no longer contains entries that link to the `archive/` directory.
- [ ] A new branch named `genai/Google-AI-SDK` exists in the local repository and matches the current HEAD.

## Out of Scope
- Implementation of new features or SDK migrations (as the SDK is already in use).
- Moving folders to `archive/` (as the requested folders are already there).
