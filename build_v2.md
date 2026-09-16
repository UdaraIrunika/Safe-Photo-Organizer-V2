You are a senior Python architect, digital-media metadata engineer, forensic file-analysis engineer, cybersecurity engineer, and professional desktop/web application developer.

I am building a high-level LOCAL WEB-BASED PHOTO ORGANIZING APPLICATION for Windows.

The application will eventually be published as a professional tool.

This is NOT a simple file sorter.

It must be designed as a reliable photo date intelligence and organization system that minimizes incorrect date classification.

============================================================
PROJECT NAME
============================================================

Safe Photo Organizer

Goal:

Automatically organize a large personal photo collection INSIDE THE ORIGINAL SOURCE FOLDER while preserving every existing folder and subfolder.

The application must determine the most reliable date associated with each image using MULTIPLE independent sources.

The system must NEVER blindly trust Windows filesystem modified/created timestamps.

============================================================
CRITICAL REAL-WORLD PROBLEM
============================================================

My photo collection contains images saved/copied/downloaded/shared through many different applications and devices.

Examples of filenames include:

20240130_080421.jpg
20240130_080427.jpg
20240501_195944.jpg
20240617_164153.jpg
20240723_064614.jpg

These filenames strongly indicate dates.

However, Windows filesystem dates may be completely different.

Example:

Actual image date:
2024-01-30

Filesystem modified date:
2026-05-01

The application MUST NOT incorrectly organize the image into:

2026-05-01

when reliable evidence indicates:

2024-01-30

This is one of the most important requirements of the entire project.

============================================================
CORE PRINCIPLE
============================================================

The application must use an EVIDENCE-BASED DATE DETECTION ENGINE.

Never use only one date source.

Never automatically trust filesystem modified date when stronger evidence exists.

Every detected date must have:

- detected date
- date source
- confidence level
- evidence
- conflict information

Example:

{
    "date": "2024-01-30",
    "source": "FILENAME",
    "confidence": "HIGH",
    "evidence": "20240130_080421.jpg"
}

============================================================
DATE SOURCE PRIORITY
============================================================

Implement a configurable date evidence engine.

Use the following evidence sources.

SOURCE 1:
EXIF DateTimeOriginal

SOURCE 2:
EXIF DateTimeDigitized

SOURCE 3:
EXIF DateTime

SOURCE 4:
XMP metadata dates if available

SOURCE 5:
Other embedded image metadata containing creation/capture dates

SOURCE 6:
Filename date patterns

SOURCE 7:
Parent folder date patterns

SOURCE 8:
Filesystem timestamps

Filesystem timestamps MUST be considered weak evidence.

Do NOT simply use:

os.path.getmtime()

as the primary date.

============================================================
FILENAME DATE INTELLIGENCE
============================================================

Create:

app/services/date_engine.py

and/or:

app/services/filename_date_parser.py

The parser must detect many common filename date patterns.

At minimum support:

YYYYMMDD

YYYYMMDD_HHMMSS

YYYY-MM-DD

YYYY_MM_DD

YYYY.MM.DD

YYYY-MM-DD_HH-MM-SS

YYYYMMDD-HHMMSS

YYYYMMDD_HHMM

YYYYMMDDHHMMSS

Examples:

20240130_080421.jpg
20240130_080427.jpg
2024-01-30.jpg
2024_01_30.jpg
2024.01.30.jpg
IMG_20240130_080421.jpg
IMG-20240130-WA0001.jpg
Screenshot_2024-01-30-123456.png

The parser should also recognize common application/device naming patterns.

Examples may include:

IMG-YYYYMMDD-WAxxxx
IMG_YYYYMMDD_xxxxxx
Screenshot_YYYY-MM-DD
PXL_YYYYMMDD_xxxxxx
VID_YYYYMMDD_xxxxxx
photo_YYYYMMDD

Design the parser as a modular rule engine so more patterns can be added later.

============================================================
IMPORTANT: DO NOT FALSELY PARSE RANDOM NUMBERS
============================================================

Do NOT assume every 8-digit number is a date.

For example:

12345678.jpg

must NOT automatically become:

1234-56-78

Validate:

- year range
- month range
- day range
- actual calendar date
- surrounding filename context
- plausible timestamp

Only accept valid calendar dates.

============================================================
DATE CONFLICT DETECTION
============================================================

This is CRITICAL.

Suppose:

EXIF:
2024-01-30

Filename:
2024-01-30

Filesystem:
2026-05-01

The system should select:

2024-01-30

and record:

filesystem conflict detected.

Example:

{
    "selected_date": "2024-01-30",
    "selected_source": "EXIF",
    "confidence": "VERY_HIGH",
    "conflicts": [
        {
            "source": "FILESYSTEM",
            "date": "2026-05-01"
        }
    ]
}

Do NOT silently hide conflicts.

The UI should show:

✓ EXIF: 2024-01-30
✓ Filename: 2024-01-30
⚠ Filesystem: 2026-05-01

Selected:
2024-01-30

============================================================
DATE EVIDENCE SCORING
============================================================

Create a transparent evidence scoring system.

Example conceptual ranking:

EXIF DateTimeOriginal:
VERY_HIGH

EXIF Digitized:
HIGH

Other embedded metadata:
HIGH

Filename:
HIGH

Parent folder:
MEDIUM

Filesystem modified:
LOW

Filesystem created:
VERY_LOW

Do NOT blindly hard-code simplistic scoring.

The architecture must allow future tuning.

If multiple strong sources agree:

increase confidence.

If strong sources disagree:

mark:

DATE_CONFLICT

and apply a review workflow.

============================================================
AMBIGUOUS DATES
============================================================

NEVER silently make a potentially wrong decision.

If:

EXIF = 2024-01-30

Filename = 2025-08-20

and there is no reliable way to determine which is correct:

mark:

REVIEW_REQUIRED

The user must be able to review the file before organization.

Provide filters:

ALL
HIGH CONFIDENCE
MEDIUM CONFIDENCE
LOW CONFIDENCE
CONFLICTS
REVIEW REQUIRED

============================================================
PRESERVE ORIGINAL FOLDER STRUCTURE
============================================================

There is NO separate destination folder.

The selected source folder is the organization root.

Example:

MY PHONE ALBUMS/

    GRADUATION/
        image1.jpg

    MY LOVE VIDEO AND MOMENTS/
        image2.jpg

    FAMILY/
        TRIPS/
            KANDY/
                image3.jpg

After organization:

MY PHONE ALBUMS/

    GRADUATION/
        2024-08-09/
            image1.jpg

    MY LOVE VIDEO AND MOMENTS/
        2024-06-12/
            image2.jpg

    FAMILY/
        TRIPS/
            KANDY/
                2024-07-09/
                    image3.jpg

Preserve every existing non-date folder.

============================================================
DATE FOLDER EXCLUSION
============================================================

Any directory matching exactly:

YYYY-MM-DD

must be treated as an organizer date folder.

Example:

2024-01-30

2025-08-19

2026-09-16

The scanner MUST NOT scan inside these folders.

This prevents:

2024-01-30/
    2024-01-30/
        2024-01-30/
            photo.jpg

from ever occurring.

Implement:

is_date_folder(path)

using strict calendar validation.

============================================================
IMMUTABLE ORGANIZATION PLAN
============================================================

The application MUST NOT scan and modify files simultaneously.

Use this architecture:

PHASE 1:
SCAN

PHASE 2:
ANALYZE METADATA

PHASE 3:
BUILD IMMUTABLE PLAN

PHASE 4:
VALIDATE PLAN

PHASE 5:
SHOW PREVIEW

PHASE 6:
USER CONFIRMATION

PHASE 7:
EXECUTE PLAN

PHASE 8:
VERIFY

PHASE 9:
GENERATE REPORT

The execution engine must operate ONLY on the approved plan.

============================================================
SAFE DEFAULT
============================================================

Default operation:

COPY

Never MOVE by default.

Original files must remain untouched.

Default:

delete_after_verify = false

If a future delete feature exists, deletion is allowed ONLY after:

1. successful copy
2. SHA-256 source hash
3. SHA-256 destination hash
4. exact hash match
5. successful verification
6. explicit user confirmation

Never delete if verification fails.

============================================================
DUPLICATE DETECTION
============================================================

Implement SHA-256 content hashing.

If:

source SHA-256 == destination SHA-256

mark:

DUPLICATE_ALREADY_EXISTS

Do not create unnecessary copies.

Also detect:

same filename + different content

and handle safely.

Never overwrite by default.

============================================================
ADVANCED DUPLICATE DETECTION
============================================================

Design the system so perceptual hashing can later be added.

Possible future algorithms:

pHash
dHash
aHash

Do NOT make perceptual hashing mandatory for V1.

Keep it modular.

============================================================
CORRUPTED FILE HANDLING
============================================================

If an image cannot be decoded:

DO NOT crash.

Mark:

CORRUPTED_OR_UNREADABLE

Keep the original untouched.

Display it in an error/review list.

============================================================
SUPPORTED IMAGES
============================================================

At minimum:

.jpg
.jpeg
.png
.webp
.tif
.tiff
.bmp
.gif

Optional support:

.heic
.heif

The architecture must allow new formats.

============================================================
VIDEO ARCHITECTURE
============================================================

Design the system so video support can be added later.

Do not incorrectly classify videos as images.

Create an abstraction such as:

MediaFile
ImageFile
VideoFile

Future video metadata can include:

creation_time
QuickTime metadata
filename date
filesystem date

============================================================
FOLDER NAME INTELLIGENCE
============================================================

If a parent folder itself contains a strong date:

Example:

MY TRIP 2024-07-15/

and the photo has no stronger date evidence,

the folder date may be considered medium-confidence evidence.

Do NOT automatically treat arbitrary folder numbers as dates.

============================================================
SPECIAL FILE NAMING PATTERNS
============================================================

Build extensible rules for:

Camera photos
Android photos
iPhone photos
Google Photos exports
WhatsApp images
Screenshots
Social-media downloads
Messenger exports
Telegram exports
Edited images
Downloaded images

The system must recognize common patterns without assuming one device.

Create:

filename_rules.py

where patterns can be added independently.

============================================================
EDITED/COPIED IMAGE DETECTION
============================================================

Some applications modify filenames or metadata.

The system must distinguish:

ORIGINAL CAPTURE DATE

from:

FILE SAVE DATE

from:

FILE MODIFIED DATE

The goal is to determine the most likely ORIGINAL MEDIA DATE.

Do not confuse:

download date
copy date
edit date
filesystem modification date

with:

original capture date.

============================================================
METADATA INSPECTION
============================================================

For each image, collect available metadata safely.

Do not upload metadata anywhere.

Possible fields:

DateTimeOriginal
DateTimeDigitized
DateTime
Make
Model
Software
Orientation
GPS presence
XMP dates

Do not expose private GPS coordinates by default.

If GPS exists:

show only:

GPS metadata available

unless the user explicitly chooses to inspect it.

============================================================
PRIVACY
============================================================

This application is LOCAL-FIRST.

No photo uploads.

No external API calls.

No cloud processing.

No telemetry by default.

No analytics by default.

No external image recognition service.

All metadata processing happens locally.

============================================================
WEB APPLICATION
============================================================

Frontend:

HTML
CSS
JavaScript

Backend:

Python
FastAPI

The browser communicates only with:

127.0.0.1

============================================================
UI
============================================================

Create a professional dark modern dashboard.

HEADER:

Safe Photo Organizer

Status:
LOCAL PROCESSING

SOURCE:

Source Folder

[ Browse ]

Selected folder:

F:\...\MY PHONE ALBUMS

Button:

[ SCAN & ANALYZE ]

============================================================
DASHBOARD STATISTICS
============================================================

Display:

Photos Found
Folders Found
Date Detected
EXIF Dates
Filename Dates
Fallback Dates
Conflicts
Review Required
Duplicates
Errors

Example:

Photos Found: 12,458
EXIF Dates: 8,920
Filename Dates: 3,100
Filesystem Fallback: 438
Conflicts: 42
Review Required: 17
Duplicates: 86
Errors: 3

============================================================
INTELLIGENT PREVIEW TABLE
============================================================

Columns:

Thumbnail

Filename

Current Folder

Detected Date

Date Source

Confidence

Evidence

Conflict

Planned Destination

Status

Example:

IMG_20240130_080421.jpg

GRADUATION

2024-01-30

FILENAME

HIGH

20240130_080421

None

GRADUATION/2024-01-30/IMG_20240130_080421.jpg

PLANNED

============================================================
DATE EVIDENCE PANEL
============================================================

When the user clicks a photo, show:

DATE ANALYSIS

EXIF DateTimeOriginal:
2024-01-30 08:04:21

Filename Date:
2024-01-30

Filesystem Modified:
2026-05-01

Selected:
2024-01-30

Confidence:
VERY HIGH

Reason:

EXIF and filename agree.
Filesystem timestamp conflicts and is treated as weak evidence.

============================================================
REVIEW QUEUE
============================================================

Create a dedicated:

REVIEW REQUIRED

section.

Display files where:

- strong metadata conflicts
- date cannot be confidently determined
- filename has multiple possible dates
- metadata is suspicious
- date is outside reasonable bounds

Allow user to select the correct date manually.

Manual override must be stored in the organization plan.

Example:

[ Use EXIF ]
[ Use Filename ]
[ Use Filesystem ]
[ Select Custom Date ]

============================================================
DRY RUN
============================================================

Dry run must be the default.

It must:

- scan
- analyze
- create plan
- show destination paths

but:

DO NOT create folders
DO NOT copy files
DO NOT move files
DO NOT delete files

============================================================
REAL ORGANIZATION
============================================================

Only after explicit confirmation:

[ START SAFE ORGANIZATION ]

The application should show:

"X files will be organized."

"Y files require review."

"Z files contain date conflicts."

Do not allow organization if unresolved REVIEW_REQUIRED files exist unless the user explicitly chooses:

[ Organize High-Confidence Files Only ]

============================================================
HIGH-CONFIDENCE MODE
============================================================

Provide:

Organize:
[ All approved ]
[ High-confidence only ]

High-confidence mode must skip:

REVIEW_REQUIRED
DATE_CONFLICT
LOW_CONFIDENCE

and leave those files untouched.

============================================================
PROGRESS
============================================================

Show:

Files processed
Total files

Copied
Verified
Duplicates
Skipped
Review Required
Failed

Progress bar.

The UI must remain responsive for tens/hundreds of thousands of files.

============================================================
UNDO / TRANSACTION LOG
============================================================

Implement an operation journal.

Every action should have:

operation_id
source
destination
action
timestamp
hash
status

Example:

operation_20260916_201500.json

This will allow a future safe UNDO feature.

Do not implement unsafe rollback.

If implementing undo, it must only remove files that the application itself created and that can be proven to match the recorded hash.

============================================================
DATABASE
============================================================

Use SQLite.

Tables:

operations
media_files
date_evidence
organization_actions

Store:

file path
hash
detected date
selected date
date source
confidence
status
operation ID

Do not store actual image data.

============================================================
API
============================================================

Create clean endpoints:

GET /

GET /health

POST /api/scan

POST /api/analyze

POST /api/plan

POST /api/organize

GET /api/status

GET /api/history

GET /api/review

POST /api/review/{id}

The API must use Pydantic models.

============================================================
SECURITY
============================================================

This is a local application, but follow secure development practices.

Prevent:

- arbitrary shell execution
- path traversal
- unsafe user-controlled command execution
- accidental scanning outside selected root
- recursive scanning of date folders
- overwriting originals
- accidental deletion
- symlink traversal outside source
- destination ambiguity

Use pathlib.Path.

Resolve paths safely.

============================================================
WINDOWS SUPPORT
============================================================

Must support:

C:\
D:\
E:\
F:\

and paths containing:

spaces
&
parentheses
Unicode
long folder names

Example:

F:\V,I,P,A & O (F)\MY DATA\MY PHONE ALBUMS

Do not manually concatenate Windows paths.

============================================================
PERFORMANCE
============================================================

The user's collection may contain:

10,000+
50,000+
100,000+
500,000+

files.

Design for large collections.

Do not load all images into RAM.

Read metadata efficiently.

Calculate SHA-256 in chunks.

Use controlled directory traversal.

Avoid scanning generated date folders.

Avoid duplicate work.

============================================================
PUBLISHING REQUIREMENTS
============================================================

The final application should eventually be publishable.

Prepare for:

Windows executable packaging
installer
versioning
configuration
logging
error reporting
portable mode

Potential future packaging:

PyInstaller

The application should NOT require the user to manually install Python for the published version.

Do not implement packaging until the core system is stable.

============================================================
PROJECT STRUCTURE
============================================================

Refactor the current project toward:

safe-photo-organizer/

    backend/

        app/

            main.py

            api/

            services/

                scanner.py
                metadata.py
                date_engine.py
                filename_date_parser.py
                planner.py
                organizer.py
                verifier.py
                duplicate_detector.py

            utils/

                paths.py
                date_folders.py
                hashing.py

            models/

                database.py
                schemas.py

    frontend/

        index.html

        css/
            style.css

        js/
            app.js

    tests/

        test_date_engine.py
        test_filename_parser.py
        test_metadata.py
        test_scanner.py
        test_planner.py
        test_organizer.py
        test_verifier.py
        test_duplicates.py
        test_paths.py

    logs/

    README.md

    requirements.txt


============================================================
SOCIAL MEDIA & APPLICATION MEDIA INTELLIGENCE
============================================================

The organizer must support media originating from social media,
messaging applications, cloud exports, screenshots, downloads,
screen recordings, and editing applications.

IMPORTANT:

Do NOT assume the filesystem timestamp represents the original
media creation date.

A media file may have:

Original creation date:
2024-01-30

Downloaded/exported/copied:
2026-05-01

The organizer should attempt to recover the ORIGINAL MEDIA DATE.

============================================================
SUPPORTED SOCIAL / MESSAGING SOURCES
============================================================

Build an extensible Application Source Detection Engine.

At minimum support common patterns associated with:

- Snapchat
- TikTok
- Instagram
- Facebook
- WhatsApp
- Messenger
- Telegram
- Signal
- Viber
- Discord
- X / Twitter
- YouTube
- Google Photos
- Google Drive
- iCloud Photos
- OneDrive
- Dropbox
- Pinterest
- Reddit
- CapCut
- Lightroom
- Adobe Photoshop
- Canva
- screen capture applications
- Android camera
- iPhone camera
- Windows screenshots
- Windows screen recordings

The application source is INFORMATIONAL.

Never assume that a filename alone proves the original creation date.

============================================================
APPLICATION-SPECIFIC FILENAME DETECTION
============================================================

Create:

app/services/media_source_detector.py

The detector should analyze:

- filename
- extension
- directory name
- nearby metadata
- known export naming conventions
- sidecar files
- folder structure

Return something like:

{
    "source": "SNAPCHAT",
    "confidence": "MEDIUM",
    "evidence": "filename pattern"
}

Possible values:

CAMERA
ANDROID
IPHONE
SNAPCHAT
TIKTOK
INSTAGRAM
FACEBOOK
WHATSAPP
MESSENGER
TELEGRAM
SIGNAL
VIBER
DISCORD
YOUTUBE
GOOGLE_PHOTOS
ICLOUD
GOOGLE_DRIVE
ONEDRIVE
DROPBOX
CAPCUT
LIGHTROOM
PHOTOSHOP
CANVA
SCREENSHOT
SCREEN_RECORDING
UNKNOWN

============================================================
SOCIAL MEDIA DATE EVIDENCE
============================================================

For each application, implement a modular parser.

Example architecture:

app/services/social_media/

    __init__.py

    snapchat.py
    tiktok.py
    instagram.py
    facebook.py
    whatsapp.py
    messenger.py
    telegram.py
    signal.py
    viber.py
    discord.py
    youtube.py
    google_photos.py
    icloud.py
    capcut.py
    generic.py

Do NOT create fake certainty.

Each parser should return:

{
    "date": "...",
    "source": "TIKTOK",
    "evidence": "...",
    "confidence": "...",
}

============================================================
IMPORTANT: SOCIAL MEDIA EXPORTS
============================================================

Social-media platforms may provide exported metadata separately
from the image/video itself.

The system must support sidecar/metadata files when present.

Examples:

JSON
CSV
TXT
XML
XMP
HTML export metadata

If a media file has an associated metadata file containing a
creation date, associate it with the media file where the
relationship can be established safely.

Never randomly associate unrelated metadata files.

============================================================
GOOGLE PHOTOS EXPORTS
============================================================

Support Google Photos Takeout-style structures.

Look for associated metadata such as:

.json

When a Google Photos metadata JSON file is clearly associated
with an image/video, extract relevant original timestamp data.

Do not rely on the JSON filename alone.

============================================================
APPLE / ICLOUD
============================================================

Support Apple/iCloud-style exports where metadata is embedded
in the image/video or provided through associated metadata.

Prioritize:

DateTimeOriginal
creation date
media creation date

over filesystem timestamps.

============================================================
WHATSAPP
============================================================

WhatsApp media often has filenames that may contain dates,
identifiers, or application-specific naming conventions.

Recognize common patterns such as:

IMG-YYYYMMDD-WAxxxx
VID-YYYYMMDD-WAxxxx

For example:

IMG-20240130-WA0001.jpg

should produce:

2024-01-30

SOURCE:

WHATSAPP_FILENAME

But do NOT assume every WhatsApp file has a reliable original
capture date.

============================================================
SCREENSHOTS
============================================================

Detect screenshot patterns from:

filename
metadata
directory

Examples:

Screenshot_2024-01-30-123456.png
Screenshot 2024-01-30 123456.png
Screen Shot 2024-01-30 at 12.34.56 PM.png

If a valid date is found in the filename, treat it as
SCREENSHOT_FILENAME evidence.

Do not confuse screenshot creation date with the date of the
content visible inside the screenshot.

Example:

A screenshot created on 2026-05-01 may contain a photo from 2024.

The organizer should organize the SCREENSHOT according to the
screenshot's own creation date unless stronger metadata explicitly
indicates otherwise.

============================================================
VIDEOS
============================================================

The system must support video files as a separate media type.

At minimum:

.mp4
.mov
.m4v
.avi
.mkv
.webm
.3gp

Create:

VideoMetadataExtractor

Support media creation metadata where technically available.

For MP4/MOV, inspect container metadata for creation timestamps.

Do NOT treat video filesystem modified date as the original
recording date when stronger media metadata exists.

============================================================
EDITED MEDIA
============================================================

A photo may have:

Original capture date:
2024-01-30

Edited:
2026-05-01

The system should attempt to distinguish:

CAPTURE_DATE
EDIT_DATE
DOWNLOAD_DATE
EXPORT_DATE
FILESYSTEM_DATE

Do not automatically use the newest timestamp.

The target organization date is:

ORIGINAL_MEDIA_DATE

when reliable evidence exists.

============================================================
MULTIPLE DATE TYPES
============================================================

The internal data model should support:

original_date
capture_date
creation_date
digitized_date
modified_date
export_date
download_date
filesystem_created
filesystem_modified

But the organizer must select:

organization_date

based on evidence.

============================================================
DATE EVIDENCE ENGINE
============================================================

Build a unified evidence pipeline:

                MEDIA FILE
                     |
        +------------+------------+
        |            |            |
       EXIF       FILENAME     SIDECAR
        |            |            |
        +------------+------------+
                     |
             APP SOURCE DETECTOR
                     |
        +------------+------------+
        |            |            |
    SOCIAL APP    CLOUD EXPORT   VIDEO META
        |            |            |
        +------------+------------+
                     |
              DATE EVIDENCE
                     |
              CONFLICT ENGINE
                     |
             CONFIDENCE ENGINE
                     |
             ORGANIZATION DATE

Every decision must be explainable.

============================================================
EVIDENCE RECORD
============================================================

Each date candidate should be represented as:

{
    "date": "2024-01-30",
    "source": "WHATSAPP_FILENAME",
    "confidence": "HIGH",
    "evidence": "IMG-20240130-WA0001.jpg"
}

Multiple candidates can exist.

Example:

[
    {
        "date": "2024-01-30",
        "source": "EXIF_DATETIME_ORIGINAL",
        "confidence": "VERY_HIGH"
    },
    {
        "date": "2024-01-30",
        "source": "FILENAME",
        "confidence": "HIGH"
    },
    {
        "date": "2026-05-01",
        "source": "FILESYSTEM_MODIFIED",
        "confidence": "LOW"
    }
]

Selected:

2024-01-30

============================================================
DO NOT OVERFIT TO KNOWN APPS
============================================================

The application must work even when the source application is
unknown.

Generic filename/date/metadata detection must always remain
available.

If no application-specific rule matches:

fall back to generic date intelligence.

============================================================
SOURCE DETECTION MUST NOT CONTROL DATE SELECTION
============================================================

CRITICAL:

Knowing that a file came from Snapchat does NOT automatically
mean the Snapchat-related date is correct.

Application detection is evidence.

Date selection is handled by the centralized date engine.

============================================================
DATE PRIORITY MODEL
============================================================

Use evidence rather than simplistic application-specific rules.

Example conceptual priority:

1. Original EXIF capture date
2. Reliable embedded creation date
3. Reliable cloud/export metadata
4. Strong filename date
5. Application-specific filename date
6. Parent-folder date
7. Filesystem creation date
8. Filesystem modified date

The implementation must allow this policy to evolve.

============================================================
SOCIAL MEDIA CONFLICT EXAMPLE
============================================================

File:

IMG-20240130-WA0001.jpg

EXIF:
2024-01-30

Filesystem:
2026-05-01

Expected:

organization_date:
2024-01-30

date_source:
EXIF_DATETIME_ORIGINAL

confidence:
VERY_HIGH

The filesystem date must be recorded as conflicting evidence.

============================================================
UNKNOWN / AMBIGUOUS CASE
============================================================

File:

download_938472.jpg

EXIF:
missing

Filename:
no date

Filesystem:
2026-05-01

Expected:

organization_date:
2026-05-01

confidence:
LOW

status:
REVIEW_RECOMMENDED

Do not pretend this is a high-confidence original date.

============================================================
MEDIA TYPE DETECTION
============================================================

Create:

app/services/media_detector.py

Detect:

IMAGE
VIDEO
UNKNOWN

Do not rely only on file extension.

Where practical, validate the actual file signature/content.

============================================================
THUMBNAIL PREVIEW
============================================================

For supported images/videos, the UI should display a thumbnail.

For videos:

show a representative frame where safely possible.

Do not load entire videos into memory.

============================================================
ADVANCED UI
============================================================

Add:

MEDIA SOURCE

Example:

WhatsApp
TikTok
Camera
Screenshot
Google Photos
Unknown

Add:

DATE EVIDENCE

Example:

EXIF
Filename
Google Photos Metadata
Filesystem

Add:

CONFIDENCE

VERY HIGH
HIGH
MEDIUM
LOW
REVIEW REQUIRED

============================================================
FILTERS
============================================================

Add filters:

All
Images
Videos
Camera
WhatsApp
Snapchat
TikTok
Instagram
Screenshots
Cloud Imports
Unknown
High Confidence
Conflicts
Review Required

============================================================
SEARCH
============================================================

Allow searching by:

filename
folder
date
source application
media type
confidence
status

Example:

Search:

WhatsApp

shows only WhatsApp-related media.

============================================================
REPORT
============================================================

Generate a report after organization.

Include:

Total media
Images
Videos
Dates detected
EXIF dates
Filename dates
Social-media detected
Cloud metadata detected
Filesystem fallback
Conflicts
Review required
Duplicates
Verified copies
Failed copies

============================================================
IMPORTANT PRIVACY REQUIREMENT
============================================================

Everything remains LOCAL.

Do not send photos or metadata to:

OpenAI
Google
Meta
TikTok
Snapchat
Microsoft
any third-party API

unless the user explicitly implements and enables such an
integration in a future version.

The V1 application must work completely offline.

============================================================
TESTING
============================================================

Create test cases for:

WhatsApp filename:

IMG-20240130-WA0001.jpg

Expected:
2024-01-30

TikTok-style filename containing a valid date.

Instagram-style filename containing a valid date.

Screenshot:

Screenshot_2024-01-30-123456.png

Expected:
2024-01-30

Google Photos-style media + associated JSON metadata.

Expected:
metadata date when association is reliable.

EXIF date + social filename date agree.

Expected:
HIGH/VERY_HIGH confidence.

EXIF date + social filename date conflict.

Expected:
DATE_CONFLICT.

Social filename date + filesystem date conflict.

Expected:
social filename evidence considered stronger.

No metadata + no valid filename date.

Expected:
filesystem fallback + LOW confidence.

============================================================
ARCHITECTURE REQUIREMENT
============================================================

Do NOT implement every social-media rule inside one huge file.

Use independent parser modules with a common interface.

Example:

class MediaDateProvider:

    def detect(self, media_file) -> list[DateEvidence]:
        ...

Providers:

ExifDateProvider
XmpDateProvider
FilenameDateProvider
GooglePhotosProvider
WhatsAppProvider
TikTokProvider
InstagramProvider
SnapchatProvider
FilesystemDateProvider

The DateEngine combines all providers.

============================================================
FINAL PRINCIPLE
============================================================

The system must answer:

"WHAT IS THE MOST RELIABLE DATE WE CAN ESTABLISH FOR THIS
MEDIA?"

NOT:

"When was this file copied to my computer?"

NOT:

"When was this file last modified?"

NOT:

"What date does Windows show?"

Every organization decision must be:

EVIDENCE → ANALYSIS → CONFIDENCE → DECISION → VERIFICATION

Never:

GUESS → COPY

============================================================
TESTING REQUIREMENTS
============================================================

NEVER test against my real photo collection.

Use temporary test directories.

Create test images with controlled metadata and filenames.

Test cases must include:

CASE 1:

Filename:
20240130_080421.jpg

Filesystem:
2026-05-01

Expected:
2024-01-30

Source:
FILENAME

Filesystem must NOT win.

CASE 2:

EXIF:
2024-01-30

Filename:
20240130_080421.jpg

Filesystem:
2026-05-01

Expected:
2024-01-30

Confidence:
VERY_HIGH

CASE 3:

EXIF:
2024-01-30

Filename:
20240131_080421.jpg

Expected:
DATE_CONFLICT

CASE 4:

No EXIF.

Filename:
20240130_080421.jpg

Filesystem:
2026-05-01

Expected:
2024-01-30

CASE 5:

No EXIF.
No valid filename date.

Filesystem:
2026-05-01

Expected:
2026-05-01

Source:
FILESYSTEM

Confidence:
LOW

CASE 6:

Folder:

GRADUATION/2024-01-30/

Expected:
Skip folder entirely.

CASE 7:

Nested:

FAMILY/TRIPS/KANDY/photo.jpg

Expected destination:

FAMILY/TRIPS/KANDY/YYYY-MM-DD/photo.jpg

CASE 8:

Run organizer twice.

Second run must not create:

YYYY-MM-DD/YYYY-MM-DD/

CASE 9:

Destination file already exists with same SHA-256.

Expected:

DUPLICATE_ALREADY_EXISTS

CASE 10:

Destination file exists with different SHA-256.

Expected:

NAME_CONFLICT

and safe renamed copy.

CASE 11:

Corrupted image.

Expected:

CORRUPTED_OR_UNREADABLE

Application continues.

============================================================
REALISTIC DATE TESTS
============================================================

Include realistic filenames:

IMG_20240130_080421.jpg
20240130_080427.jpg
IMG-20240130-WA0001.jpg
Screenshot_2024-01-30-123456.png
PXL_20240501_195944.jpg
20240617_164153.jpg
photo_20240723.jpg

All valid dates should be detected correctly.

============================================================
IMPORTANT DESIGN RULE
============================================================

Do NOT make filesystem timestamps the main date source.

The entire purpose of this project is to recover the most likely ORIGINAL PHOTO DATE from available evidence.

============================================================
NO GUESSING
============================================================

When evidence is insufficient:

DO NOT pretend the date is correct.

Use:

REVIEW_REQUIRED

or:

LOW_CONFIDENCE

instead.

============================================================
CODE QUALITY
============================================================

Use:

- type hints
- dataclasses/Pydantic models
- clear service boundaries
- small testable functions
- structured logging
- proper exception handling
- docstrings for complex logic
- no giant monolithic functions
- no duplicated date parsing logic

Do not hard-code paths.

Do not hard-code my personal folders.

============================================================
DEVELOPMENT PROCESS
============================================================

First inspect the EXISTING PROJECT.

Do not blindly overwrite working code.

Then refactor incrementally.

PHASE 1:
Analyze current project.

PHASE 2:
Implement date intelligence engine.

PHASE 3:
Implement filename date parser.

PHASE 4:
Implement date-folder exclusion.

PHASE 5:
Implement controlled recursive scanner.

PHASE 6:
Implement immutable organization planner.

PHASE 7:
Implement duplicate detection.

PHASE 8:
Implement safe copy + SHA-256 verification.

PHASE 9:
Implement review/conflict system.

PHASE 10:
Update FastAPI APIs.

PHASE 11:
Update frontend dashboard.

PHASE 12:
Implement logs/database.

PHASE 13:
Run complete automated tests.

PHASE 14:
Run a controlled real-world test using a COPY of a small subset of my photos.

PHASE 15:
Prepare Windows packaging.

============================================================
CRITICAL DEVELOPMENT RULE
============================================================

Do not modify my real photo collection while developing.

Do not run organization against my real folder automatically.

Always test with temporary directories first.

============================================================
START NOW
============================================================

Start by inspecting the existing project.

Do NOT make destructive changes.

Do NOT organize any real files.

Do NOT delete anything.

Report:

1. Existing architecture
2. Existing files
3. Existing API
4. Existing frontend
5. Existing date logic
6. Existing tests
7. Problems that must be fixed
8. Recommended migration plan

Then STOP and wait for confirmation.