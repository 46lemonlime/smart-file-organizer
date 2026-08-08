# Smart File Organizer (v1.0.0)

A Python CLI application for deterministic file organization built around a contract-first architecture.

It automates file management workflows such as file sorting, dry-run simulation, and structured folder generation, with a focus on safety, configurability, and extensibility.

## 🚀 Quick Start

Get up and running in three steps.

**1. Clone and install**

```bash
git clone https://github.com/46lemonlime/smart-file-organizer.git
cd smart-file-organizer
pip install .
```

**2. Initialize**

Creates the application directory, default configuration, and report storage under `~/smartorg/`.

```bash
smartorg init
```

**3. Organize a directory**

Preview the changes first with a dry-run, then run it for real.

```bash
smartorg move ~/Downloads --dry-run
smartorg move ~/Downloads
```

Made a mistake, or just want to undo the last run?

```bash
smartorg rollback
```

**Requirements:** Python 3.10+

For the full command reference (report history, cleanup, scoped filters, and more), see [Usage & Execution](#4--usage--execution).

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
```md
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
   - init
   - move
   - rollback
   - report
   - cleanup

- Application initialization
   - application-owned directory structure under `~/smartorg/`
   - idempotent initialization
   - default configuration generation

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
   - chronological report history
   - scoped report history filtering
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

- Packaging
   - installable Python package
   - `smartorg` terminal command via console entry point

---

## 3. 🧱 Architecture (Design & Structure)
### 🏛️ Design Principles
- Separation of concerns
- Config-driven architecture
- Deterministic execution pipeline
- Modular responsibilities per file
- CLI-first design
- Structured log-based observability
- Application-owned infrastructure, independent of user configuration

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

## 🛠️ Application Paths & Initialization

All persistent application data is stored under a single
application-owned directory:

```md
~/smartorg/
├── config.yaml
├── logs/
│ └── smartorg.log
└── reports/
├── executions/
└── rollbacks/
```
This location is centrally defined in `core/paths.py`, which acts
as the single source of truth for every application-owned path.
No other module constructs or infers these paths independently.

`smartorg init` creates this structure and a default
configuration file. It is idempotent: running it against an
already-initialized installation leaves existing directories and
configuration untouched.

Every command other than `init` requires an initialized
application directory. Attempting to run `move`, `report`,
`rollback`, or `cleanup` before initialization prints guidance
instead of failing with a filesystem error.

### 🧹 Cleanup System

The cleanup subsystem manages application-generated persistence
artifacts.

| Component | Responsibility |
|---|---|
| cleaner.py | Delete persisted reports and clear application logs |

#### Key capabilities
- report deletion by index
- report deletion by identifier
- scoped report cleanup
- application log cleanup
- complete persistence cleanup

### 📊 Reporting System

The reporting subsystem provides complete execution traceability
through persisted JSON reports.

Reports are generated automatically after every move and rollback
operation and can later be inspected through the CLI.

The subsystem is organized into independent components, each with
a single responsibility:

| Module | Responsibility |
|---|---|
| `generator.py` | Build new execution and rollback reports |
| `reporter.py` | Persist and present generated reports |
| `storage.py` | Discover report files and read persisted JSON |
| `deserializer.py` | Reconstruct report contracts from persisted data |
| `history.py` | Build, sort, filter, and resolve report history |
| `loader.py` | Coordinate persisted report loading |

#### Key capabilities
- automatic report generation
- execution and rollback reports
- chronological report history
- report selection by index
- report selection by identifier

### 🔎 Logging System

The project uses a structured logging system across all modules.

```md
module_action | key=value [key=value ...]
```

Static logging paths and filenames are centrally managed by
`core/paths.py`, allowing the logging infrastructure to operate
independently from runtime configuration loading.

**Design guarantees:**
- consistent debugging across the full pipeline
- machine-readable logs for filtering and analysis
- consistent operational traceability
- centralized logging path ownership
- scalable observability for future system expansion
- consistent failure diagnostics across modules
- clean separation of concerns between scanning, planning, and execution layers
- millisecond-precision timestamps

#### Field Naming Consistency

| Field | Meaning |
|---|---|
| path | Generic filesystem path |
| source_path | Original file location |
| destination_path | Target file location |
| file | Filename only |
| reason | Machine-readable failure reason |

**Avoid inconsistent aliases such as:**
- src
- dest
- filepath
- target

### 📁 Project Structure

```md
mart-file-organizer/
│
├── pyproject.toml
├── LICENSE
├── main.py
├── config.yaml
├── requirements.txt
│
├── cli/
│ └── parser.py
│
├── core/
│ ├── events.py
│ ├── metadata.py
│ ├── paths.py
│ └── contracts/
│ ├── validation.py
│ ├── configuration.py
│ ├── inventory.py
│ ├── operations.py
│ ├── recovery.py
│ └── records.py
│
├── handlers/
│ ├── cleanup.py
│ ├── init.py
│ ├── move.py
│ ├── report.py
│ └── rollback.py
│
├── tasks/
│ ├── bootstrap/
│ │ ├── initializer.py
│ │ └── verifier.py
│ │
│ ├── discovery/
│ │ ├── scanner.py
│ │ ├── filter.py
│ │ ├── classifier.py
│ │ └── coordinator.py
│ │
│ ├── execution/
│ │ ├── planner.py
│ │ └── mover.py
│ │
│ ├── rollback/
│ │ ├── planner.py
│ │ ├── executor.py
│ │ └── coordinator.py
│ │
│ ├── cleanup/
│ │ └── cleaner.py
│ │
│ └── reporting/
│ ├── deserializer.py
│ ├── generator.py
│ ├── history.py
│ ├── loader.py
│ ├── reporter.py
│ ├── saver.py
│ └── storage.py
│
├── utils/
│ ├── logger.py
│ └── config_loader.py
│
└── README.md
```

Application-owned runtime data (`config.yaml`, `logs/`, `reports/`)
is created separately under `~/smartorg/` by `smartorg init` and
is not part of the project's source tree.

### 🏛️ Application Architecture

```md
CLI
    ↓
Application Handlers
    ↓
Task Subsystems
    ↓
Core Contracts & Infrastructure
```

The application is organized into distinct architectural layers.

- cli/ defines and validates the command-line interface.
- handlers/ coordinate application workflows.
- tasks/ implement specialized subsystem behavior, including
  application bootstrap (tasks/bootstrap/).
- core/ centralizes shared contracts, events, metadata and application paths.
- utils/ provides reusable infrastructure services.

This layered architecture keeps orchestration independent from subsystem implementation while maintaining clear ownership boundaries.

### 🔄 Data Flow

#### init task

```md
CLI Input
    │
    ▼
cli/parser.py
    │
    ▼
main.py
    │
    ▼
handlers/
    │
    ▼
tasks/bootstrap/
    │
    ├── verify initialization state
    ├── create application directories
    └── create default configuration
```

#### move task

```md
CLI Input
    │
    ▼
cli/parser.py
    │
    ▼
main.py
    │
    ▼
handlers/
    │
    ▼
tasks/discovery/
    │
    ▼
tasks/execution/
    │
    ▼
tasks/reporting/
```
#### rollback task

```md
CLI Input
    │
    ▼
cli/parser.py
    │
    ▼
main.py
    │
    ▼
handlers/
    │
    ▼
tasks/rollback/
    │
    ▼
tasks/reporting/
```

#### report task

```md
CLI Input
    │
    ▼
cli/parser.py
    │
    ▼
main.py
    │
    ▼
handlers/
    │
    ▼
tasks/reporting/
    │
    ├── load report history
    ├── resolve report reference
    └── render CLI output
```

#### Cleanup task
```md
CLI Input
    │
    ▼
cli/parser.py
    │
    ▼
main.py
    │
    ▼
handlers/
    │
    ▼
tasks/cleanup/
    │
    ├── delete report by reference
    ├── delete reports by scope
    └── clear application logs
```

---

---

## 4. 🧰 Usage & Execution

### ▶️ Command Reference

Run the application from the terminal using the installed `smartorg` command:

```bash
smartorg <command> [arguments]
```

During development, or without installing the package, the
application can also be run directly:

```bash
python3 main.py <command> [arguments]
```

#### Init

Initialize the SmartOrg application directory and default
configuration under `~/smartorg/`.

```bash
smartorg init
```

Running `init` against an already-initialized installation is
safe and leaves existing directories and configuration untouched.

#### Move

Organize the contents of a directory according to the configured
classification rules.

```bash
smartorg move /path/to/directory
```

Example:

```bash
smartorg move ~/Downloads
```

**Move (Dry-run)**

Simulate the organization process without modifying the filesystem.

```bash
smartorg move /path/to/directory --dry-run
```

Example:

```bash
smartorg move ~/Downloads --dry-run
```

#### Rollback

Restore the latest execution using the most recent execution report.

```bash
smartorg rollback
```

**Rollback (Dry-run)**

Simulate the rollback without modifying the filesystem.

```bash
smartorg rollback --dry-run
```

#### Report

Display the latest persisted execution report.

```bash
smartorg report
```

Browse the unified report history.

```bash
smartorg report list
```

Filter the report history by workflow.

```bash
smartorg report list executions
smartorg report list rollbacks
```

Display a persisted report by history index or identifier.

```bash
smartorg report 3
smartorg report 20260710T090146
```

#### Cleanup

Delete persisted reports by history index or identifier.

```bash
smartorg cleanup report 3
smartorg cleanup report 20260710T090146
```

Delete groups of persisted reports.

```bash
smartorg cleanup report executions
smartorg cleanup report rollbacks
smartorg cleanup report all
```

Clear the application log.

```bash
smartorg cleanup log
```

Remove all persisted reports and application logs.

```bash
smartorg cleanup all
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

Configuration is loaded from `~/smartorg/config.yaml`, created by
`smartorg init`. Application-owned paths (logs, reports) are not
part of this file — they are defined exclusively in
`core/paths.py`.

### Key settings:

- folder_prefix → controls output folder naming
- ignore_hidden_files → safe handling of system files
- dry_run → default execution mode
- categories → file classification rules

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
- Safe and deterministic execution systems
- Modular design
- Real-world file system automation
- Scalable contract-driven software architecture
- End-to-end execution traceability
- Distributable Python packaging

### 📌 Development Principles

- Clean and maintainable architecture
- Config-driven behavior (no hardcoded rules)
- Controlled execution (dry-run support)
- Separation of concerns
- Contract-first architecture
- Observable and deterministic system behavior through structured logs
- Application-owned infrastructure, independent of user configuration

### 🧭 Roadmap

#### Versioning Strategy (Semantic Versioning / SemVer)

Version numbers follow the **x.y.z** format:

- **x (major):** stable release milestones
- **y (minor):** feature and development milestones
- **z (patch):** bug fixes and small improvements


#### v1.0.0 — Project Stabilization (latest stable release)

* [x] Architecture review
* [x] Cleanup command architecture
* [x] Handler modularization
* [x] Contract package modularization
* [x] Core path centralization
* [x] Application-owned path relocation (`~/smartorg/`)
* [x] Application initialization (`smartorg init`)
* [x] Workflow event taxonomy centralization
* [x] CLI refinements
* [x] Manual workflow validation
* [x] Final code cleanup
* [x] Packaging & distribution (`smartorg` terminal command)

#### v1.1.0+ — Future Releases

* [ ] Automated testing infrastructure
* [ ] Terminal autocompletion
* [ ] Extended rollback (environment restoration, including
      removal of empty directories created by the original
      execution)
* [ ] Graphical user interface (GUI)


### 🚧 Current Limitations

- Additional report renderers not yet implemented
- Rollback currently restores only the latest execution
- Rollback does not remove directories created by the original
  execution, even when left empty
- No plugin-based classification system
- No AI-assisted file classification
- CLI only (no graphical interface)
- Report history currently supports local JSON persistence only
---

## 7. 📜 Version History

Versions **v0.4.0** and **v0.5.0** were internal development iterations merged into adjacent releases to maintain a cleaner version history.

### v1.0.0

- Completed architecture review and responsibility audit
- Consolidated `main.py` as the application Composition Root
- Extracted application handlers from `main.py`
- Segregated handlers into dedicated workflow modules
- Introduced standalone cleanup command
- Introduced dedicated cleanup subsystem
- Simplified report command architecture
- Reviewed reporting loader architecture
- Modularized the core contracts package
- Centralized reusable contract validation utilities
- Centralized static application paths in `core/paths.py`
- Relocated all application-owned data under `~/smartorg/`
- Removed report path configuration from `config.yaml` and `AppConfig`
- Introduced the `tasks/bootstrap` subsystem
- Introduced the `smartorg init` command (idempotent)
- Introduced a centralized application-initialization guard in `main.py`
- Migrated `tasks/reporting/storage.py` from `os.path` to `pathlib`
- Centralized workflow event taxonomy
- Removed duplicated logging path constants
- Removed obsolete subsystem imports
- Removed obsolete handler implementation
- Removed obsolete metadata registry
- Removed dead code (`build_reports_directory`)
- Added scoped report history filtering
- Improved CLI consistency and command ergonomics
- Reviewed configuration loader responsibilities
- Reviewed execution mover responsibilities
- Reviewed rollback planner responsibilities
- Reviewed rollback executor responsibilities
- Confirmed separation between execution and rollback contracts
- Standardized execution and rollback operation semantics
- Improved source validation in filesystem move execution
- Standardized rollback runtime failure events
- Standardized rollback dry-run simulation events
- Fixed an obsolete report-saving call signature in the move handler
- Fixed report history construction silently failing due to a
  `Path`/`str` contract mismatch in `ReportHistoryItem`
- Added `validate_path_type` to the shared contract validation module
- Validated missing-source execution behavior
- Validated prevention of unnecessary destination directory creation
- Validated rollback missing-source handling
- Validated rollback destination-conflict handling
- Validated rollback dry-run behavior
- Validated rollback path inversion
- Validated dry-run execution end-to-end
- Validated live execution end-to-end
- Validated report persistence and loading
- Validated live rollback end-to-end
- Validated cleanup workflows (by index, by scope, log, all)
- Completed project-wide compilation validation
- Synchronized architecture and Composition Root documentation
- Completed project-wide performance and memory audit
- Optimized filesystem traversal using os.scandir where appropriate
- Introduced constant-time extension classification
- Optimized report history reconstruction
- Optimized report storage discovery
- Improved structured logging performance
- Increased log timestamp precision to milliseconds
- Reviewed configuration loader performance
- Reviewed application composition-root performance
- Packaged the project for distribution via `pyproject.toml`
- Exposed the `smartorg` terminal command
- Added MIT `LICENSE`
- Verified installation end-to-end in a clean virtual environment

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
GitHub: [46lemonlime](https://github.com/46lemonlime)

Built as a portfolio project focused on software architecture, 
maintainability and safe automation.