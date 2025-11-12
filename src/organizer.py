# ============================================================================
# DownNest - Smart Downloads Organizer
# Version: 1.0.0
# 
# Copyright (c) 2025 Isiyak Solomon
# Licensed under MIT License - See LICENSE.txt for details
# 
# GitHub: https://github.com/isiyaksolomon-dev/downnest
# Email: isiyak.solomon.01@gmail.com
# ============================================================================

import os
import time
import shutil
import threading
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# ----------------------------
# Configuration
# ----------------------------

# Detect all user profiles (including default)
USERS_DIR = Path("C:/Users")
DOWNLOAD_FOLDERS = []

for user_dir in USERS_DIR.iterdir():
    if user_dir.is_dir():
        dl = user_dir / "Downloads"
        if dl.exists():
            DOWNLOAD_FOLDERS.append(dl)

# Define categories and extensions
CATEGORIES = {
    "Documents": [".pdf", ".docx", ".txt", ".pptx", ".xls", ".xlsx"],
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg"],
    "Videos": [".mp4", ".avi", ".mov", ".mkv"],
    "Music": [".mp3", ".wav", ".aac", ".flac"],
    "Archives": [".zip", ".rar", ".7z", ".tar", ".gz"],
    "Installers": [".exe", ".msi"],
    "Code": [".py", ".js", ".html", ".css", ".cpp", ".c", ".java"],
    "Others": []
}

# Temporary browser download extensions to ignore
TEMP_EXTENSIONS = [".crdownload", ".part", ".download"]

# Thread pool for moving files
executor = ThreadPoolExecutor(max_workers=os.cpu_count() or 4)

# ----------------------------
# Helper functions
# ----------------------------

def get_category(file_path: Path) -> str:
    ext = file_path.suffix.lower()
    for category, exts in CATEGORIES.items():
        if ext in exts:
            return category
    return "Others"

def move_file(file_path: Path):
    """Move file to appropriate category folder."""
    if not file_path.exists() or file_path.suffix.lower() in TEMP_EXTENSIONS:
        return

    category = get_category(file_path)
    dest_dir = file_path.parent / category
    dest_dir.mkdir(exist_ok=True)

    try:
        shutil.move(str(file_path), str(dest_dir / file_path.name))
        print(f"✅ Moved {file_path.name} → {category}")
    except Exception as e:
        print(f"⚠️ Failed to move {file_path.name}: {e}")

def wait_for_complete(file_path: Path, retries=3, delay=0.5):
    """Wait until file download is complete by checking stable size."""
    last_size = -1
    stable_count = 0

    while stable_count < retries:
        if not file_path.exists():
            return False
        current_size = file_path.stat().st_size
        if current_size == last_size:
            stable_count += 1
        else:
            stable_count = 0
            last_size = current_size
        time.sleep(delay)
    return True

def process_file(file_path: Path):
    if file_path.suffix.lower() in TEMP_EXTENSIONS:
        return
    if wait_for_complete(file_path):
        print(f"⏳ Waiting 30s before moving {file_path.name}...")
        time.sleep(30)
        move_file(file_path)

# ----------------------------
# Watchdog event handler
# ----------------------------

class DownloadHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            executor.submit(process_file, Path(event.src_path))

    def on_moved(self, event):
        if not event.is_directory:
            executor.submit(process_file, Path(event.dest_path))

# ----------------------------
# Initial organization
# ----------------------------

def organize_existing():
    for folder in DOWNLOAD_FOLDERS:
        for f in folder.iterdir():
            if f.is_file() and f.suffix.lower() not in TEMP_EXTENSIONS:
                executor.submit(move_file, f)

# ----------------------------
# Main program
# ----------------------------

def main():
    print("📂 Starting Downloads Organizer for all users...")
    organize_existing()

    observers = []
    for folder in DOWNLOAD_FOLDERS:
        handler = DownloadHandler()
        observer = Observer()
        observer.schedule(handler, str(folder), recursive=False)
        observer.start()
        observers.append(observer)

    print("✅ Monitoring active Downloads folders...")
    try:
        while True:
            time.sleep(2)
    except KeyboardInterrupt:
        print("🛑 Stopping organizer...")
        for obs in observers:
            obs.stop()
        for obs in observers:
            obs.join()
        executor.shutdown(wait=True)
        print("✅ Organizer stopped.")

if __name__ == "__main__":
    main()
