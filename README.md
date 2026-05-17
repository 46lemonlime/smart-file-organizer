# Smart File Organizer (v0.6.0)

A Python CLI tool that organizes files in a directory by scanning, classifying, and moving them into structured folders.

It automates file management tasks such as sorting files by type, previewing changes before execution (dry-run mode), and preparing structured outputs for future automation features.

## 🚀 Quick Start
###### Standard execution
```bash
python3 main.py move ~/Downloads
```
###### Dry-run (safe simulation)
```bash
python3 main.py move ~/Downloads --dry-run
```
---

## 1. 🧠 Project Overview

Smart File Organizer is a lightweight CLI automation engine for cleaning and structuring directories such as Downloads or Desktop.

It follows a config-driven and controlled execution design:

1. Scans a target folder  
2. Classifies files using configurable rules
3. Simulates or executes file organization
4. Logs structured execution summaries for observability and debugging

The tool prioritizes transparency, control, and extensibility over raw automation speed.

---

## 2. ✨ Features
- CLI-based interface for task execution  
- Config-driven system (`config.yaml`)  
- Directory scanning and file detection  
- File classification system (fully configurable)  
- Automated folder creation with prefix system  
- Structured file moving engine  
- Prefixed folder structure (`smartorg-*`)  
- Modular architecture with clear separation of concerns:

  - `file_sorter.py` → scanning & classification  
  - `file_mover.py` → file system operations  
  - `report_generator.py` → placeholder (future feature)

- Configuration system:
  - folder prefix control
  - hidden file handling
  - classification rules (YAML-driven)

- Execution safety features:
  - Dry-run mode for execution preview
  - CLI override support

- Observability system:
  - Structured logging (key=value format for machine readability)
  - Move summary logs (total + per-category breakdown)

- Task-based routing system via main.py  
- Cross-platform design (macOS / Windows compatible)

---

## 3. 🧱 Architecture (Design & Structure)
### 🧩 Design Principles
- Separation of concerns
- Config-driven architecture (no hardcoded rules)
- Predictable and controlled execution
- Modular responsibilities per file
- CLI-first design
- Observability through structured logs

### 🔎 Logging System (Observability Design)

The project uses a structured logging format across all modules:

module_action | key=value

This design ensures:

- consistent debugging across the pipeline
- machine-readable logs for analysis and filtering
- clear separation of concerns between modules
- scalable observability for future system expansion

#### Example log format:

scan_start | path=/Users/demo
scan_items | count=12
file_moved | file=test.txt destination=images
scan_error | reason=permission_denied path=/data

### 📁 Project Structure

```
smart-file-organizer/
│
├── main.py
├── config.yaml
├── logs/
│   └── smartorg.log
│
├── tasks/
│   ├── file_sorter.py
│   ├── file_mover.py
│   ├── report_generator.py (placeholder)
│
├── utils/
│   ├── logger.py
│   └── config_loader.py
│
├── README.md
└── requirements.txt
```

### 🔄 Data Flow

#### move task

```md
CLI Input
   ↓
main.py (orchestration layer)
   ↓
scan_and_classify() → config-driven classification system
   ↓
move_files() → dry-run aware execution engine
   ↓
File system organized OR safely simulated
```

#### report task

```md
CLI Input
   ↓
main.py
   ↓
generate_report()
   ↓
Report output generated (future expansion area)
```

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
## 5. ⚙️ Configuration System

This project is now fully config-driven via `config.yaml`.

### Key settings:

- folder_prefix → controls output folder naming  
- ignore_hidden_files → safe handling of system files  
- dry_run → default execution mode  
- categories → file classification rules  


### Example

```yaml
folder_prefix: smartorg
ignore_hidden_files: true
dry_run: false

categories:
  images:
    description: "Image files"
    extensions: [.png, .jpg]
```
---
## 6. 🧪 Development Overview

### 🎯 Project Intent

Smart File Organizer is a portfolio-grade automation engine demonstrating:

- Python CLI design
- Config-driven architecture
- Safe execution systems
- Modular design
- Real-world file system automation

### 📌 Development Principles

- Clean and maintainable architecture
- Config-driven behavior (no hardcoded rules)
- Controlled execution (dry-run support)
- Separation of concerns
- Observable system behavior through structured logs

### 🧭 Roadmap
> Versioning follows project phases.  
> Each major phase maps directly to a version (e.g. Phase 6 → v0.6.0).
> v0.4.0 & v0.5.0 are intermediate versions that were skipped intentionally to maintain alignment.

#### v0.1.0 (Initial Setup)
 * [x] CLI interface (basic skeleton)
 * [x] Project structure setup

#### v0.2.0 (Core Automation)
 * [x] Directory scanning
 * [x] File classification (by type)
 * [x] File moving / organization (smartorg-* folders)
 * [x] Basic task routing system

#### v0.3.0 (Stability & Observability)
* [x] Structured logging system
* [x] Module-based log ownership
* [x] Execution trace improvements
* [x] Hidden file filtering

#### v0.4.0 — Configuration Layer
* [x] Config system (YAML-driven rules)
* [x] Classification rules externalized
* [x] Prefix configuration
* [x] Hidden file handling
* [x] Config caching

#### v0.6.0 — Execution Safety Layer (CURRENT)
* [x] Dry-run mode (simulation execution)
* [x] CLI override (--dry-run)
* [x] Controlled execution architecture
* [x] Move summary logs
* [x] Logging consistency improvements

#### v1.0.0 (Stable Release)
 * [ ] Full configuration system
 * [ ] Undo + recovery system
 * [ ] Robust safety controls
 * [ ] Fully documented CLI tool
 * [ ] Production-ready structure

### 🚧 Current Limitations (v0.6.0)

- No undo / rollback system
- No operation history tracking
- No GUI or dashboard interface
- No advanced classification intelligence
- No plugin system
---

## 7. 📜 Version History
### v0.6.0 (Current)
- Config-driven architecture implemented
- Dry-run execution system added
- CLI override for safe execution introduced
- File sorting and moving engines refactored
- Logging system standardized
- Move summary logs added
- Config caching implemented

### v0.3.0
- Structured logging system
- Module-level log ownership
- Execution trace improvements
- Hidden file filtering

### v0.2.0
- Core scanning, classification, and moving system
- Modular architecture introduced
- CLI routing system

### v0.1.0
- Initial CLI skeleton
- Basic project setup

---

## 8. 👤 Author


**46lemonlime**
GitHub: https://github.com/46lemonlime

Creator, developer, and maintainer of this project.
