# Smart File Organizer (v0.2.0)

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
* Task-based routing system via `main.py`  
* Cross-platform design (macOS / Windows compatible)

---

## 3. 🧱 Architecture (Design & Structure)
### 🧩 Design Principles
* Separation of concerns
* Modular architecture
* CLI-first design
* Cross-platform compatibility (macOS & Windows)
* Safe filesystem operations (basic validation)

### 📁 Project Structure

```
smart-file-organizer/
│
├── main.py
├── config.yaml (future)
├── logs/ (future)
│
├── tasks/
│ ├── file_sorter.py
│ ├── file_mover.py
│ ├── report_generator.py (placeholder for the moment)
│
├── utils/ (future)
├── README.md
└── requirements.txt
```

### 🔄 Data Flow

#### move task

```md
CLI Input
   ↓
main.py (router)
   ↓
scan_and_classify()
   ↓
move_files()
   ↓
File system organization applied
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
- Modular and scalable architecture
- Real-world usability for personal file management
- Incremental development with stable milestones
- Future-proof design for configuration and extensibility

### 🧭 Roadmap

#### v0.1.0 (Initial Setup)
 * [x] CLI interface (basic skeleton)
 * [x] Project structure setup

#### v0.2.0 (Current - Core Automation)
 * [x] Directory scanning
 * [x] File classification (by type)
 * [x] File moving / organization (smartorg-* folders)
 * [x] Basic task routing system

#### v0.3.0 (Stability & Observability)
 * [ ] Logging system (track actions and errors)
 * [ ] Improved CLI output formatting
 * [ ] Better error handling and validation

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

### 🚧 Current Limitations (v0.2.0)

- No configuration file (settings are currently hardcoded)
- No dry-run mode
- No logging system
- No undo functionality
- Limited file type classification rules
- Report generator not implemented yet
---

## 6. 📜 Version History
[v0.2.0] - Current
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

