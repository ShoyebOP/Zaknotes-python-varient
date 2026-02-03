# Zaknotes (Python Variant)

Zaknotes is a powerful Linux CLI tool designed for students and learners who want to automate their study workflow. It effortlessly converts online class URLs (YouTube, Facebook, and more) into high-quality, study-ready **Markdown notes** using the official Google Gemini API.

---

## 🛠 Arch Linux Installation & Prerequisites

Zaknotes is optimized for Arch Linux. Follow these steps to set up your environment:

### 1. Install System Dependencies
Zaknotes requires `ffmpeg` for audio processing and `nodejs` to solve YouTube's "n challenge" via the EJS solver.

```bash
sudo pacman -S ffmpeg nodejs
```

### 2. Install UV (Modern Python Package Manager)
We use `uv` for lightning-fast dependency management and virtual environments.

```bash
sudo pacman -S uv
```

### 3. Clone & Setup
```bash
git clone https://github.com/ShoyebOP/Zaknotes-python-varient.git
cd Zaknotes-python-varient
uv sync
```

---

## 🚀 Quick Start Guide (The "Happy Path")

Get your first set of notes in 3 easy steps:

### 1. Add your Gemini API Key
Run the tool and navigate to API management:
```bash
uv run python zaknotes.py
```
- Select **Option 2: Manage API Keys**
- Select **Option 1: Add API Key**
- Paste your key from [Google AI Studio](https://aistudio.google.com/app/apikey).

### 2. Start Note Generation
Return to the main menu and start a new job:
- Select **Option 1: Start Note Generation**
- Select **Option 1: Start New Jobs (Cancel Old Jobs)**
- Provide a name for your notes (e.g., `Biology_Lecture_1`) and the class URL.

### 3. Retrieve Your Notes
Once the pipeline finishes, your high-quality Markdown notes will be waiting for you in the `notes/` directory:
```bash
ls notes/
```
