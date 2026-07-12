# Smart File Organizer (v0.9.0)

A Python CLI application for deterministic file organization built around a contract-first architecture.

It automates file management workflows such as file sorting, dry-run simulation, and structured folder generation, with a focus on safety, configurability, and extensibility.

## 🚀 Quick Start

**Organize files**

```bash
python3 main.py move ~/Downloads
```

**Rollback latest execution**

```bash
python3 main.py rollback
```

**Safe simulation**

```bash
python3 main.py move ~/Downloads --dry-run
python3 main.py rollback --dry-run
```

**Browse report history**

```bash
python3 main.py report list
```

**View a report**

```bash
python3 main.py report
python3 main.py report 3
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
6. Captures operation-level results
7. Generates a structured report for every execution and rollback
8. Supports deterministic rollback of the latest execution

Execution and rollback reports preserve detailed discovery,
planning, mover, and rollback information, providing complete
operation traceability and allowing safe restoration of previous
executions.


The system prioritizes transparency, control, and reproducibility over raw automation speed.
```
Filesystem
      │
      ▼
Scanner
      │
      ▼
Filter
      │
      ▼
Classifier
      │
      ▼
Planner
      │
      ▼
Mover
```
---

## 2. ✨ Features
- Command-line interface with dedicated commands
   - move
   - rollback
   - report

- Config-driven behavior
   - YAML-based configuration
   - configurable classification rules
   - configurable folder naming

- File organization
   - deterministic execution planning
   - structured file classification
   - automatic folder organization

- Safe execution
   - dry-run simulation
   - per-file failure isolation
   - planning/execution separation

- Rollback
   - deterministic rollback planning
   - rollback dry-run
   - rollback execution
   - rollback report persistence

- Reporting
   - automatic execution reports
   - JSON report persistence
   - unified report history
   - report selection by index
   - report selection by identifier
   - report cleanup
   - application log cleanup
   - operation-level execution trace
   - discovery skipped-item reporting
   - planning skipped-operation reporting

- Observability
   - structured logging
   - centralized event taxonomy
   - execution summaries
   - end-to-end pipeline traceability

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

The project uses a centralized contracts package located under:

(`core/contracts/`)

The package provides a stable contract-first architecture through
a unified public API while internally organizing contracts by
functional domain.

Application modules should normally import contracts directly from:

```python
from core.contracts import ...
```

This keeps the import surface stable while allowing the internal
organization of the contracts package to evolve independently.

The contracts package is organized into the following domains:

- **configuration**
    - AppConfig
    - CategoryConfig

- **inventory**
    - DiscoveredItem
    - RawDiscoveryDataset
    - ClassifiedDiscovery
    - DiscoverySkippedItem
    - DiscoveryResult

- **operations**
    - ExecutionOperation
    - SkippedOperation
    - ExecutionPlan
    - ExecutionResult

- **recovery**
    - RollbackOperation
    - RollbackPlan
    - RollbackResult

- **records**
    - CategoryReport
    - DiscoveryReport
    - PlanningReport
    - MoverReport
    - ExecutionReport
    - RollbackReport
    - ReportHistoryItem

Shared validation helpers are provided by:

- **validation**
    - reusable contract validation utilities

This architecture:

- centralizes schema ownership
- reduces dynamic dictionary usage
- improves pipeline consistency
- strengthens type safety
- separates contract domains without exposing internal organization

### 🧹 Cleanup System

The cleanup subsystem manages application-generated persistence
artifacts.

| Component | Responsibility |
|---|---|
| cleaner.py | Delete reports and clear application logs |

### 📊 Reporting System

The reporting subsystem provides complete execution traceability
through persisted JSON reports.

Reports are generated automatically after every move and rollback
operation and can later be inspected through the CLI.

The subsystem is organized into independent components, each with
a single responsibility:

| Component | Responsibility |
|---|---|
| generator.py | Build report contracts |
| saver.py | Persist reports |
| loader.py | Load persisted reports |
| reporter.py | Render reports through the CLI |

#### Key capabilities
- automatic report generation
- execution and rollback reports
- chronological report history
- report selection by index
- report selection by identifier
- report cleanup
- application log cleanup

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
│
├── logs/
│   └── smartorg.log
│
├── reports/
│   ├── executions/
│   └── rollbacks/
│
├── cli/
│   └── parser.py
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
│   │   └── mover.py
│   │
│   ├── rollback/
│   │   ├── planner.py
│   │   ├── executor.py
│   │   └── coordinator.py
│   │
│   ├── reporting/
│   │   └── cleaner.py
│   │
│   └── reporting/
│       ├── generator.py
│       ├── saver.py
│       ├── loader.py
│       ├── cleaner.py
│       └── reporter.py
│
├── core/
│   ├── events.py
│   ├── metadata.py
│   └── contracts/
│        ├── validation.py
│        ├── configuration.py
│        ├── inventory.py
│        ├── operations.py
│        ├── recovery.py
│        └── records.py
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
parser.py
   ↓
main.py
   ↓
discovery/coordinator.py
   │
   ├── discovery/scanner.py
   ├── discovery/filter.py
   └── discovery/classifier.py
   ↓
execution/planner.py
   ↓
execution/mover.py
   ↓
Filesystem execution / Dry-run simulation
   ↓
reporting/generator.py
   ↓
reporting/saver.py
   ↓
ExecutionReport (.json)
```
#### rollback task
```
CLI Input
   ↓
parser.py
   ↓
main.py
   ↓
rollback/coordinator.py
   │
   ├── reporting/loader.py
   ├── rollback/planner.py
   └── rollback/executor.py
   ↓
Filesystem rollback / Dry-run simulation
   ↓
reporting/saver.py
   ↓
RollbackReport (.json)
   ↓
reporting/reporter.py
```

#### report task

```md
CLI input
 ↓
parser.py
 ↓
main.py
 ↓
Reporting subsystem
 ↓
CLI Output
```

---

## 4. 🧰 Usage & Execution

### ▶️ Command Reference

Run the application from the terminal using one of the available commands:

```bash
python3 main.py <command> [arguments]
```

#### Move

Organize the contents of a directory according to the configured
classification rules.

```bash
python3 main.py move /path/to/directory
```

Example:

```bash
python3 main.py move ~/Downloads
```


#### Move (Dry-run)

Simulate the organization process without modifying the filesystem.

```bash
python3 main.py move /path/to/directory --dry-run
```

Example:

```bash
python3 main.py move ~/Downloads --dry-run
```


#### Rollback

Restore the latest execution using the most recent execution report.

```bash
python3 main.py rollback
```

#### Rollback (Dry-run)

Simulate the rollback without modifying the filesystem.

```bash
python3 main.py rollback --dry-run
```

#### Report

Display the latest persisted report.

```bash
python3 main.py report
```

Browse report history.

```bash
python3 main.py report list
```

Display a report by index or identifier.

```bash
python3 main.py report 3
python3 main.py report 20260710T090146
```

Delete persisted reports.

```bash
python3 main.py report clear 3
python3 main.py report clear executions
python3 main.py report clear all
python3 main.py report clear logs
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

The configuration system is centralized through
`utils/config_loader.py`.

The loader:

- parses YAML
- validates configuration
- normalizes category definitions
- builds validated AppConfig and CategoryConfig contracts
- caches configuration
- provides safe fallback configuration

Downstream modules never access raw YAML directly.

### Key settings:

- folder_prefix → controls output folder naming  
- ignore_hidden_files → safe handling of system files  
- dry_run → default execution mode  
- categories → file classification rules  
- reports_directory → root report location
- execution_reports_directory → execution report storage
- rollback_reports_directory → rollback report storage


### Example

```yaml
folder_prefix: smartorg
ignore_hidden_files: true
ignore_symlinks: true
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
- Scalable contract-driven software architecture
- End-to-end execution traceability

### 📌 Development Principles

- Clean and maintainable architecture
- Config-driven behavior (no hardcoded rules)
- Controlled execution (dry-run support)
- Separation of concerns
- Contract-first architecture
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

#### Phase 8 - v0.8.0 Architecture Hardening & Extensibility

* [x] Layered discovery architecture
* [x] Coordinator-based discovery pipeline
* [x] Typed pipeline contracts
* [x] Contract-first architecture
* [x] Typed runtime configuration
* [x] Configuration authority layer
* [x] Discovery pipeline simplification
* [x] Reduced module coupling
* [x] Improved subsystem cohesion

#### Phase 9 - v0.9.0 Operational Maturity
* [x] Reporting subsystem
* [x] Reporting architecture
* [x] Configuration-driven report persistence
* [x] Rollback subsystem
* [x] Execution traceability
* [x] Observability improvements
* [x] CLI & developer experience
* [x] Report history
* [x] Report cleanup

#### Phase 10 - v1.0.0 Stable Release Preparation
* [ ] Code cleanup
* [ ] Architecture review and responsibility audit
* [ ] Performance and memory optimization
* [ ] Style cohesion and consistency
* [ ] Testing and stabilization
* [ ] Documentation review and synchronization

### 🚧 Current Limitations

- Additional report renderers not yet implemented
- Rollback currently restores only the latest execution
- No plugin-based classification system
- No AI-assisted file classification
- CLI only (no graphical interface)
- Report history currently supports local JSON persistence only
---

## 7. 📜 Version History

### v0.9.0

- Complete reporting subsystem
- Execution and rollback reports
- Automatic report generation and rendering
- Report history with chronological browsing
- Report loading by index or identifier
- Report cleanup and log cleanup commands
- Complete rollback subsystem
- Rollback planning and execution
- Rollback dry-run support
- Rollback report persistence
- Expanded execution traceability
- Improved CLI experience
- Configuration-driven report persistence
- Improved observability and event taxonomy

### v0.8.0

- Contract-first architecture
- Centralized typed contracts
- Typed runtime configuration
- Configuration authority layer
- Coordinator-based discovery pipeline
- Simplified filtering and classification
- Reduced runtime validation
- Improved module boundaries
- Improved architectural consistency
- Enhanced configuration observability

### v0.7.1
- discovery subsystem refactor
- layered discovery architecture introduced
- scanner/coordinator responsibility split
- typed dataclass contracts introduced
- execution contracts centralized in Core Contracts System
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


Designed and developed by **46lemonlime**
GitHub: https://github.com/46lemonlime

Built as a portfolio project focused on software architecture, maintainability and safe automation.
