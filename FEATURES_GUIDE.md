# FITS Database v2.3 - Features Guide

**Complete Reference for All Features and Capabilities**

---

## Table of Contents

1. [Database Management](#database-management)
2. [Search & Filtering](#search--filtering)
3. [FITS Viewer Integration](#fits-viewer-integration)
4. [NINA Sequencer Export](#nina-sequencer-export)
5. [Image Metadata Analysis](#image-metadata-analysis)
6. [Data Export & Backup](#data-export--backup)
7. [User Preferences](#user-preferences)
8. [Advanced Options](#advanced-options)

---

## Database Management

### Folder Scanning

**Purpose:** Index FITS files from a folder into the searchable database.

**How to Use:**
```
1. Click "Select Directory" button
2. Navigate to folder containing FITS observations
3. Click "Scan" button
4. Progress indicator shows scanning status
5. Results appear in hierarchical tree when complete
```

**What Gets Scanned:**
- ✅ FITS files (.fits, .fit, .fts, .fits.gz)
- ✅ FITS headers (coordinates, object, filter, etc.)
- ✅ Folder structure (date organization)
- ✅ Related CSV metadata files
- ✗ Non-FITS files (ignored safely)

**Database Tree Organization:**

```
Observation Date (YYYY-MM-DD)
├─ Session/Folder Name
│  ├─ Object Name
│  │  ├─ FITS File 1
│  │  ├─ FITS File 2
│  │  └─ FITS File 3
│  └─ Calibration Frames
│     ├─ Flat_Ha_001.fits
│     ├─ Dark_60s_001.fits
│     └─ Bias_001.fits
```

**Auto-Extraction of Metadata:**

From each FITS file header, FITS Database automatically extracts:

| FITS Keyword | Extracted As | Used For |
|---|---|---|
| OBJECT | Object Name | Identification |
| TELESCOP | Telescope | Equipment tracking |
| INSTRUME | Camera | Equipment tracking |
| FILTER | Filter Type | Search/organization |
| EXPTIME | Exposure Time | Statistics |
| GAIN | Gain Value | Camera settings |
| OFFSET | Offset Value | Camera settings |
| RA / DEC | Coordinates | NINA export |
| DATE-OBS | Observation Date | Timeline organization |
| IMAGETYP | Frame Type | Light/Dark/Flat classification |

### Tree Navigation

**Expanding/Collapsing:**
```
Single Click → Select item (highlights)
Double Click → Toggle expand/collapse
Arrow Key → Navigate up/down
Right Arrow → Expand selected
Left Arrow → Collapse selected
```

**Tree Context Menu** (Right-click any item):
```
├─ View Details        → Show details panel
├─ Export as NINA JSON → Single file export
├─ Launch in FITS Viewer → Open viewer with folder
├─ Read Image Metadata → Analyze CSV data
├─ Copy Path          → Copy file path to clipboard
└─ Delete Entry       → Remove from database
```

**Batch Operations:**
```
Ctrl+A → Select all visible entries
Ctrl+Click → Multi-select items
Shift+Click → Select range
Right-click selection → Apply action to all selected
```

---

## Search & Filtering

### Basic Search

**Access:**
- Click in search box at top of window
- Press Ctrl+F
- Start typing immediately

**Supported Search Terms:**

```
What You Search | What It Finds | Examples
────────────────────────────────────────────
Date Range     | Observations by date | "2026-01"
               |                       | "2026-01-15"
               |                       | "January"

Object Names   | Target names | "M31"
               |              | "Andromeda"
               |              | "NGC"
               |              | "UGC"

Telescopes     | Equipment used | "Newtonian"
               |                | "Refractor"
               |                | "RC"

Filters        | Filter types | "Ha"
               |              | "SII"
               |              | "OIII"
               |              | "RGB"
               |              | "Mono"

Exposure Info  | Timing & settings | "300" (300s)
               |                    | "gain 200"
               |                    | "offset 30"

Geographic     | Sky regions | "M31"
               |            | "Leo"
               |            | "Cygnus"
```

**Search Behavior:**

```
As You Type:
• Results filter instantly
• No need to press Enter
• Matches highlighted as typed

Clear Search:
• Click X in search box
• Press Escape
• Or: Edit → Clear Search
```

**Case Sensitivity:**
- ✓ Case-insensitive by default
- "M31", "m31", "M31" all work the same
- Special character handling: Automatic

### Advanced Search/Filtering

**Access:** Click [Advanced] button next to search box

**Advanced Options:**

```
Search Within:
☑ Object Names
☑ Telescope Info
☑ Filter Types  
☑ File Names
☑ Notes/Metadata

Filter By:
• Date Range:    From _____ To _____
• Exposure Time: Min _____ Max _____ seconds
• Gain Range:    Min _____ Max _____
• Object Type:   DropDown (NGC, M, UGC, Other)

Results:
• Match ALL criteria (AND)
• Match ANY criteria (OR)
• Case sensitive search
• Whole words only
```

**Example Advanced Searches:**

```
Find all Ha observations from January 2026:
  Date Range: 2026-01-01 to 2026-01-31
  Filter: "Ha"
  Result: All January Ha sessions

Find all 300-second exposures:
  Exposure: Min 300, Max 300
  Result: Only 300s exposures

Find all Newtonian observations:
  Telescope: Contains "Newtonian"
  Result: Only Newtonian telescope data
```

### Managing Search History

**Search History:**
- Last 20 searches automatically saved
- Click dropdown arrow in search box to view history
- Click any previous search to re-run

**Saving Searches:**
```
1. Perform your search
2. Click "Save Search" button
3. Give it a name: "January M31 Ha"
4. Saved searches appear in Tools menu
5. Reuse anytime with one click
```

**Search Functions:**

| Operation | Method |
|---|---|
| Clear search | Click X, press Escape, or Edit → Clear Search |
| Advanced filter | Click [Advanced] button |
| Search history | Click ▼ in search box |
| Save search | Click "Save" after searching |
| View saved searches | Tools → Saved Searches |

---

## FITS Viewer Integration

### Launching FITS Viewer

**Method 1: From Context Menu (Auto-Load Folder)**
```
1. Find observation in tree
2. Right-click
3. Select "Launch in FITS Viewer"
4. Viewer opens with folder pre-loaded
5. Select which FITS file to view
```

**Method 2: Toolbar Button (Standalone)**
```
1. Click "Launch FITS Viewer" button (top toolbar)
2. Browser window opens
3. Navigate and select folder manually
4. Choose FITS file to inspect
```

**Method 3: Command Line (Advanced)**
```bash
python FITS_Viewer/fits_viewer.py
# Opens empty viewer, user selects folder

python FITS_Viewer/fits_viewer.py --folder "D:\M31\"
# Viewer opens with folder pre-loaded
```

### FITS Viewer Capabilities

**What FITS Viewer Shows:**

```
Header Information:
├─ All FITS keywords and their values
├─ Data type and dimensions
├─ Extension information
└─ Comment field values

Statistics:
├─ Image min/max/mean values
├─ Pixel statistics
├─ Histogram
└─ Data range analysis

Preview:
├─ Image thumbnail
├─ Contrast adjustment
├─ Zoom in/out
└─ Pan around image
```

**Viewing FITS Headers:**

```
1. Select FITS file in viewer
2. Header information displays
3. Edit capability for some keywords
4. Export header to text file
5. Copy specific keywords
```

**Features:**

| Feature | Function |
|---|---|
| Thumbnail Preview | Quick image inspection |
| Header Editing | Modify FITS keywords (if needed) |
| Extension Browser | View multi-extension FITS files |
| Histogram | Visualize pixel distribution |
| Statistics | Calculate image metrics |
| Export | Save header as text file |

### FITS File Support

**Supported Formats:**
- ✅ Single-extension FITS (.fits)
- ✅ Multi-extension FITS (.fits)
- ✅ Compressed FITS (.fits.gz)
- ✅ Various FITS variants (.fit, .fts)

**Image Types Recognized:**
- ✓ Light Frames (Science images)
- ✓ Flat Fields (Calibration)
- ✓ Bias Frames (Calibration)
- ✓ Dark Frames (Calibration)
- ✓ Bias+Dark Frames (Combined calibration)

---

## NINA Sequencer Export

### Single File Export

**Purpose:** Export one observation to NINA JSON format for automated imaging.

**Steps:**
```
1. Find observation in database
2. Right-click on entry
3. Select "Export as NINA JSON"
4. File save dialog appears
5. Choose save location
6. Click Save
7. JSON file created with observation data
```

**What Gets Exported:**

```
Target Information:
✓ Object name
✓ RA/Dec coordinates (decimal degrees)
✓ Coordinate epoch
✓ Proper motion (if available)

Equipment Configuration:
✓ Telescope name
✓ Camera/Instrument
✓ Focal length
✓ Pixel scale

Observation Settings:
✓ Filter(s) used
✓ Exposure time
✓ Gain and Offset values
✓ Binning (if applicable)
✓ Number of exposures (estimated)

Additional Metadata:
✓ Observation notes
✓ Date/time observed
✓ Sky conditions
✓ Custom tags
```

### Bulk Export (All Observations)

**Purpose:** Export entire database to NINA JSON format in one operation.

**Steps:**
```
1. Click "Export All as NINA JSON" button (top toolbar)
   Or: Tools → Export All as NINA JSON
2. File browser opens
3. Choose destination folder for exports
4. Click Select Folder
5. Progress indicator shows:
   - Files processed: X/Total
   - Time elapsed
   - Estimated time remaining
6. Upon completion, folder contains JSON files
```

**Output Structure:**

```
Export_Folder\
├─ 2026-01-15_M31.json
├─ 2026-01-15_M33.json
├─ 2026-01-14_NGC224.json
├─ 2026-01-14_Calibration.json
├─ ...
└─ INDEX.json (Master index of all exports)
```

**INDEX.json Contents:**

```json
{
  "export_date": "2026-01-20T143025",
  "total_exports": 127,
  "nina_version": "2.0+",
  "observations": [
    {
      "filename": "2026-01-15_M31.json",
      "object": "M31",
      "date": "2026-01-15",
      "coordinates": "00:42:44.3 +41:16:09"
    },
    ...
  ]
}
```

### JSON File Format

**Structure of Exported File:**

```json
{
  "$type": "Nightingale.Sequencer.SequenceEntity.DeepSkyObject",
  "$id": "DSO_M31_20260115",
  "Name": "M31 - 2026-01-15",
  "TargetName": "M31",
  "Description": "Andromeda Galaxy wide-field imaging",
  "Notes": "Best seeing night. Image quality 2.1\" FWHM",
  "InputCoordinates": {
    "RAHours": 0.7123,
    "DecDegrees": 41.269,
    "NegativeDec": false,
    "Epoch": 2000.0
  },
  "Offset": {
    "RAArcseconds": 0,
    "DecArcseconds": 0
  },
  "ImageGeometry": {
    "Rotation": 0
  },
  "ReferenceBrightness": {
    "Brightness": 100
  },
  "Equipment": {
    "Telescope": "Newtonian 200/1000mm",
    "Camera": "ZWO ASI533MM-Pro",
    "Filter": "Ha (656nm)",
    "FocalLength": 1000
  },
  "ObservationSettings": {
    "ExposureTime": 300,
    "Gain": 200,
    "Offset": 20,
    "Count": 35,
    "TotalIntegration": 10500
  },
  "Metadata": {
    "FiltersUsed": ["Ha", "R", "G", "B"],
    "AverageExposure": 300,
    "IntegrationTotal": "2h 45m",
    "SessionNotes": "Prime focus, manual focus"
  }
}
```

### Importing into NINA

**NINA Sequencer Import:**

```
NINA Desktop Application → Sequencer Interface
↓
File → Import Objects (or Edit → Import DeepSkyObject)
↓
Select JSON file exported from FITS Database
↓
NINA Parses File and Auto-Populates:
  √ Target name and coordinates
  √ Equipment configuration
  √ Camera settings (gain, offset)
  √ Exposure parameters
  √ Filter selections
↓
Configure Additional Sequence Parameters:
  • Autofocus intervals
  • Dithering pattern
  • Plate solving settings
↓
Start Automated Imaging Sequence
```

---

## Image Metadata Analysis

### What is Image Metadata?

**Definition:** Detailed information about each image captured during an imaging session, typically logged by imaging software like NINA.

**Why Useful:**
- Verify imaging statistics after session
- Track which filters were used most
- Verify exposure times and camera settings
- Identify sessions with issues
- Plan future observations based on data

### CSV Format Requirements

**Supported Column Names for Time:**
```
Auto-detected (checks in this order):
1. ExposureStartUTC (NINA standard)
2. ExposureStart (Alternative)
3. StartUTC (Some software)
4. Time (Generic)
5. Timestamp (Unix format)

First match found is used
```

**Required Columns (at minimum):**
```
Date Column
+ Time Column  (one of the above)
= Complete timestamp

Optional but useful:
Filter, Exposure, Gain, Offset, Quality, FWHM
```

### How to Create Metadata CSV

**From NINA:**
```
1. End imaging session in NINA
2. File → Export Session
3. Choose "CSV Format"
4. Select location: Same folder as FITS files
5. CSV file created with detailed image logs
```

**Filename Convention (Optional):**
```
Good: M31_Ha_metadata.csv (describes contents)
Good: session_data.csv
Good: session.csv
Bad: file.csv (too generic)
```

### Analyzing Metadata

**Steps:**

```
1. Right-click session in FITS Database tree
2. Select "Read Image Metadata"
3. Analysis panel opens
4. Results display:
   • Total images from CSV
   • Statistics breakdown
   • Filter usage
   • Camera settings
```

**Analysis Output:**

```
Session: M31 Ha Survey - 2026-01-15
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Images:        147
Average Exposure:    240 seconds
Min Exposure:        180 seconds
Max Exposure:        300 seconds

Total Integration:   9 hours 48 minutes
Start Time:          20:32:15 UTC
End Time:            06:20:43 UTC (next day)

Filter Breakdown:
  Ha (656nm):  105 images (71%)
  R (700nm):    42 images (29%)

Camera Settings:
  Average Gain:        120
  Min Gain:           100
  Max Gain:           140
  Gain Changes:        2
  Offset:            20 (constant)

Session Quality:
  Average FWHM:        2.1 arcseconds
  Best FWHM:           1.8 arcseconds
  Cloudy Minutes:      0
  Mount Errors:        0
  Autofocus Runs:      8
```

### CSV Analysis Features

**Metrics Calculated:**
- Total frame count
- Per-filter frame counts
- Average/min/max exposure times
- Total integration time
- Camera gain/offset ranges
- Session duration
- Quality metrics (if logged)
- Auto-focus history
- Mount tracking errors

**Visual Display:**
- Bar charts for filter usage
- Time series for exposure settings
- Statistics summary
- Session timeline

---

## Data Export & Backup

### Database Export

**Purpose:** Create an external backup/archive of your entire database.

**Steps:**
```
1. File → Export Database
   Or: Tools → Backup Database
2. File save dialog appears
3. Choose destination and filename
4. Example: fits_database_20260115_backup.json
5. Click Save
6. Backup file created (5-50 MB depending on size)
```

**What's Included:**
- ✓ All indexed observations
- ✓ Complete metadata
- ✓ Search indexes
- ✓ Database configuration
- ✗ FITS file data (only indexes)

**File Size:**
- 1,000 observations: ~2-5 MB
- 5,000 observations: ~10-25 MB
- 10,000 observations: ~25-50 MB

### Automatic Backups

**Auto-Backup Features:**
```
✓ Auto-creates backup before major updates
✓ Stored as: fits_database.backup.json
✓ Last 10 backups automatically retained
✓ Scheduled daily (if enabled)
✓ Accessible from Tools → Database Recovery
```

**Backup Management:**
```
Tools → Database Management
├─ View Backups          → See all backups
├─ Restore Backup        → Recover from backup
├─ Delete Old Backups    → Clean up storage
└─ Backup Schedule       → Configure auto-backup
```

### CSV Export

**Purpose:** Export observation list as CSV for spreadsheet use.

**Steps:**
```
1. Select observations (or use search to filter)
2. Right-click selected items
3. Select "Export as CSV"
4. Choose save location
5. CSV file created with observation list
```

**CSV Columns:**
```
Date | Session | Object | Telescope | Camera | Filter | 
ExposureTime (sec) | Gain | Offset | RA | Dec | 
FileCount | IntegrationTime | Notes
```

### JSON Export

**Purpose:** Export database as JSON for programmatic access.

**Format:**
```json
{
  "metadata": {
    "export_date": "2026-01-20T143025",
    "database_version": "2.3",
    "total_observations": 847
  },
  "observations": [
    {
      "date": "2026-01-15",
      "session": "M31_Ha",
      "object": "M31",
      "telescope": "Newtonian 200mm",
      "files": 35,
      "...": "..."
    }
  ]
}
```

---

## User Preferences

### Appearance Settings

**Theme Selection:**
```
View → Dark Theme (modern dark interface)
View → Light Theme (traditional light interface)
```

**Font Size:**
```
View → Increase Font Size  (Ctrl++)
View → Decrease Font Size  (Ctrl+-)
View → Reset Font Size     (Ctrl+0)
```

**Window Settings:**
```
View → Remember Window Size    (auto-restore position)
View → Remember Window Position (auto-restore location)
View → Always on Top           (keep window above others)
View → Fullscreen Toggle       (F11)
```

### General Preferences

**Edit → Settings (or Preferences):**

```
Display:
☑ Show status bar
☑ Show tree icons
☑ Show file sizes
☑ Show timestamps

Behavior:
☑ Auto-scan on startup
☑ Remember last folder
☑ Compact database on exit
☑ Show notifications

Database:
☑ Auto-backup on save
☑ Keep 10 recent backups
Backup Interval: _____ minutes

Scanning:
☑ Index subdirectories
☑ Include calibration frames
☑ Skip very large files (>500 MB)
```

### Keyboard Shortcuts Configuration

**Edit → Keyboard Shortcuts:**
```
Customize keyboard bindings for any function
Save custom shortcuts profile
Import/Export shortcut configurations
```

**Preset Profiles:**
```
• FITS Database Standard
• Vim-style keys
• Emacs-style keys
• Mac-friendly keys
```

---

## Advanced Options

### Command-Line Arguments

**When Launching Application:**

```bash
# Launch with specific folder
python fits_gui_database.py --folder "D:\Observations"

# Launch and auto-scan
python fits_gui_database.py --auto-scan

# Launch with custom database file
python fits_gui_database.py --database "D:\archives\2025.json"

# Launch in headless mode (no GUI)
python fits_gui_database.py --headless --export-all

# Launch with verbosity
python fits_gui_database.py --verbose
python fits_gui_database.py --debug
```

### Configuration File

**Location:** `config.json` (in application directory)

**Contents:**

```json
{
  "default_folder": "D:\\Observations",
  "database_file": "fits_database.json",
  "auto_backup": true,
  "backup_interval": 3600,
  "keep_backups": 10,
  "fits_extensions": [".fits", ".fit", ".fts", ".fits.gz"],
  "nina_export_format": "v2.3",
  "theme": "light",
  "remember_last_folder": true,
  "remember_window_position": true,
  "auto_scan_on_startup": false,
  "timeout_seconds": 300,
  "max_file_size_mb": 500,
  "parallel_threads": 4
}
```

### Database Recovery

**Corrupted Database?**

```
1. Close FITS Database
2. Go to: F:\Documentos\Python\FITS_Database\
3. Find: fits_database.backup.json
4. Copy to: fits_database.json (overwrite existing)
5. Restart application
6. Database restored!
```

**Advanced Recovery:**

```
Tools → Database Tools → Verify & Repair
Checks for:
  ✓ Orphaned entries
  ✓ Missing files
  ✓ Invalid coordinates
  ✓ Duplicate entries
  
Option to auto-repair issues
```

### Performance Tuning

**For Large Databases (10,000+ files):**

```
Edit → Settings → Advanced
├─ Parallel Threads: Set to 4-8
├─ Cache Size: Increase for faster search
├─ Index Update Frequency: Adjust
├─ Preview Timeout: Increase if timing out
└─ Memory Limit: Set available RAM
```

**Optimization Steps:**
```
1. Tools → Compact Database (weekly)
2. Archive old observations (monthly)
3. Verify database integrity (quarterly)
4. Rebuild indexes (semi-annually)
```

---

## Summary Table

| Feature | Purpose | Access |
|---|---|---|
| **Database Scan** | Index FITS files | Select Directory → Scan |
| **Search** | Find observations | Ctrl+F or top search box |
| **Advanced Filter** | Complex searches | [Advanced] button |
| **FITS Viewer** | Inspect headers | Right-click → "Launch Viewer" |
| **NINA Export** | Export to automation | Right-click → "Export NINA" |
| **Bulk Export** | Export all at once | Button or Tools menu |
| **Metadata Analysis** | Analyze CSV data | Right-click → "Read Metadata" |
| **Database Backup** | Create backup | File → Export Database |
| **Preferences** | Customize settings | Edit → Settings |
| **Help** | User Manual | F1 or Help menu |

---

**For more details, see:**
- **USER_MANUAL.md** - Step-by-step workflows
- **QUICK_START.md** - Get started fast
- **README.md** - Project overview
- **BUILD_INSTRUCTIONS.md** - Compilation guide

---

Happy observing! 🔭✨
