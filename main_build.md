# Safe Photo Organizer - Main Build Documentation

## 1. Project Identity

**Project:** Safe Photo Organizer

**Version direction:** V2 source-root organizer

**Developer:** Udara Irunika

**Portfolio:** https://udarairunika.com/

**Company:** https://uiddevelopers.com/

**WhatsApp:** https://wa.me/94764353012

## 2. Product Definition

Safe Photo Organizer is a local FastAPI browser application for organizing large personal media collections on Windows.

The source-root model is central to the design:

- The user selects one source root.
- The existing hierarchy below that root is preserved.
- Date folders are created inside the corresponding existing folder.
- Original source files remain unchanged.
- The application creates a plan before any execution.

Example:

```text
Source/
  Graduation/
    image.jpg

Result after execution:

Source/
  Graduation/
    2024-01-30/
      image.jpg
```

The file is copied. The original `Source/Graduation/image.jpg` remains in place.

## 3. Technology Stack

### Backend

- Python
- FastAPI
- Uvicorn
- Pydantic
- SQLAlchemy
- SQLite
- Pillow

### Frontend

- HTML5
- CSS3
- Vanilla JavaScript
- Fetch API
- Readable browser streaming through NDJSON

### Runtime

- Windows local development environment
- Default URL: `http://127.0.0.1:8000`

## 4. Architecture

### Application Entry Point

`app/main.py` owns:

- FastAPI application creation.
- Static file mounting.
- HTML response handling.
- API route registration.
- Plan and execute orchestration.
- Preview file serving.
- About image serving.
- History reads and deletion.
- Database initialization.

### Scanner

`app/services/scanner_v2.py` recursively scans the source root.

It returns:

- Total folders.
- Subfolder count.
- Folder paths.
- Total files.
- Supported media count.
- Unsupported file count.
- Scan items with path, relative path, name, and media type.

The scanner excludes date folders matching the strict `YYYY-MM-DD` format. This prevents a previous organization result from being treated as new input.

### Date Engine

`app/services/date_engine.py` evaluates evidence for each media file.

`app/services/filename_date_parser.py` handles filename patterns such as:

- `YYYYMMDD`
- `YYYYMMDD_HHMMSS`
- `YYYY-MM-DD`
- `YYYY_MM_DD`
- `YYYY.MM.DD`
- `IMG_YYYYMMDD_xxxxxx`
- `IMG-YYYYMMDD-WAxxxx`
- `Screenshot_YYYY-MM-DD`
- `PXL_YYYYMMDD_xxxxxx`
- `VID_YYYYMMDD_xxxxxx`

Invalid calendar values are rejected. Random numbers are not automatically treated as dates.

Each detection carries:

- Date.
- Source.
- Confidence.
- Evidence.
- Conflicts.

### Planner

`app/services/planner_v2.py` creates an immutable operation plan.

A plan item includes:

- Source path.
- Relative path.
- Media type.
- Detected date.
- Date source.
- Confidence.
- Evidence.
- Conflicts.
- Planned destination.
- Current status.
- SHA-256 hash.

The planner calculates summary totals for total media, planned items, review-required items, conflicts, duplicates, and failures.

### Review Gate

`app/services/review_gate.py` separates approved items from items requiring review or conflict handling.

Items marked `REVIEW_REQUIRED` or `DATE_CONFLICT` are not copied automatically.

### Executor

`app/services/executor_v2.py` enforces copy-only behavior.

Execution behavior:

1. Skip review-required and conflict items.
2. Perform dry-run planning without copying when requested.
3. Create destination directories only for approved execution.
4. Detect an existing destination.
5. Compare hashes for duplicate detection.
6. Select a unique destination name when content differs.
7. Copy with `shutil.copy2`.
8. Verify source and destination SHA-256 values.
9. Report verified, duplicate, failed, and skipped states.

`iter_execute_plan()` yields progress events for live browser updates.

### Reporting

`app/services/report_v2.py` converts plan and execution data into final totals displayed in the UI.

### Database

`app/database.py` defines SQLite models for scan data, operation logs, and categorized activity history.

History categories:

- `plan`
- `directories`
- `execute_approved`
- `dry_run`
- `file_names`

## 5. Complete User Workflow

### Source Selection

The Source Folder input accepts a Windows path. The Browse control uses the browser directory picker where supported and falls back to manual path entry when a real operating-system path cannot be exposed by the browser.

### Create Plan

Create Plan:

- Disables the button while running.
- Shows an animated inline progress bar.
- Builds a full plan.
- Updates media, review, conflict, and subfolder counts.
- Renders up to the configured preview rows.
- Shows a success status after completion.

### Plan Preview

The table includes:

- Preview thumbnail or video control.
- File name.
- Relative path.
- Detected date.
- Date source.
- Planned destination.
- Live status.

Supported live statuses include planned, skipped review, verified, duplicate, hash mismatch, and failed states.

### Dry Run Execute

Dry Run Execute:

- Shows an inline loading bar.
- Streams progress events.
- Updates the progress bar and counters.
- Does not copy files.
- Displays a completion popup.

### Execute Approved Plan

Execute Approved Plan:

- Shows an inline loading bar.
- Streams per-item progress.
- Updates table statuses live.
- Shows Pause, Resume, and Cancel controls.
- Copies only approved items.
- Verifies copied files with SHA-256.
- Displays a completion popup with copied and verified totals.

### Operation Controls

Pause aborts the active browser stream while retaining the operation state.

Resume starts the approved operation again. The executor is safe to rerun because it detects existing files, compares hashes, and skips already copied duplicates.

Cancel aborts the active operation and clears the operation controls.

### Plan Summary

The summary contains clickable metrics:

- Total Media.
- Planned.
- Review Required.
- Conflicts.
- Copied.
- Verified.
- Subfolders.

The popup groups matching records by folder. Empty folders are included in the Subfolders view.

### History

The responsive history sidebar opens categorized popups. History is written after plan generation and completed execution events.

Clear History requires confirmation and deletes all activity history rows through `DELETE /api/history`.

## 6. API Contract

### `GET /`

Returns the frontend HTML document.

### `GET /health`

Returns application health information.

### `POST /api/scan`

Request:

```json
{"source": "D:/Photos"}
```

Returns legacy scan statistics.

### `POST /api/plan`

Request:

```json
{"source": "D:/Photos"}
```

Returns:

```json
{
  "source_root": "D:\\Photos",
  "scan": {},
  "plan": [],
  "summary": {}
}
```

### `POST /api/execute`

Request:

```json
{"source": "D:/Photos", "dry_run": false}
```

Returns review information, execution results, and a final report.

### `POST /api/execute/stream`

Returns newline-delimited JSON events:

```json
{"type":"started","total":10}
{"type":"progress","completed":1,"total":10}
{"type":"complete","report":{}}
```

### `GET /api/preview?path=...`

Serves a local image or video if the file exists and has a supported image/video MIME type.

### `GET /api/about-image`

Serves the project-root About image `photo_2026-09-06_20-37-22.jpg`.

### `GET /api/history`

Returns the categorized history object.

### `DELETE /api/history`

Deletes all saved activity-history records and returns the deleted row count.

## 7. Frontend Details

The frontend is a single-page vanilla HTML/JavaScript interface located in:

- `app/static/index.html`
- `app/static/js/app.js`

The UI includes:

- Fixed desktop history sidebar.
- Horizontal mobile history toolbar.
- Responsive summary grid.
- Responsive source and action controls.
- Horizontally scrollable preview table on small screens.
- Centered About popup.
- Rounded portfolio, company, and WhatsApp links.
- GitHub developer avatar.
- Local About image.

## 8. Installation and Operations

From PowerShell:

```powershell
cd D:\xampp\htdocs\ALL_PROJECTS\photo-organizer
py -m venv .venv
.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
py -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Open the application at:

```text
http://127.0.0.1:8000
```

Stop the server with `Ctrl+C` in the terminal hosting Uvicorn.

## 9. Validation

Run:

```powershell
py -m pytest -q
```

The completed project currently reports:

```text
13 passed
```

Known non-blocking warnings may be emitted by current FastAPI/Starlette and SQLAlchemy versions:

- FastAPI `on_event` lifecycle deprecation.
- Starlette TestClient/httpx compatibility warning.
- `datetime.utcnow()` deprecation from SQLAlchemy default handling.

These warnings do not currently fail the test suite.

## 10. Safety and Operational Limits

- The app is intended for local use.
- The user should test with a copy of valuable data before a large production run.
- Review-required and conflicting dates require user review.
- Browser folder pickers cannot always provide the actual Windows path; manual entry remains available.
- The preview endpoint is intended for local use and should not be exposed publicly without additional access controls.
- History is stored in the local SQLite database `safe_photo_organizer.db`.

## 11. Branding and About Content

The About popup contains:

- Udara Irunika developer identity.
- GitHub avatar image.
- Developer portfolio link.
- UID Developers website link.
- WhatsApp contact link.
- UIDD company description.
- `photo_2026-09-06_20-37-22.jpg` project image.

## 12. Future Improvements

Potential future work includes:

- Replace deprecated FastAPI startup event with a lifespan handler.
- Add dedicated tests for history deletion and stream cancellation.
- Add persisted operation IDs for server-side pause/resume across page reloads.
- Add user-selectable review approval controls per plan row.
- Add exportable JSON/CSV operation reports.
- Add configurable media extension and evidence rules.
- Add authentication if the app is ever exposed beyond localhost.
