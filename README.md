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