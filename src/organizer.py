# ============================================================================
# DownNest - Smart Downloads Organizer
# Version: 2.0.8 - Added Notification Sound & UI Improvements
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
import sys
import winsound
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Qt5 imports
try:
    from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGraphicsOpacityEffect
    from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QObject, pyqtSignal
    from PyQt5.QtGui import QFont
    QT_AVAILABLE = True
except ImportError:
    QT_AVAILABLE = False

# ----------------------------
# Configuration
# ----------------------------

USERS_DIR = Path("C:/Users")
DOWNLOAD_FOLDERS = []

for user_dir in USERS_DIR.iterdir():
    if user_dir.is_dir():
        dl = user_dir / "Downloads"
        if dl.exists():
            DOWNLOAD_FOLDERS.append(dl)

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

CATEGORY_EMOJIS = {
    "Documents": "📄",
    "Images": "🖼️",
    "Videos": "🎬",
    "Music": "🎵",
    "Archives": "📦",
    "Installers": "⚙️",
    "Code": "💻",
    "Others": "📁"
}

TEMP_EXTENSIONS = [".crdownload", ".part", ".download"]
executor = ThreadPoolExecutor(max_workers=os.cpu_count() or 4)

# ----------------------------
# Global Qt5 Application
# ----------------------------

_app = None
_notifications = []
_notification_manager = None

_hide_all_container = None
_hide_all_btn = None
_hide_all_spacing = 8

def get_qt_app():
    global _app
    if not _app:
        _app = QApplication.instance()
        if not _app:
            _app = QApplication(sys.argv)
    return _app

# ----------------------------
# Thread-Safe Notification Signals
# ----------------------------

class NotificationSignaler(QObject):
    notification_signal = pyqtSignal(str, str, str, str)

    def __init__(self):
        super().__init__()
        self.notification_signal.connect(self._show_notification, Qt.QueuedConnection)

    def _show_notification(self, title, message, category, file_path):
        try:
            app = get_qt_app()
            notification = GlassNotification(title, message, category, file_path if file_path != "" else None)
            notification.show()
            _notifications.append(notification)

            # Play Windows notification sound
            winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)

            for _ in range(5):
                app.processEvents()
                time.sleep(0.02)
        except Exception as e:
            print(f"⚠️ Notification error: {e}")
        _update_hide_all_button()

    def notify(self, title, message, category="Others", file_path=None):
        self.notification_signal.emit(title, message, category, str(file_path) if file_path else "")

def get_notification_signaler():
    global _notification_manager
    if not _notification_manager and QT_AVAILABLE:
        app = get_qt_app()
        _notification_manager = NotificationSignaler()
        _notification_manager.moveToThread(app.thread())
    return _notification_manager

# ----------------------------
# Minimalistic Glass Notification Widget
# ----------------------------

class GlassNotification(QWidget):
    def __init__(self, title, message, category="Others", file_path=None, duration=10000):
        super().__init__()
        self.title = title
        self.message = message
        self.category = category
        self.file_path = Path(file_path) if file_path else None
        self.duration = duration

        self.init_ui()
        self.setup_position()
        self.setup_animations()

    def init_ui(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        content = QWidget()
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(12, 10, 12, 10)
        content_layout.setSpacing(12)

        # Accent bar
        accent_bar = QWidget()
        accent_bar.setFixedWidth(5)
        accent_bar.setStyleSheet("background-color:#6B7280; border-radius:2px;")
        content_layout.addWidget(accent_bar)

        # Icon
        icon_label = QLabel(CATEGORY_EMOJIS.get(self.category,"📁"))
        icon_label.setFont(QFont('Arial',28))
        icon_label.setFixedSize(50,50)
        icon_label.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(icon_label)

        # Text layout
        text_layout = QVBoxLayout()
        text_layout.setSpacing(4)

        title_lbl = QLabel("DownNest")
        title_lbl.setFont(QFont("Segoe UI", 10, QFont.Bold))
        title_lbl.setStyleSheet("color:#000000;")
        text_layout.addWidget(title_lbl)

        sep = QWidget()
        sep.setFixedHeight(1)
        sep.setStyleSheet("background-color: #D1D5DB;")
        text_layout.addWidget(sep)

        msg_lbl = QLabel(self.message)
        msg_lbl.setFont(QFont("Segoe UI", 10))  # Slightly larger for professional look
        msg_lbl.setWordWrap(True)
        msg_lbl.setStyleSheet("color:#1F2937;")
        msg_lbl.setMaximumWidth(280)
        text_layout.addWidget(msg_lbl)
        text_layout.addStretch()
        content_layout.addLayout(text_layout)

        # Buttons layout
        btn_layout = QVBoxLayout()
        btn_width, btn_height = 60, 30

        if self.file_path and self.file_path.exists():
            open_btn = QPushButton("Open")
            open_btn.setFont(QFont("Segoe UI", 8, QFont.Bold))
            open_btn.setFixedSize(btn_width, btn_height)
            open_btn.setStyleSheet("background-color:#10B981; color:white; border:none; border-radius:5px;")
            open_btn.clicked.connect(self.open_file)
            btn_layout.addWidget(open_btn)

        close_btn = QPushButton("×")
        close_btn.setFont(QFont("Arial", 12))
        close_btn.setFixedSize(btn_width, btn_height)
        close_btn.clicked.connect(self.close_notification)
        close_btn.setStyleSheet("background-color:#EF4444; color:white; border:none; border-radius:5px;")
        btn_layout.addWidget(close_btn)
        btn_layout.addStretch()
        content_layout.addLayout(btn_layout)

        content.setLayout(content_layout)
        content.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 10px;
            }
        """)
        layout.addWidget(content)
        self.setLayout(layout)

        self.setMinimumWidth(380)
        self.setMaximumWidth(380)
        self.adjustSize()

        self.hide_timer = QTimer()
        self.hide_timer.setSingleShot(True)
        self.hide_timer.timeout.connect(self.fade_out)

    def setup_position(self):
        screen = QApplication.primaryScreen().geometry()
        x = int(screen.width() - self.width() - 30)
        y = int(screen.height() - self.height() - 80)
        for n, notif in enumerate(_notifications):
            y -= (notif.height() + _hide_all_spacing)
        self.move(x, y)

    def setup_animations(self):
        self.opacity_effect = QGraphicsOpacityEffect()
        self.opacity_effect.setOpacity(1)
        self.setGraphicsEffect(self.opacity_effect)

        self.fade_out_anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_out_anim.setDuration(900)
        self.fade_out_anim.setStartValue(1)
        self.fade_out_anim.setEndValue(0)
        self.fade_out_anim.setEasingCurve(QEasingCurve.InOutCubic)
        self.fade_out_anim.finished.connect(self.close)

    def showEvent(self, event):
        super().showEvent(event)
        if self.duration > 0:
            self.hide_timer.start(self.duration)
        _update_hide_all_button()

    def fade_out(self):
        if self.hide_timer.isActive(): self.hide_timer.stop()
        self.fade_out_anim.start()

    def open_file(self):
        if self.file_path and self.file_path.exists():
            os.startfile(self.file_path)
        self.fade_out()

    def close_notification(self):
        self.fade_out()

    def closeEvent(self, event):
        if self in _notifications: _notifications.remove(self)
        _update_hide_all_button()
        super().closeEvent(event)

# ----------------------------
# Hide All Button Logic
# ----------------------------

def _create_hide_all_button():
    global _hide_all_btn, _hide_all_container
    if _hide_all_btn is None:
        app = get_qt_app()
        _hide_all_container = QWidget()
        _hide_all_container.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        _hide_all_container.setAttribute(Qt.WA_TranslucentBackground)
        layout = QHBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        _hide_all_btn = QPushButton("Hide All")
        _hide_all_btn.setFont(QFont("Segoe UI", 11, QFont.Bold))
        _hide_all_btn.setFixedSize(380, 30)
        _hide_all_btn.setStyleSheet("background-color:#1F2937; color:white; border-radius:5px; border:none;")
        _hide_all_btn.clicked.connect(_hide_all_notifications)
        layout.addWidget(_hide_all_btn)
        _hide_all_container.setLayout(layout)

        # Hide All fade-out animation
        _hide_all_opacity = QGraphicsOpacityEffect()
        _hide_all_btn.setGraphicsEffect(_hide_all_opacity)
        _hide_all_btn.fade_anim = QPropertyAnimation(_hide_all_opacity, b"opacity")
        _hide_all_btn.fade_anim.setDuration(900)
        _hide_all_btn.fade_anim.setStartValue(1)
        _hide_all_btn.fade_anim.setEndValue(0)
        _hide_all_btn.fade_anim.setEasingCurve(QEasingCurve.InOutCubic)
        _hide_all_btn.fade_anim.finished.connect(_hide_all_container.hide)

    _position_hide_all_button()
    _hide_all_container.show()

def _position_hide_all_button():
    global _hide_all_btn, _hide_all_container
    if not _hide_all_container or not _hide_all_btn:
        return
    screen = QApplication.primaryScreen().geometry()
    x = int(screen.width() - _hide_all_btn.width() - 30)
    if _notifications:
        y_top = min(notif.y() for notif in _notifications)
        y = y_top - _hide_all_btn.height() - _hide_all_spacing
    else:
        y = int(screen.height() - 80)
    _hide_all_container.setGeometry(x, y, _hide_all_btn.width(), _hide_all_btn.height())

def _update_hide_all_button():
    global _hide_all_btn, _hide_all_container
    if len(_notifications) >= 2:
        _create_hide_all_button()
    elif _hide_all_container:
        # Fade out when hiding
        _hide_all_btn.fade_anim.start()

def _hide_all_notifications():
    global _hide_all_btn, _hide_all_container
    for notif in _notifications[:]:
        notif.hide()
        if notif in _notifications:
            _notifications.remove(notif)
    if _hide_all_container:
        _hide_all_btn.fade_anim.start()

# ----------------------------
# Thread-safe notification wrapper
# ----------------------------

def show_notification(title, message, category="Others", file_path=None):
    if not QT_AVAILABLE:
        print(f"\n📢 {title}\n{message}")
        return
    try:
        signaler = get_notification_signaler()
        if signaler:
            signaler.notify(title, message, category, file_path)
    except Exception as e:
        print(f"⚠️ Error showing notification: {e}")

# ----------------------------
# Helper functions
# ----------------------------

def get_category(file_path: Path) -> str:
    ext = file_path.suffix.lower()
    for cat, exts in CATEGORIES.items():
        if ext in exts: return cat
    return "Others"

def format_size(size_bytes):
    for unit in ['B','KB','MB','GB']:
        if size_bytes<1024: return f"{size_bytes:.1f}{unit}"
        size_bytes/=1024
    return f"{size_bytes:.1f}TB"

def move_file(file_path: Path, notify=True):
    if not file_path.exists() or file_path.suffix.lower() in TEMP_EXTENSIONS:
        return
    category = get_category(file_path)
    dest_dir = file_path.parent / category
    dest_dir.mkdir(exist_ok=True)
    try:
        dest_path = dest_dir / file_path.name
        shutil.move(str(file_path), str(dest_path))
        print(f"✅ Moved {file_path.name} → {category}")

        if notify:
            try:
                size = format_size(dest_path.stat().st_size)
            except:
                size = "Unknown"
            message = f"{file_path.name}\n→ {category} • {size}"
            show_notification("File Organized", message, category, dest_path)

    except Exception as e:
        print(f"⚠️ Failed to move {file_path.name}: {e}")

def wait_for_complete(file_path: Path, retries=3, delay=0.5):
    last = -1
    stable = 0
    while stable < retries:
        if not file_path.exists(): 
            return False
        cur = file_path.stat().st_size
        if cur == last: 
            stable += 1
        else: 
            stable = 0
            last = cur
        time.sleep(delay)
    return True

def process_file(file_path: Path):
    if file_path.suffix.lower() in TEMP_EXTENSIONS:
        return
    print(f"⏳ Processing {file_path.name}...")
    time.sleep(30)
    if wait_for_complete(file_path):
        move_file(file_path, notify=True)

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
# Organize existing files
# ----------------------------

def organize_existing():
    moved = 0
    for folder in DOWNLOAD_FOLDERS:
        try:
            for f in folder.iterdir():
                if f.is_file() and f.suffix.lower() not in TEMP_EXTENSIONS:
                    move_file(f, notify=False)
                    moved += 1
        except:
            pass
    if moved > 0:
        msg = f"Downloads folder organized.\nFiles moved: {moved}\nAll files sorted into categories."
        show_notification("DownNest", msg, "Others")

# ----------------------------
# Main program
# ----------------------------

def main():
    if QT_AVAILABLE:
        print("🔧 Initializing Qt5 Application...")
        app = get_qt_app()
        get_notification_signaler()
    else:
        app = None

    print("📂 Starting Downloads Organizer")
    print(f"📍 Qt5 Notifications: {'✅ Enabled' if QT_AVAILABLE else '⚠️ Disabled'}")
    print(f"📍 Monitoring {len(DOWNLOAD_FOLDERS)} Downloads folder(s)")
    print(f"📍 Notification Style: 🎨 Minimalistic Glass Morphism")

    organize_existing()

    observers = []
    for folder in DOWNLOAD_FOLDERS:
        try:
            handler = DownloadHandler()
            obs = Observer()
            obs.schedule(handler, str(folder), recursive=False)
            obs.start()
            observers.append(obs)
        except Exception as e:
            print(f"⚠️ Failed to monitor {folder}: {e}")

    print("✅ Monitoring active... Ctrl+C to stop\n")
    
    try:
        while True:
            if QT_AVAILABLE and app:
                try:
                    app.processEvents()
                except:
                    pass
            time.sleep(0.05)
    except KeyboardInterrupt:
        print("\n🛑 Stopping organizer...")
        for obs in observers: obs.stop()
        for obs in observers: obs.join()
        executor.shutdown(wait=True)
        print("✅ Organizer stopped gracefully")
        print("👋 Thank you for using DownNest!")
        sys.exit(0)

if __name__ == "__main__":
    main()
