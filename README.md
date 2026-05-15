# Smart File Organizer

A Python-based CLI tool to scan, organize, and manage files within a directory.
This project aims to automate common file management tasks such as sorting files by type and generating reports.

---

## 🚀 Features (Current)

* CLI interface to run tasks from the terminal
* Directory scanning (lists files in a given path)
* Modular architecture (separated tasks and utilities)
* Cross-platform design (macOS / Windows compatible)

---

## 🛠️ Usage

Run the script from the terminal:

```bash
python3 main.py <task> <path>
```

### Example:

```bash
python3 main.py move /Users/yourname/Downloads
```

---

## 📂 Current Functionality

### `move` task

* Scans the specified directory
* Lists all items found inside
* (File organization logic coming soon)

### `report` task

* Placeholder for future report generation

---

## ⚠️ macOS Permissions

On macOS, you may encounter a `PermissionError` when accessing folders like Downloads, Desktop, or Documents.

To resolve this:

1. Go to **System Settings → Privacy & Security**
2. Open:

   * **Files and Folders** (recommended), or
   * **Full Disk Access** (optional)
3. Grant access to your terminal application (Terminal, iTerm, or VS Code)

---

## 🧱 Project Structure

```
smart-file-organizer/
│
├── main.py
├── tasks/
│   ├── file_sorter.py
│   ├── report_generator.py
│
├── utils/
├── logs/
├── reports/
├── config.yaml
└── README.md
```

---

## 🧭 Roadmap

* [x] CLI interface
* [x] Directory scanning
* [ ] File classification (by type)
* [ ] File moving / organization
* [ ] Report generation
* [ ] Logging system
* [ ] Config-driven rules

---

## 🎯 Goal

Build a reusable and configurable automation tool that simplifies file management workflows and demonstrates clean Python architecture for real-world use cases.

---

## 📌 Notes

This project is being developed incrementally with a focus on:

* clean structure
* modular design
* real-world usability
