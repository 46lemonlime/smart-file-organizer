# Smart File Organizer (v0.7.1)

A Python CLI tool that organizes files in a directory by scanning, classifying, planning, and executing structured file movements.

It automates file management workflows such as file sorting, dry-run simulation, and structured folder generation, with a focus on safety, configurability, and extensibility.

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

It follows a config-driven and deterministic execution design:

1. Scans a target folder
2. Filters unwanted items
3. Classifies files using configurable rules
4. Builds a deterministic execution plan
5. Executes or simulates file system operations
6. Logs structured execution traces for observability and debugging

The system prioritizes transparency, control, and reproducibility over raw automation speed.

---

## 2. ✨ Features
- CLI-based interface for task execution
- Config-driven system (config.yaml)
- Modular pipeline architecture
- Deterministic execution planning layer
- Dry-run simulation mode
- Defensive file system execution engine
- Structured file classification system
- Folder prefix-based organization system (smartorg-*)
- Core Modules:
   - discovery/scanner.py → raw filesystem discovery
   - discovery/filter.py → skip/filter rules engine
   - discovery/classifier.py → config-driven classification
   - discovery/coordinator.py → discovery pipeline orchestration
   - execution/planner.py → deterministic execution planning
   - execution/executor.py → filesystem execution layer
   - reporting/reporter.py → future reporting subsystem
   - contracts.py → shared typed pipeline contracts
- Configuration System
   - folder prefix control
   - hidden file handling
   - classification rules (YAML-driven)
- Execution Safety
   - Dry-run mode for safe previews
   - Strict separation of planning vs execution
   - Failure isolation per file operation
- Observability System
   - Structured logging (key=value format)
   - Execution traceability across all modules
   - Move summary logs (total + per-category breakdown)
   - Failure visibility with structured metadata
   - Optional execution tracing enhancements:
      - op_id tracking
      - total_failed tracking
- Typed dataclass-based pipeline contracts
- Discovery/execution layered architecture
- Coordinator-based discovery pipeline
---

## 3. 🧱 Architecture (Design & Structure)
### 🏛️ Design Principles
- Separation of concerns
- Config-driven architecture
- Deterministic execution pipeline
- Modular responsibilities per file
- CLI-first design
- Structured log-based observability

### 🧩 Contracts System

The project uses centralized typed contracts (`contracts.py`)
to define stable inter-module structures.

These contracts:
- reduce dynamic dictionary usage
- improve pipeline consistency
- strengthen type safety
- centralize schema ownership

Current contracts include:
- DiscoveredItem
- ClassifiedDiscovery
- ExecutionOperation
- ExecutionPlan
- SkippedOperation

### 🔎 Logging System (Observability Design)

The project uses a structured logging system across all modules.

```md
module_action | key=value [key=value ...]
```

- Design guarantees:
   - consistent debugging across the full pipeline
   - machine-readable logs for filtering and analysis
   - consistent operational traceability
   - scalable observability for future system expansion
   - consistent failure diagnostics across modules
   - clean separation of concerns between scanning, planning, and execution layers



#### Field Naming Consistency
| Field | Meaning |
|---|---|
|path	| Generic filesystem path|
|source_path | Original file location|
|destination_path | Target file location|
|file	| Filename only|
|reason	| Machine-readable failure reason|

**Avoid inconsistent aliases such as:**
- src
- dest
- filepath
- target

### 📁 Project Structure

```
smart-file-organizer/
│
├── main.py
├── config.yaml
├── contracts.py
│
├── logs/
│   └── smartorg.log
│
├── tasks/
│   ├── discovery/
│   │   ├── scanner.py
│   │   ├── filter.py
│   │   ├── classifier.py
│   │   └── coordinator.py
│   │
│   ├── execution/
│   │   ├── planner.py
│   │   └── executor.py
│   │
│   └── reporting/
│       └── reporter.py
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
main.py
   ↓
discovery/coordinator.py
   ↓
discovery/scanner.py
   ↓
discovery/filter.py
   ↓
discovery/classifier.py
   ↓
execution/planner.py
   ↓
execution/executor.py
   ↓
Filesystem changes OR dry-run simulation
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
* [x] Standardize error handling across modules (consistent log_error structure)
* [x] Improve file operation resilience (per-file isolation, safe continuation)
* [x] Handle classification edge cases (empty dirs, bad extensions, invalid inputs)
* [x] Validate dry-run parity vs real execution (logic identical, only FS differs)
* [x] Improve failure log clarity (structured, non-ambiguous messages)
* [x] Refactor pipeline architecture (scanner → filter → classify → plan → move)
* [x] Add execution planner layer (deterministic plan generation)
* [x] Enforce execution-only mover (no decision logic in file_mover)
* [x] Harden config edge cases (YAML safety, missing keys, defaults)
* [x] Improve observability (structured logs, op_id, total_failed)
* [x] Ensure full traceability (end-to-end structured logging)

#### Phase 8 - v0.8.0 Observability & Architecture Refinement
* [ ] Build reporting system foundation (deterministic execution reports)
* [ ] Improve execution contract validation
* [ ] Reduce module coupling
* [ ] Improve module cohesion
* [ ] Optimize directory scanning
* [ ] Add global event schema layer
* [ ] Unify error taxonomy
* [ ] Improve op_id propagation
* [ ] Standardize warning severity levels
* [ ] Remove redundant defensive checks

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

### v0.7.1
- discovery subsystem refactor
- layered discovery architecture introduced
- scanner/coordinator responsibility split
- typed dataclass contracts introduced
- execution contracts centralized in contracts.py
- typed execution pipeline contracts
- improved architectural separation of concerns
- reduced module coupling
- improved pipeline readability and maintainability

### v0.7.0
- full pipeline refactor (scanner → planner → mover)
- execution planner introduced
- structured logging standardization
- resilience improvements
- per-operation failure isolation (no rollback)
- deterministic execution planning (filesystem-dependent execution phase)
- config edge-case hardening
- observability enhancements (op_id, total_failed)

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
