# Smart File Organizer (v0.3.0)

A Python CLI tool that organizes files in a directory by scanning, classifying, and moving them into structured folders.

It automates file management tasks such as sorting files by type and preparing structured outputs for future reporting features.

## 🚀 Quick Start

```bash
python3 main.py move ~/Downloads
```
---

## 1. 🧠 Project Overview

Smart File Organizer is a lightweight CLI automation tool for cleaning and structuring directories such as Downloads or Desktop:

1. Scans a target folder  
2. Classifies files by type  
3. Creates organized directories  
4. Moves files into structured folders  

---

## 2. ✨ Features
* CLI-based interface for task execution  
* Directory scanning and file detection  
* File classification system based on extensions
* Automated folder creation  
* File moving engine  
* Prefixed folder structure (`smartorg-*`)  
* Modular architecture with clear separation of concerns:
  - `file_sorter.py` → scanning & classification  
  - `file_mover.py` → file system operations  
  - `report_generator.py` → placeholder (future feature)  
* Structured logging system with:
   - timestamped logs
   - log levels (INFO / WARN / ERROR)
   - module attribution (MAIN, FILE_SORTER, FILE_MOVER, LOGGER)
* Execution trace visibility for debugging workflows
* Task-based routing system via main.py
* Cross-platform design (macOS / Windows compatible)

---

## 3. 🧱 Architecture (Design & Structure)
### 🧩 Design Principles
* Separation of concerns
* Modular architecture with internal logging
* Parent modules only logging lifecycle events
* CLI-first design
* Cross-platform compatibility (macOS & Windows)
* Safe filesystem operations (basic validation)

### 📁 Project Structure

```
smart-file-organizer/
│
├── main.py
├── config.yaml (future)
├── logs/
│   └── smartorg.log
│
├── tasks/
│   ├── file_sorter.py
│   ├── file_mover.py
│   ├── report_generator.py (placeholder)
│
├── utils/
│   └── logger.py
│
├── README.md
└── requirements.txt
```

### 🔄 Data Flow

#### move task

```md
CLI Input
   ↓
main.py (lifecycle logging only)
   ↓
scan_and_classify() → FILE_SORTER logs internally
   ↓
move_files() → FILE_MOVER logs internally
   ↓
File system organized
```

#### report task

* Placeholder for future report generation

---

## 4. 🧰 Usage & Execution


###  ▶️ How to Use
Run the CLI tool from the terminal:

```bash
python3 main.py <task> <path>
```

#### 📦 Move & organize files

```bash
python3 main.py move /path/to/directory
```

#### Example:

```bash
python3 main.py move /Users/yourname/Downloads
```

#### 📊 Generate report (not implemented yet)
```bash
python3 main.py report /path/to/directory
```

#### Example:

```bash
python3 main.py report /Users/yourname/Downloads
```


### ⚠️ macOS Permissions

On macOS, you may encounter a `PermissionError` when accessing folders like Downloads, Desktop, or Documents.

To resolve this:

1. Go to **System Settings → Privacy & Security**
2. Open:

   * **Files and Folders** (recommended), or
   * **Full Disk Access** (optional)
3. Grant access to your terminal application (Terminal, iTerm, or VS Code)

---

## 5. 🧪 Development Overview

### 🎯 Project Intent

Smart File Organizer is being developed as a portfolio project to demonstrate Python automation, CLI design, and modular architecture.


### 📌 Development Principles

- Clean and maintainable structure
- Separation of concerns (sorting, moving, reporting)
- Module-level responsibility for logging
- Scalable architecture for future configuration system
- Real-world usability for file system automation

### 🧭 Roadmap

#### v0.1.0 (Initial Setup)
 * [x] CLI interface (basic skeleton)
 * [x] Project structure setup

#### v0.2.0 (Core Automation)
 * [x] Directory scanning
 * [x] File classification (by type)
 * [x] File moving / organization (smartorg-* folders)
 * [x] Basic task routing system

#### v0.3.0 (Current - Stability & Observability)
* [x] Structured logging system
* [x] Module-based log ownership
* [x] Execution trace improvements
* [x] Hidden file filtering

#### v0.4.0 (Configuration Layer)
 * [ ] Config-driven rules (config.yaml)
 * [ ] Custom folder prefixes
 * [ ] Enable/disable file categories
 * [ ] User-defined classification rules

#### v1.0.0 (Stable Release)
 * [ ] Full configuration system
 * [ ] Dry-run mode (preview changes without executing)
 * [ ] Robust safety controls
 * [ ] Fully documented CLI tool
 * [ ] Production-ready structure

### 🚧 Current Limitations (v0.3.0)

- No configuration file (settings are currently hardcoded)
- No dry-run mode
- No undo functionality
- Basic classification rules only
- Report generator not implemented yet
---

## 6. 📜 Version History
[v0.3.0] (Current)
* Introduced structured logging system
* Implemented module-level log ownership
* Improved execution trace visibility
* Fixed hidden file handling in scanning logic
* Standardized workflow logging patterns

[v0.2.0]
* Implemented full scanning, classification, and file moving pipeline
* Introduced modular architecture with task-based structure
* Added prefixed folder system (smartorg-*)
* Implemented CLI routing system with task handlers

[v0.1.0]
* Initial project setup
* CLI skeleton
* Placeholder functions for future logic

---

## 7. 👤 Author


**46lemonlime**
GitHub: https://github.com/46lemonlime

Creator, developer, and maintainer of this project.
