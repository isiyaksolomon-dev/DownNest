# 🪺 DownNest - Smart Downloads Organizer

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE.txt)
[![Platform: Windows](https://img.shields.io/badge/Platform-Windows%207%2B-blue)]()
[![Version: 1.0.0](https://img.shields.io/badge/Version-1.0.0-green)]()

**DownNest automatically organizes your Downloads folder into meaningful categories in real-time, runs as a Windows service, and requires zero configuration.**

---

## ✨ Features

- 🤖 **Automatic Organization** - Monitors downloads in real-time and sorts files by type.
- ⚡ **Multi-user Support** - Organizes all users’ Downloads folders on the system.
- 🔒 **Safe** - Handles locked files, avoids data loss, and respects permissions.
- 🎯 **Smart Categories**:
  - Documents (PDF, DOCX, TXT, PPTX, XLSX)
  - Images (JPG, PNG, GIF, SVG)
  - Videos (MP4, AVI, MKV, MOV)
  - Music (MP3, WAV, FLAC, M4A)
  - Archives (ZIP, RAR, 7Z, TAR, GZ)
  - Installers (EXE, MSI)
  - Code (PY, JS, HTML, CSS, etc.)
  - Others (everything else)
- 🚀 **Zero Config** - Works out-of-the-box without setup.
- 🔄 **Auto-start** - Runs as Windows service automatically at boot.
- 📊 **Lightweight** - Minimal RAM usage (~5–10 MB).

---

## 📋 System Requirements

- Windows 7 SP1 or later (32-bit or 64-bit)
- Administrator rights for service installation
- 100 MB free disk space
- Python 3.8+ required only if building from source

---

## 🚀 Installation

1. Download the latest installer: `DownNest_Setup_1.0.0.exe`
2. Run installer (Admin privileges required)
3. Follow the wizard steps
4. Finished! Service starts automatically

**After installation:**

- DownNest runs silently in the background.
- Organizes downloads for all users automatically.
- Desktop and Start Menu shortcuts are created.

---

## 📁 Folder Organization

By default, your files are organized as follows:

```

Downloads/
├── Documents/ (PDF, DOCX, TXT, XLSX, PPTX)
├── Images/ (JPG, PNG, GIF, SVG)
├── Videos/ (MP4, AVI, MKV, MOV)
├── Music/ (MP3, WAV, FLAC, M4A)
├── Archives/ (ZIP, RAR, 7Z, TAR, GZ)
├── Installers/ (EXE, MSI)
├── Code/ (PY, JS, HTML, CSS, etc.)
└── Others/ (Everything else)

````

---

## 🎮 Usage

### Automatic Mode (Default)
- Runs silently in the background as a Windows service.
- Organizes files immediately as they are downloaded.
- Starts automatically with Windows.

### Manual Service Management
1. Press `Windows + R` → type `services.msc`
2. Locate **DownNest** in the list
3. Options:
   - Start / Stop / Restart service
   - Check service status

### Debug Mode (Optional)
If you want to run manually and see console logs:

```bash
python src/organizer.py debug
````

---

## ⚙️ Configuration

You can customize categories and extensions:

1. Open `config_default.json` in installation folder:

```json
{
  "downloads_dir": "",
  "destinations": {
    "Documents": [".pdf", ".docx", ".txt", ".xlsx"],
    "Images": [".jpg", ".png", ".gif"],
    "Videos": [".mp4", ".avi", ".mkv"]
  }
}
```

2. Modify categories or add new ones.
3. Save and restart the service:

```bash
net stop DownNest
net start DownNest
```

---

## 🛠️ Building from Source

1. Install Python 3.8+
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Download NSSM from [https://nssm.cc/download](https://nssm.cc/download)
4. Build executable with `build.bat` (bundles everything using PyInstaller)
5. Create installer using Inno Setup:

```bash
iscc installer_script.iss
```

---

## 🆘 Troubleshooting

| Issue               | Solution                                                                           |
| ------------------- | ---------------------------------------------------------------------------------- |
| Service won't start | Verify in `services.msc`. Restart service if needed.                               |
| Files not moving    | Ensure service is running; restart with `net stop DownNest && net start DownNest`. |
| High CPU usage      | Normal during initial organization of existing files.                              |
| Permission errors   | Run installer as Administrator.                                                    |

---

## 🗑️ Uninstall

* **Control Panel → Programs → Uninstall → DownNest**
* Or manually (Admin):

```bash
net stop DownNest
sc delete DownNest
rmdir /s "C:\Program Files\DownNest"
```

---

## 📄 License

[MIT License](LICENSE.txt)

* **Use commercially:** ✅
* **Modify:** ✅
* **Distribute:** ✅
* **Requirements:** Include license, state changes if modified.

---

## 👨‍💻 Author

**Isiyak Solomon**

* Email: [isiyak.solomon.01@gmail.com](mailto:isiyak.solomon.01@gmail.com)
* GitHub: [@isiyaksolomon](https://github.com/isiyaksolomon-dev)
* Website: [https://isiyaksolomon.pro.et](https://isiyaksolomon.pro.et)

---

## ❓ FAQ

**Q: Is DownNest free?**
A: Yes, MIT open-source license.

**Q: Does it slow down my computer?**
A: No, minimal impact (~5-10 MB RAM, <1% CPU idle).

**Q: Can I customize categories?**
A: Yes, edit `config_default.json` and restart the service.

**Q: Is my data safe?**
A: Yes, files are only moved; no deletion occurs by default.

**Q: Does it require internet?**
A: No, completely offline after installation.

**Q: Can I install on multiple computers?**
A: Yes, repeat installation on each machine.

---

## 📞 Support

* Check FAQ above
* Read `README.md` or `INSTALL_GUIDE.md` for detailed instructions
* Email: [isiyak.solomon.01@gmail.com](mailto:isiyak.solomon.01@gmail.com)
* Report bugs: Include Windows version + error messages

---

**Version 1.0.0 | Stable Release | Last Updated: January 2025**
