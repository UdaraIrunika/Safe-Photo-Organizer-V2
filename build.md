You are a senior Python full-stack developer and software architect.

PROJECT DEVELOPER:
Udara Irunika

DEVELOPER PORTFOLIO:
https://udarairunika.com/

COMPANY WEBSITE:
https://uiddevelopers.com/

I want you to build a complete LOCAL WEB-BASED PHOTO ORGANIZER application for Windows.

PROJECT NAME:
Safe Photo Organizer

MAIN PURPOSE:
I have a very large photo collection stored on a Windows hard drive. The collection contains many existing folders and subfolders. I want a local web application that scans the entire folder recursively, detects the date each photo was taken, and creates date-based folders INSIDE the existing folder structure.

IMPORTANT:
The original files are extremely valuable.

NEVER delete, move, rename, overwrite, or modify original source files.

The application must COPY files only.

Every copied file must be verified using SHA-256 before being marked as successfully copied.

==================================================
1. TECHNOLOGY STACK
==================================================

Backend:
- Python 3.12+
- FastAPI
- Uvicorn
- Pydantic
- Pillow

Frontend:
- HTML5
- CSS3
- Vanilla JavaScript
- Fetch API
- No React/Vue/Angular for V1

Database:
- SQLite for scan history and operation logs
- SQLAlchemy if useful

Application type:
- Local web application running on Windows
- Browser UI communicates with local FastAPI backend
- Default URL:
  http://127.0.0.1:8000

Do not require cloud storage.
Do not upload photos to the internet.
All processing must happen locally.

==================================================
2. CORE USER WORKFLOW
==================================================

The user should be able to:

1. Select a source folder.
2. Select a separate destination folder.
3. Scan the source recursively.
4. Detect all supported image files.
5. Extract the photo date.
6. Display scan statistics.
7. Preview exactly where files will be copied.
8. Run a DRY RUN before any actual copying.
9. Start the copy operation.
10. Verify every copied file using SHA-256.
11. Display successful, failed, skipped, and duplicate files.
12. Generate an operation summary/log.

==================================================
3. SUPPORTED IMAGE FORMATS
==================================================

Support at minimum:

.jpg
.jpeg
.png
.webp
.tif
.tiff
.bmp
.gif

Design the system so additional formats can easily be added later.

HEIC/HEIF support should be optional because Pillow support may depend on the installed environment.

==================================================
4. DATE DETECTION
==================================================

Date priority must be:

1. EXIF DateTimeOriginal
2. EXIF DateTimeDigitized
3. EXIF DateTime
4. Filesystem modified date as fallback

Create a metadata service:

metadata.py

Example:

get_photo_date(path)

Return:

{
    "date": "2026-08-09",
    "source": "EXIF"
}

or:

{
    "date": "2026-08-09",
    "source": "FILESYSTEM"
}

Never silently invent a date.

==================================================
5. MOST IMPORTANT FOLDER STRUCTURE REQUIREMENT
==================================================

PRESERVE THE ORIGINAL FOLDER STRUCTURE.

Example source:

F:\MY DATA\MY PHONE ALBUMS\

    GRADUATION\
        photo1.jpg
        photo2.jpg

    ESU MEMO VIDEO\
        photo3.jpg

    MY LOVE VIDEO AND MOMENTS\
        photo4.jpg

The destination must become:

F:\MY DATA\ORGANIZED PHOTOS\

    GRADUATION\
        2026-08-09\
            photo1.jpg

        2026-08-10\
            photo2.jpg

    ESU MEMO VIDEO\
        2026-07-09\
            photo3.jpg

    MY LOVE VIDEO AND MOMENTS\
        2026-06-12\
            photo4.jpg

DO NOT flatten everything into:

2026-08-09\
2026-08-10\
2026-07-09\

The original folder hierarchy MUST be preserved.

==================================================
6. DESTINATION PATH ALGORITHM
==================================================

For each source file:

source:
F:\MY DATA\MY PHONE ALBUMS\GRADUATION\photo1.jpg

relative path from source root:

GRADUATION\photo1.jpg

photo date:

2026-08-09

destination:

F:\MY DATA\ORGANIZED PHOTOS\GRADUATION\2026-08-09\photo1.jpg

For:

F:\MY DATA\MY PHONE ALBUMS\MY LOVE VIDEO AND MOMENTS\HOLIDAY\photo2.jpg

destination:

F:\MY DATA\ORGANIZED PHOTOS\MY LOVE VIDEO AND MOMENTS\HOLIDAY\2026-08-10\photo2.jpg

Preserve ALL nested subfolders.

==================================================
7. DUPLICATE / NAME COLLISION HANDLING
==================================================

Never overwrite destination files by default.

If:

photo.jpg

already exists, automatically generate:

photo_1.jpg
photo_2.jpg
photo_3.jpg

etc.

However, also implement SHA-256 duplicate detection.

If source SHA-256 == destination SHA-256:

mark as:

DUPLICATE_ALREADY_EXISTS

and do not copy unnecessarily.

The UI must clearly distinguish:

- NEW COPY
- DUPLICATE
- NAME CONFLICT
- FAILED
- VERIFIED

==================================================
8. SAFE COPY ENGINE
==================================================

Create:

services/
    organizer.py
    verifier.py

Use safe copying.

Recommended:

shutil.copy2()

Do not use shutil.move().

After copying:

source_hash = SHA256(source)
destination_hash = SHA256(destination)

Compare both.

Only mark:

VERIFIED

when hashes are identical.

If hashes differ:

HASH_MISMATCH

Do not delete the source.

==================================================
9. DRY RUN
==================================================

DRY RUN must be enabled by default.

During dry run:

- Do not create destination files.
- Do not modify source files.
- Calculate planned destination paths.
- Display what would happen.

Example:

SOURCE:
F:\MY DATA\MY PHONE ALBUMS\GRADUATION\IMG001.jpg

DATE:
2026-08-09

DESTINATION:
F:\MY DATA\ORGANIZED PHOTOS\GRADUATION\2026-08-09\IMG001.jpg

STATUS:
PLANNED

The user must explicitly click:

START ORGANIZATION

before real copying begins.

==================================================
10. SCAN STATISTICS
==================================================

After scanning display:

Total folders
Total files
Total supported photos
Photos with EXIF date
Photos using filesystem fallback
Unsupported files
Errors

Example dashboard:

Photos Found: 12,458
EXIF Dates: 11,982
Fallback Dates: 476
Folders: 86
Errors: 0

==================================================
11. WEB UI
==================================================

Create a professional modern dashboard.

Main sections:

HEADER
- Safe Photo Organizer
- Local Processing indicator

SOURCE / DESTINATION

Source Folder:
[ path input ] [ Browse ]

Destination Folder:
[ path input ] [ Browse ]

Buttons:

[ Scan Photos ]

After scan:

SCAN SUMMARY

Photos Found
Folders Found
EXIF Dates
Fallback Dates
Errors

PREVIEW TABLE

Columns:

Filename
Original Folder
Detected Date
Date Source
Destination
Status

Buttons:

[ Dry Run ]
[ Start Organization ]

During operation:

Progress bar

Files processed:
1250 / 12458

Copied:
1200

Verified:
1198

Duplicates:
2

Failed:
0

After completion:

OPERATION SUMMARY

Total
Copied
Verified
Duplicates
Failed
Skipped

==================================================
12. API DESIGN
==================================================

Create clean API routes.

GET /
GET /health

POST /api/scan

POST /api/organize

POST /api/verify

GET /api/status

GET /api/history

Use Pydantic request/response models.

Example:

POST /api/scan

{
    "source": "F:\\MY DATA\\MY PHONE ALBUMS"
}

Return structured JSON.

Do not expose arbitrary filesystem access through unsafe endpoints.

Validate paths.

==================================================
13. WINDOWS PATH HANDLING
==================================================

The application must properly support:

C:\
D:\
E:\
F:\

including paths containing:

spaces
parentheses
ampersands
Unicode characters

Example:

F:\V,I,P,A & O (F)\MY DATA\MY PHONE ALBUMS

Use pathlib.Path rather than manually concatenating strings.

Never assume the source folder is C:.

==================================================
14. SECURITY
==================================================

This application runs locally.

Still implement:

- Path validation
- Prevent source == destination
- Prevent destination being inside source
- Prevent accidental recursive scanning of destination
- No shell command execution
- No arbitrary command execution through API
- No remote network requests for photos
- No photo uploads
- Validate file extensions
- Handle permission errors
- Handle corrupted images safely
- Handle symlinks carefully
- Never follow dangerous paths outside the selected source tree

==================================================
15. PERFORMANCE
==================================================

The folder may contain tens of thousands or hundreds of thousands of files.

Do NOT load every image into memory.

Use:

Path.rglob()

or efficient os.walk().

Process files incrementally.

Calculate SHA-256 using chunks, for example:

1 MB chunks.

Do not read huge files completely into RAM.

The UI must remain responsive.

Design the backend so scanning/copying can later use background tasks.

==================================================
16. ERROR HANDLING
==================================================

Never stop the entire operation because one file fails.

For each failure record:

source
destination
error
timestamp
status

Continue processing remaining files.

At the end show:

Successful
Failed
Skipped
Duplicates

==================================================
17. LOGGING
==================================================

Create:

logs/

Store operation logs.

Example:

operation_2026-09-16_181500.json

Include:

operation ID
start time
end time
source
destination
statistics
file results
errors

Do not store image contents.

==================================================
18. DATABASE
==================================================

Use SQLite.

Tables can include:

operations
files

operations:

id
started_at
completed_at
source
destination
total_files
copied
verified
duplicates
failed
status

files:

id
operation_id
source_path
destination_path
detected_date
date_source
sha256
status
error

==================================================
19. PROJECT STRUCTURE
==================================================

Create:

safe-photo-organizer/

    backend/
        app/
            __init__.py
            main.py

            api/
                __init__.py
                routes.py

            services/
                __init__.py
                scanner.py
                metadata.py
                organizer.py
                verifier.py

            models/
                __init__.py
                database.py
                schemas.py

            utils/
                __init__.py
                paths.py
                hashing.py
                logging_config.py

        requirements.txt

    frontend/
        index.html

        css/
            style.css

        js/
            app.js

    tests/
        test_metadata.py
        test_scanner.py
        test_paths.py
        test_verifier.py
        test_organizer.py

    logs/

    README.md

    .gitignore

==================================================
20. TESTING
==================================================

Create automated tests.

IMPORTANT:

Tests must NEVER operate on my real photo collection.

Use:

tests/test_data/

with temporary files/directories.

Test:

- EXIF date extraction
- filesystem fallback
- recursive scanning
- nested folder preservation
- date folder generation
- duplicate detection
- SHA-256 verification
- filename collisions
- source == destination rejection
- destination inside source rejection
- missing source rejection
- corrupted image handling

Use pytest.

==================================================
21. FRONTEND UX
==================================================

Make the interface clean and professional.

Use:

- responsive design
- cards
- progress indicators
- status badges
- tables
- modal for operation details
- toast notifications
- confirmation dialog before actual organization

Do not use external CDN dependencies unless absolutely necessary.

The application should work offline after installation.

==================================================
22. CRITICAL SAFETY CONFIRMATION
==================================================

Before actual copying:

Show:

"Your original files will NOT be deleted or moved.
The application will COPY files to the destination and verify each copy."

Require confirmation:

[ ] I understand that the application will copy files only.

Then:

[ START SAFE COPY ]

==================================================
23. DEVELOPMENT RULES
==================================================

Do NOT generate the entire project blindly in one huge file.

Build it incrementally.

PHASE 1:
Create project structure.

PHASE 2:
Implement metadata extraction.

PHASE 3:
Implement recursive scanner.

PHASE 4:
Implement destination path calculation.

PHASE 5:
Implement SHA-256 verification.

PHASE 6:
Implement safe copy engine.

PHASE 7:
Implement FastAPI routes.

PHASE 8:
Implement frontend dashboard.

PHASE 9:
Integrate frontend and backend.

PHASE 10:
Add tests.

PHASE 11:
Run tests and fix all errors.

PHASE 12:
Create Windows startup script.

After each phase:
- explain what was created
- show changed files
- run relevant tests
- report errors
- fix errors before moving to the next phase

Do not skip testing.

==================================================
24. START NOW
==================================================

Start with PHASE 1 only.

Create the complete project structure and minimal runnable FastAPI application.

Do not implement the photo copying yet.

After PHASE 1 is complete, stop and show me:

1. Project tree
2. Files created
3. Commands to install dependencies
4. Command to start the server
5. Expected browser URL
6. Test result

Wait for confirmation before continuing to PHASE 2.