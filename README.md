# Zaknotes (Python Variant)

Zaknotes is a powerful Linux CLI tool designed for students and learners who want to automate their study workflow. It effortlessly converts online class URLs (YouTube, Facebook, and more) into high-quality, study-ready **Markdown notes** using the official Google Gemini API.

[demo notes](notes/)

---

## 🛠 Installation & Prerequisites

Zaknotes is optimized for Linux (Arch and Ubuntu). Follow these steps to set up your environment:

### 1. Install System Dependencies

#### **Arch Linux:**
```bash
sudo pacman -Syu ffmpeg nodejs
```

#### **Ubuntu/Debian:**
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y ffmpeg nodejs npm
```

### 2. Install UV (Modern Python Package Manager)
We use `uv` for lightning-fast dependency management.

```bash
# Official installation script
curl -LsSf https://astral.sh/uv/install.sh | sh
# Or via wget
wget -qO- https://astral.sh/uv/install.sh | sh
```

### 3. Notion Integration (Optional)
Zaknotes can automatically push your generated notes to a Notion database.
1.  **Create a Notion Integration:** Go to [Notion My Integrations](https://www.notion.so/my-integrations) and create a new internal integration to get your **Notion API Secret**.
2.  **Setup Database:** Create a database in Notion and [share it with your integration](https://developers.notion.com/docs/create-a-notion-integration#step-2-share-a-database-with-your-integration).
3.  **Get Database ID:** Copy the ID of your database from the URL.

### 4. Clone & Setup
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

---

## 📖 Feature Deep-Dive

Zaknotes offers a granular CLI interface to manage your learning materials.

### 1. Note Generation Sub-Menu
- **Start New Jobs (Cancel Old Jobs):** Clears the current queue and starts a fresh batch.
- **Start New Jobs (Add to Queue):** Appends new links to your existing processing queue.
- **Cancel All Old Jobs:** Flushes the queue without starting new work.
- **Process Queued Jobs:** Resumes processing any pending links in the queue.
- **Process Old Notes (Push to Notion):** Scans your `notes/` folder and pushes any existing Markdown files to your Notion database.

### 2. Manage API Keys & Integration
Zaknotes supports multiple API keys and external integrations.
- **Gemini Keys:** Add/remove keys and view quota status. Zaknotes automatically cycles through keys on exhaustion.
- **Manage Notion Settings:** 
    - Toggle `notion_integration_enabled` to decide if notes should be pushed automatically.
    - Set your **Notion Secret** and **Database ID**.
    - If a Notion push fails, Zaknotes preserves your local Markdown note and marks the job as `completed_local_only`.

### 3. Configure Audio Chunking
Long lectures are automatically split into manageable parts for the AI.
- **Default:** 1800s (30 minutes).
- **Customization:** You can increase or decrease this based on the complexity of the content or API stability.

### 4. Configure Browser User-Agent
Configure a custom User-Agent to improve download reliability and avoid being blocked by platforms like YouTube.

### 5. Cleanup Stranded Audio Chunks
If a process is interrupted, temporary audio files might remain. Use this option to safely purge the `temp/` and `downloads/temp/` directories and reclaim disk space.

### 6. Refresh Cookies
For platforms requiring authentication (like some Facebook or private classroom videos), use this to update your `cookies/bangi.txt` file via an interactive paste.

---

## ❓ Troubleshooting

### 🛑 HTTP Error 403: Forbidden (YouTube)
If you see "403: Forbidden" while downloading from YouTube, it's often due to rate-limiting or signature issues.
- **Solution 1: Update User-Agent.** Use **Option 4** in the main menu to set a modern Browser User-Agent. This helps Zaknotes mimic a real browser.
- **Solution 2: Automatic Concurrency Adjustment.** Zaknotes automatically reduces download concurrency for YouTube to mitigate this error. If it persists, try using a different User-Agent.

### 🎥 HLS Stream Issues (EdgeCourseBD / Vimeo)
Some platforms use HLS (HTTP Live Streaming), which can be tricky to download directly.
- **Solution:** Zaknotes is pre-configured to use `ffmpeg` as the downloader for these platforms. Ensure you have `ffmpeg` installed (`sudo pacman -S ffmpeg`).

### 🍪 403 Forbidden (Facebook/Private Links)
- **Solution:** Your cookies may have expired. Use **Option 6: Refresh Cookies** to update your authentication state.

### 🧽 Cleanup Stranded Chunks
If the tool crashes or is interrupted, temporary files might remain in `temp/` or `downloads/temp/`.
- **Solution:** Use **Option 5: Cleanup Stranded Audio Chunks** to recursively clean all temporary directories while preserving system files like `.gitkeep`.

### ⏳ "429 Too Many Requests"
This means your Gemini API key has hit its limit for the day (quota limits vary by model).
- **Solution:** Add more API keys via **Option 2** in the main menu. Zaknotes will automatically cycle through all available keys.

### 🧩 YouTube "n challenge" or Extraction Errors
If `yt-dlp` fails to download from YouTube, it usually means it cannot find a JavaScript runtime.
- **Solution:** Ensure `nodejs` is installed (`sudo pacman -S nodejs`). Zaknotes uses the EJS solver by default.
