# Safe Photo Organizer

Safe Photo Organizer is a local Windows web application for organizing image and video collections without modifying original source files.

The application scans a selected source folder recursively, detects media dates using evidence from filenames and metadata, builds a reviewable plan, and copies verified files into date-based folders while preserving the existing folder hierarchy.

## Developer

Udara Irunika

  <img width="460" height="460" alt="119570415" src="https://github.com/user-attachments/assets/93c92a1a-82ae-4d59-9ed0-47653c8bcb11" />

- Portfolio: https://udarairunika.com/
- Company: https://uiddevelopers.com/
- WhatsApp: https://wa.me/94764353012

## Main Features

- Local-only processing. Photos are not uploaded to a cloud service.
- Recursive source-folder scanning.
- Preservation of existing source folders and subfolders.
- Date-folder exclusion to prevent repeated reorganization.
- Evidence-based date detection.
- Filename date parsing for common camera, phone, screenshot, and messaging formats.
- Conflict and review-required classification.
- Immutable plan generation before execution.
- Copy-only execution. Original files are not moved, renamed, deleted, or overwritten.
- SHA-256 verification after copying.
- Duplicate detection using hashes.
- Dry Run Execute mode.
- Execute Approved Plan mode.
- Real-time streamed execution progress.
- Live per-file status in the Plan Preview table.
- Image thumbnails and video previews.
- Clickable Plan Summary metrics with subfolder breakdowns.
- Subfolder counting, including empty subfolders.
- Persistent history for plans, directories, dry runs, approved executions, and file names.
- Pause, Resume, and Cancel controls for approved execution.
- Responsive desktop, tablet, and mobile layout.
- About popup with developer profile, company links, WhatsApp contact, UIDD information, and project image.

## Video About this tool



Uploading Safe Photo Organizer - Google Chrome 2026-09-17 00-29-06.mp4…



## Requirements

- Windows
- Python 3.12 or newer recommended
- A modern browser
- Local write permission for the project directory and the selected destination paths

## Installation

Open PowerShell in the project directory:

```powershell
cd D:\xampp\htdocs\ALL_PROJECTS\photo-organizer
py -m venv .venv
.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
```

## Run

```powershell
py -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Open:

```text
http://127.0.0.1:8000
```

The server is local-only when started with `127.0.0.1`.

## Normal Workflow

1. Enter or browse to a source folder.
2. Click **Create Plan**.
3. Review the Plan Summary and Plan Preview table.
4. Click summary metrics to inspect files by subfolder.
5. Run **Dry Run Execute**.
6. Review live statuses and the review queue.
7. Click **Execute Approved Plan** only when the plan is acceptable.
8. Use Pause, Resume, or Cancel if needed.
9. Confirm copied and verified totals.
10. Open History to review previous plans and operations.

## Safety Rules

The application is designed around the following safety rules:

- Source files are copied only.
- Source files are never deleted.
- Source files are never moved.
- Source files are never renamed.
- Existing destination files are not blindly overwritten.
- Conflicting destinations receive a unique target name.
- Copied files are verified with SHA-256.
- Files without reliable date evidence remain in review.
- Date conflicts are not silently treated as safe plans.
- Existing `YYYY-MM-DD` folders are excluded from future scans.

## Date Evidence

The date engine considers stronger evidence before weaker evidence. Current evidence includes:

1. EXIF image dates.
2. Filename dates.
3. Filesystem timestamps as weak fallback evidence.
4. Conflict information when sources disagree.

Each plan item contains the detected date, source, confidence, evidence, conflicts, and planned destination.

## Supported Media

Images are detected through Pillow-supported image extensions. Video extensions currently include:

- `.mp4`
- `.mov`
- `.m4v`
- `.avi`
- `.mkv`
- `.webm`
- `.3gp`

The preview endpoint serves supported image and video files for local browser preview.

## API Summary

- `GET /` - Serves the web application.
- `GET /health` - Health check.
- `GET /api/status` - Application status.
- `POST /api/scan` - Legacy scan operation.
- `POST /api/organize` - Legacy organize operation.
- `POST /api/plan` - Builds an immutable operation plan.
- `POST /api/execute` - Executes a complete operation and returns JSON.
- `POST /api/execute/stream` - Streams newline-delimited progress events.
- `GET /api/preview?path=...` - Serves a supported local media preview.
- `GET /api/about-image` - Serves the project About image.
- `GET /api/history` - Returns categorized activity history.
- `DELETE /api/history` - Clears saved activity history.
- `POST /api/verify` - File verification endpoint.

## History Categories

The History sidebar provides popup views for:

- Plan History
- Directory History
- Execute Approved Plan
- Dry Run Execute
- File Name History
- Clear History

## Testing

Run the test suite with:

```powershell
py -m pytest -q
```

The current project validation result is 13 passing tests. Some dependency deprecation warnings may appear from FastAPI/Starlette lifecycle and TestClient compatibility; they do not currently fail the suite.

## Project Layout

```text
photo-organizer/
|-- app/
|   |-- main.py
|   |-- database.py
|   |-- metadata.py
|   |-- schemas.py
|   |-- services/
|   |   |-- date_engine.py
|   |   |-- date_folders.py
|   |   |-- executor_v2.py
|   |   |-- filename_date_parser.py
|   |   |-- planner_v2.py
|   |   |-- report_v2.py
|   |   |-- review_gate.py
|   |   |-- scanner_v2.py
|   |   `-- verifier.py
|   `-- static/
|       |-- index.html
|       `-- js/app.js
|-- tests/
|-- build.md
|-- build_v2.md
|-- main_build.md
|-- requirements.txt
|-- README.md
`-- safe_photo_organizer.db
```

## License and Data Handling

This is a local project intended for personal photo organization. Media processing is performed on the local machine. No cloud upload is required by the application.
=======
# Safe-Photo-Organizer-V2
Safe Photo Organizer V2
>>>>>>> origin/main
