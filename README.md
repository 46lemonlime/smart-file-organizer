# smart-file-organizer
Creating a file organiser bot that also creates reports and logs about organised files

smart-file-organizer
│
├── main.py                 # Entry point (CLI interface)
├── config.yaml             # Configurable rules (file types, defaults)
├── logger.py               # Logging setup
│
├── tasks/
│   ├── file_sorter.py      # Core logic: scan, classify, move files
│   ├── report_generator.py # Generates summary after execution
│
├── utils/
│   ├── helpers.py          # Shared helpers (validation, file utils)
│   ├── config_loader.py    # Loads and parses config.yaml
│
├── logs/
│   └── app.log             # Execution logs
│
├── reports/                # (NEW) store generated reports
│   └── .gitkeep
│
├── requirements.txt
└── README.md

🧠What Each Part Is Responsible For
main.py
- CLI interface (--task, --path, optional flags)
- Controls flow:
    - validate input
    - call sorter
    - call report generator

👉 Think: orchestrator, not logic-heavy

config.yaml

This is where your project becomes reusable.

You should define things like:

File categories (images, docs, etc.)
Default path (optional fallback)
Maybe ignore folders

👉 No hardcoding in your logic files

tasks/file_sorter.py

Core engine of your project:

Responsibilities:

Scan directory
Classify files
Move them
Track stats (for report)

👉 This is where most of your logic lives

tasks/report_generator.py

Takes execution results and produces:

Simple summary (txt or csv)
Possibly timestamped file

👉 Important for “real-world tool” feeling

logger.py

Centralized logging:

Info (what happened)
Errors (what failed)

👉 Makes your project feel professional instantly

utils/helpers.py

Reusable utilities:

Path validation
File extension extraction
Safe file moving (handle duplicates)

👉 Prevents duplication and messy code

utils/config_loader.py (NEW but important)
Loads YAML config
Returns structured data

👉 Keeps config logic separated (clean architecture)

logs/ + reports/
logs/ → debugging / technical trace
reports/ → user-friendly output

👉 This separation is subtle but very professional

⚠️ Small But Important Improvements
1. Avoid re-processing folders

Your sorter should ignore:

images/
documents/
reports/
logs/
2. Think about naming consistency

Keep naming predictable:

file_sorter
report_generator
not mixed styles like fileSorter / reportGen
3. Keep responsibilities strict

Don’t let:

file_sorter generate reports
main.py contain logic

👉 separation = clean code

🏷️ Repository Name Ideas

You want something:

Clear
Slightly branded
Not generic like “python-script”

Here are strong options depending on style:

🔹 Clean & Professional (recommended)
smart-file-organizer
auto-file-organizer
file-automation-tool
cli-file-organizer
file-organizer-bot

👉 Best choice:
smart-file-organizer (clear + slightly elevated)

🔹 More “Product-like”
FilePilot
Sortify
FileFlow
AutoSort
FolderBot

👉 These are cooler, but slightly less descriptive

🔹 Portfolio-Optimized (VERY good for recruiters)
python-file-automation
task-automation-bot
file-organizer-cli

👉 Best balance:
file-organizer-cli

🔥 My Recommendation

If your goal is getting hired:

👉 Go with:
smart-file-organizer

If your goal is showing Python + CLI skills clearly:

👉 Go with:
file-organizer-cli

🚀 Final Thought

Right now your project has:

✔ Real-world use case
✔ CLI interaction
✔ Config-driven behavior
✔ Logging + reporting
✔ Clean modular structure

That’s already stronger than 90% of beginner GitHub projects.

If you want next step, I can:

Help you define a clean config.yaml (categories + structure)
Or 
give you a step-by-step implementation order (what to build first, second, etc.)