# Smart File Organizer (v0.6.1)

A Python CLI tool that organizes files in a directory by scanning, classifying, and moving them into structured folders.

It automates file management workflows such as file sorting, dry-run preview execution, and structured folder generation, with a focus on safety, configurability, and future extensibility.

## 🚀 Quick Start
**Standard execution**
```bash
python3 main.py move ~/Downloads
```
**Dry-run (safe simulation)**
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

```md
module_action | key=value [key=value ...]
```

This design ensures:

- consistent debugging across the pipeline
- machine-readable logs for analysis and filtering
- clear separation of concerns between modules
- scalable observability for future system expansion

#### Example log format:
```md
scan_start | path=/Users/demo
scan_items | count=12
file_moved | file=test.txt destination=images
scan_error | reason=permission_denied path=/data
```
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


### ▶️ How to Use
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

#### Versioning Strategy (Semantic Versioning / SemVer)

x.y.z format:

- **x (major):** stable release milestones  
- **y (minor):** phase-based development progression  
- **z (patch):** hotfixes and small improvements  

Each major phase maps directly to a version (e.g. Phase 6 → v0.6.0).  
v0.4.0 and v0.5.0 were internal iterations merged into adjacent releases for version alignment.


#### Phase 1 - v0.1.0 Initial Setup
 * [x] CLI interface (basic skeleton)
 * [x] Project structure setup

#### Phase 2 - v0.2.0 Core Automation
 * [x] Directory scanning
 * [x] File classification (by type)
 * [x] File moving / organization (smartorg-* folders)
 * [x] Basic task routing system

#### Phase 3 - v0.3.0 Stability & Observability
* [x] Core scanning and classification pipeline
* [x] File moving engine (initial version)
* [x] Structured logging system
* [x] Module-based log ownership
* [x] Execution trace improvements
* [x] Hidden file filtering
* [x] Logging format foundation (key=value structured contract)

#### Phase 6 - v0.6.0 Execution Safety Layer
* [x] Config system (YAML-driven rules)
* [x] Config caching layer
* [x] Classification rules externalized
* [x] Prefix configuration system
* [x] Dry-run mode (simulation execution)
* [x] CLI override (--dry-run)
* [x] Move summary logs
* [x] Logging consistency improvements
* [x] Config validation (basic YAML safety checks)
* [x] Controlled execution architecture

#### Phase 7 - v0.7.0 Reliability & Edge Case Hardening
* [ ] Improve error handling consistency across failure points (standardize patterns, not add new ones)
* [ ] Strengthen file operation resilience (partial failure recovery, safer rollback behavior)
* [ ] Improve classification edge-case handling (empty dirs, unusual file extensions)
* [ ] Validate dry-run parity with real execution behavior
* [ ] Improve logging clarity for failure scenarios (reduce ambiguity, not restructure system)

#### Phase 8 - v0.8.0 Architecture Refinement
* [ ] Refactor scanner/mover boundary for cleaner separation (reduce implicit coupling)
* [ ] Improve config schema scalability (preparing for future expansion, not core changes)
* [ ] Remove remaining redundant checks and legacy defensive logic
* [ ] Improve internal module cohesion and responsibility clarity
* [ ] Minor performance improvements in directory scanning

#### Phase 9 - v0.9.0 Polish & Developer Experience
* [ ] Improve CLI usability (help text clarity and consistency)
* [ ] Final documentation refinement pass (README + examples + structure)
* [ ] Logging readability improvements (minor tweaks, no structural changes)
* [ ] Full edge-case testing and stabilization pass
* [ ] Pre-release bug fixing and behavioral consistency audit

#### Phase 10 - v1.0.0 Stable Release
* [ ] Fully stable and production-ready execution pipeline
* [ ] Fully validated config-driven system
* [ ] Complete dry-run safety guarantees
* [ ] Fully consistent logging and observability layer
* [ ] Clean, documented, portfolio-ready architecture
* [ ] Final cleanup of development artifacts and temporary logic

### 🚧 Current Limitations

- No undo / rollback system
- No operation history tracking
- No GUI or dashboard interface
- No advanced classification intelligence
- No plugin system
---

## 7. 📜 Version History
### v0.6.1
- README improvements and formatting fixes
- Logging documentation consistency

### v0.6.0
- Config-driven architecture (YAML-based)
- Config loader with caching and validation
- Classification rules externalized
- Prefix configuration system
- Dry-run execution system (full pipeline)
- CLI override for execution control (`--dry-run`)
- File sorting and moving refactored for config
- Logging system standardized across modules
- Structured logging format enforced (key=value)
- Move summary logs (total + per-category)
- Logging consistency improvements
- Controlled execution architecture

### v0.3.0
- Core scanning and classification pipeline
- Initial file moving engine
- Structured logging system
- Module-based log ownership
- Execution trace improvements
- Hidden file filtering
- Logging format foundation (key=value)

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
