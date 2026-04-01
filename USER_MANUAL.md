# FITS Database v2.3 - User Manual

**Complete Step-by-Step Guide for Managing Astrophotography FITS Observations**

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [User Interface](#user-interface)
3. [Essential Workflows](#essential-workflows)
4. [Advanced Features](#advanced-features)
5. [NINA Integration](#nina-integration)
6. [Troubleshooting](#troubleshooting)
7. [Tips & Best Practices](#tips--best-practices)

---

## Getting Started

### Installation

#### Option 1: Executable (Fastest - Windows Only)

```
1. Download FITS_Database.exe from releases
2. Double-click the file
3. Application launches immediately
4. No installation dialog, no setup required
```

**Advantages:**
- ✅ No Python installation needed
- ✅ Single file, portable
- ✅ Faster performance
- ✅ Professional Windows integration

#### Option 2: Python Source Code

**Requirements:**
- Python 3.7 or higher installed
- Command line access
- ~200 MB disk space for dependencies

**Steps:**

```bash
# Step 1: Clone or download the repository
git clone https://github.com/Toro7777/FITS_Database.git
cd FITS_Database

# Step 2: Install dependencies
pip install -r requirements.txt

# Step 3: Launch the application
python fits_gui_database.py
```

**Advantages:**
- ✓ Works on Windows, macOS, Linux
- ✓ Can modify source code
- ✓ Educational (see how it works)

### First Time Setup

1. **Launch the Application**
   - Executable: Double-click FITS_Database.exe
   - Python: Run `python fits_gui_database.py`

2. **Wait for Main Window**
   - Application initializes (may take 5-10 seconds)
   - Loads previous database if available
   - Displays empty tree on first run

3. **You're Ready!**
   - All features available
   - No additional setup needed
   - Ready to scan your FITS observations

---

## User Interface

### Main Window Layout

```
┌──────────────────────────────────────────────────────────────────┐
│ FITS Database v2.3                             [_] [□] [X]      │
├──────────────────────────────────────────────────────────────────┤
│ File   Edit   View   Tools   Help                                │
├──────────────────────────────────────────────────────────────────┤
│ [Select Directory] [Scan] [Export All as NINA JSON] [Syntax]    │
│ [Launch FITS Viewer]                                             │
├──────────────────────────────────────────────────────────────────┤
│ Search: [_________________________] [Advanced]                   │
├──────────────────────┬──────────────────────────────────────────┤
│                      │                                           │  
│  Database Tree       │  Details Panel                           │
│  📅 2026-01-15      │  ┌─ Observation Details ─────────────┐   │
│     📁 M31          │  │ Object: Andromeda Galaxy          │   │
│        🌟 Andromeda │  │ Coordinates: 00:42:44.3 / +41°16' │   │
│           📊 47 FITS│  │ Telescope: Newtonian 200mm        │   │
│        🌟 M33      │  │ Camera: ZWO ASI533MM-Pro          │   │
│           📊 28 FITS│  │ Filter: Ha (658nm)               │   │
│     🔧 Calibration │  │ Exposure: 300 seconds            │   │
│        📊 64 FLAT  │  │ Gain: 200 | Offset: 20           │   │
│                      │  │ Total Integration: 2h 45m 00s     │   │
│  📅 2026-01-14      │  │ First File: M31_Ha_001.fits       │   │
│  📅 2026-01-13      │  └──────────────────────────────────┘   │
│                      │                                           │
├──────────────────────┴──────────────────────────────────────────┤
│ Status: 847 FITS files loaded. Ready.        Database size: 12.3 MB
└──────────────────────────────────────────────────────────────────┘
```

### Component Breakdown

#### Top Toolbar

| Button | Function | Keyboard |
|--------|----------|----------|
| Select Directory | Choose folder to scan | Ctrl+O |
| Scan | Start scanning FITS files | Ctrl+S |
| Export All as NINA JSON | Export entire database | Ctrl+E |
| Syntax | Toggle dark/light theme | - |
| Launch FITS Viewer | Open FITS file viewer | Ctrl+F |

#### Search & Filter Bar

```
Search Box: Real-time filtering as you type
Supported searches:
  • "2026-01-15" → Find observations from this date
  • "M31" → Find object name or session
  • "Newtonian" → Find telescope
  • "Ha" → Find filter type
  • "300" → Find exposure time
```

#### Database Tree (Left Panel)

**Organization Hierarchy:**
```
Observation Date (Clickable, expandable)
├─ Session/Folder Name (Clickable)
│  ├─ Object Name (Clickable)
│  │  ├─ FITS File 1
│  │  ├─ FITS File 2
│  │  └─ ... more files
```

**Tree Navigation:**
- **Click Expand Arrow** → Show/hide nested items
- **Double-click Date** → Expand all observations for that date
- **Double-click Object** → Show details panel

#### Details Panel (Right)

Shows when you click an observation:
- Object name and coordinates
- Equipment information
- Exposure settings
- Integration time summary
- First FITS filename in sequence

#### Status Bar (Bottom)

```
Shows in real-time:
• Total FITS files loaded
• Database file size
• Current operation (scanning, exporting)
• Number of matches (during search)
```

### Menu Options

#### File Menu
```
├─ Select Directory   (Ctrl+O) - Choose folder with FITS files
├─ Open Recent        → Quick access to previous folders
├─ Scan              (Ctrl+S) - Start indexing FITS files
├─ Export Database   (Ctrl+D) - Save database backup
├─ Exit              (Ctrl+Q) - Close application
```

#### Edit Menu
```
├─ Clear Search       - Reset search box
├─ Reset Filters      - Clear all active filters
├─ Select All         - Select all entries
├─ Copy Info          - Copy details to clipboard
├─ Settings           - Application preferences
```

#### View Menu
```
├─ Increase Font Size    - Make text larger
├─ Decrease Font Size    - Make text smaller
├─ Dark Theme            - Switch to dark mode
├─ Light Theme           - Switch to light mode
├─ Show Status Bar       - Toggle status bar visibility
├─ Full Screen          (F11) - Maximize window
```

#### Tools Menu
```
├─ Export All as NINA JSON   - Batch export all observations
├─ Launch FITS Viewer        - Open FITS file viewer
├─ Read Image Metadata       - Analyze CSV data
├─ Compact Database          - Optimize database file size
├─ Generate Report           - Create statistics report
├─ Backup Database           - Manual database backup
```

#### Help Menu
```
├─ User Manual              (F1) - This manual
├─ Quick Reference          (F2) - Keyboard shortcuts
├─ Check for Updates            - Look for new version
├─ About FITS Database          - Version and credits
├─ Documentation Links          - Online resources
```

---

## Essential Workflows

### Workflow 1: Load and Organize Your FITS Library

**Scenario:** You have a folder with thousands of FITS files organized by date, and you want to catalog them.

**Steps:**

1. **Open FITS Database** (or it's already running)

2. **Click "Select Directory"** (or press Ctrl+O)
   ```
   Dialog appears: "Choose folder with FITS files"
   ```

3. **Choose Your Top-Level Observation Folder**
   ```
   Good structure:
   D:\Observations\
   ├─ 2026-01-15\
   │  ├─ M31_Session\
   │  │  ├─ M31_Ha_001.fits
   │  │  ├─ M31_Ha_002.fits
   │  │  └─ M31_Ha_003.fits
   │  └─ M33_Session\
   │     └─ M33_Ha_001.fits
   └─ 2026-01-14\
      └─ NGC_Session\
   ```

4. **Click "Scan"** (or press Ctrl+S)
   ```
   Progress indicator appears with:
   ✓ Files processed: 147/1,234
   ✓ Time elapsed: 2 minutes 15 seconds
   ✓ Estimated time remaining: 3 minutes
   ```

5. **Wait for Completion**
   ```
   When done:
   Status bar shows: "1,234 FITS files loaded. Ready."
   Tree populates with your observations
   ```

6. **Explore Your Database**
   ```
   • Click on dates to expand
   • Click on sessions to see objects
   • Click on objects to see file count
   • Details panel updates when you select items
   ```

**Result:** Your entire FITS library is now indexed and searchable!

### Workflow 2: Find a Specific Observation

**Scenario:** You remember photographing M31 in March, but need to find the exact session and retrieve the files.

**Steps:**

1. **Open Search Box**
   - Click in the search field at the top, or press Ctrl+F

2. **Type Search Query**
   ```
   Try: "M31"
   Or:  "2026-03"
   Or:  "Andromeda"
   ```

3. **Results Filter Instantly**
   ```
   Tree shows only matching observations:
   ✓ 2026-03-15 - M31 Session (matches "M31")
   ✓ 2026-03-20 - NGC 224 (M31 alternate name)
   ✗ 2026-03-22 - M33 Session (not matching, hidden)
   ```

4. **View Details**
   - Click matching entry to highlight
   - Details panel shows full information
   - See coordinates, telescope, filters, etc.

5. **Narrow Results Further**
   ```
   Add to search: "Ha"
   Now shows only M31 with Ha filter
   Much faster than scrolling!
   ```

**Pro Tip:** Search is instant - try filtering by multiple criteria:
- Date + Target: "2026-03 M31"
- Filter type: "Ha"
- Telescope: "Newtonian"

### Workflow 3: Export Observation to NINA Sequencer

**Scenario:** You want to run a follow-up observation of M31 in NINA, and want to import all the metadata from your database.

**Steps:**

1. **Find Your Observation** (See Workflow 2)
   ```
   Search and locate: M31 - 2026-01-15
   Select entry to highlight it
   ```

2. **Right-Click the Observation**
   ```
   Context menu appears:
   • View Details
   • Export as NINA JSON
   • Launch in FITS Viewer
   • Copy Path
   ```

3. **Select "Export as NINA JSON"**
   ```
   File save dialog appears
   Default name: M31_20260115.json
   ```

4. **Choose Save Location**
   ```
   Recommended: Desktop for easy access
   Or: NINA import folder if configured
   ```

5. **Click Save**
   ```
   JSON file created with:
   ✓ Target coordinates (RA/Dec)
   ✓ Observation equipment
   ✓ Filter and exposure settings
   ✓ Metadata notes
   ```

6. **Open NINA Desktop Application**
   ```
   NINA → File → New Sequence
   Or: Edit existing sequence
   ```

7. **Import the JSON File**
   ```
   NINA → Tools → Import Objects
   Select your M31_20260115.json file
   NINA loads all parameters automatically
   ```

8. **Run Your Observation**
   ```
   NINA now has:
   ✓ Exact target coordinates
   ✓ Your equipment configuration
   ✓ Proven exposure settings
   ✓ Filter choices
   Ready for automated imaging!
   ```

**Result:** Your entire imaging session is now in NINA, ready for follow-up observations!

### Workflow 4: View FITS File Details

**Scenario:** You want to inspect the FITS header of a specific observation to verify its metadata.

**Steps:**

1. **Select Observation in Tree**
   ```
   Click on any FITS file or object entry
   Details panel updates on right side
   ```

2. **Review Details Panel**
   ```
   Shows:
   • Object Name (from FITS OBJECT keyword)
   • Coordinates (RA/Dec)
   • Telescope and Camera
   • Filter Used
   • Exposure Time
   • Gain/Offset Settings
   • Date of Observation
   ```

3. **For More Detailed FITS Headers, Use FITS Viewer**
   ```
   Right-click observation
   Select "Launch in FITS Viewer"
   Full FITS header inspector opens
   ```

4. **In FITS Viewer, You Can See**
   ```
   ✓ All FITS keywords and values
   ✓ Image statistics
   ✓ Header comments
   ✓ Image preview/thumbnail
   ✓ Extension information
   ```

**Pro Tip:** FITS Viewer can also be launched standalone for exploring individual FITS files.

---

## Advanced Features

### Analyzing Image Metadata

**What is ImageMetaData Analysis?**
Some imaging software (like N.I.N.A.) can export CSV files with detailed metadata for each image taken in a session. FITS Database can parse and analyze these files.

**How to Use:**

1. **Gather CSV File**
   - Export from your imaging software (e.g., NINA → Export Session → CSV)
   - Place CSV file in observation folder
   - File naming: Optional, any name works

2. **Right-Click Session**
   ```
   Database tree → Find session
   Right-click → "Read Image Metadata"
   ```

3. **Analysis Results Display**
   ```
   Opens panel showing:
   • Total Images Captured
   • Average Exposure Time
   • Filter Breakdown (30% Ha, 25% SII, etc.)
   • Gain/Offset Statistics
   • Total Integration Time
   • Image Quality Metrics (if available)
   ```

4. **Supported Time Column Names**
   ```
   CSV column detection looks for:
   • ExposureStartUTC (NINA standard)
   • ExposureStart (Alternative format)
   • StartUTC (Some software)
   • Time (Generic)
   • Timestamp (Unix format)
   
   Automatically detects and uses first match found
   ```

**Example CSV Analysis Results:**

```
Session: M31 Ha Mapping - 2026-01-15
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Images:        127
Average Exposure:    240 seconds
Total Integration:   8 hours 32 minutes

Filter Breakdown:
  Ha (656nm):  87 images (68%)
  R:           40 images (32%)

Camera Settings:
  Avg Gain:    120
  Min Gain:    100, Max Gain:    140
  Offset:      20 (Constant)

Quality Metrics:
  Avg FWHM:    2.1 arcseconds
  Min FWHM:    1.8 arcseconds
```

### Bulk Export Operations

**What is Bulk Export?**
Instead of exporting one observation at a time, export your entire database at once.

**How to Use:**

1. **Click "Export All as NINA JSON"** Button (Top toolbar)
   ```
   Or: Tools → Export All as NINA JSON
   ```

2. **Choose Export Folder**
   ```
   Dialog appears: "Select export destination"
   Recommended: Create new "NINA_Exports" folder
   ```

3. **Choose Options**
   ```
   ☑ Include calibration frames
   ☑ Group by date
   ☑ Create index file
   Backup existing files
   ```

4. **Click Export**
   ```
   Progress indicator shows:
   ✓ Processing 847 FITS files
   ✓ Creating JSON exports: 245/847 (29%)
   ✓ Estimated time: 2 minutes
   ```

5. **Results**
   ```
   Export folder now contains:
   ├─ 2026-01-15_M31.json
   ├─ 2026-01-15_M33.json
   ├─ 2026-01-14_NGC_224.json
   ├─ ... (one file per observation)
   └─ INDEX.json (master index)
   ```

**Use These Exports:**
- ✅ Import into NINA sequencer
- ✅ Share with colleagues
- ✅ Backup observation data
- ✅ Archive in cloud storage

### Database Backup and Recovery

**Automatic Backup:**
- FITS Database auto-creates backup before major updates
- Stored as: `fits_database.backup.json`
- Last 10 backups retained

**Manual Backup:**

```
File → Export Database

Creates: fits_database_2026_01_15_143025.json
Backup contains: All observations indexed
Size: Typically 5-50 MB depending on catalog size
```

**Recovery:**

If something goes wrong:

```
1. Close FITS Database
2. Navigate to: F:\Documentos\Python\FITS_Database\
3. Locate: fits_database.backup.json
4. Copy to: fits_database.json (overwrite)
5. Restart FITS Database
6. Database restored to backup state
```

### Database Maintenance

**Compact Database** (Tools → Compact Database)
```
Removes unused entries
Optimizes file size
Rebuilds indexes
Takes: 5-30 seconds (depending on size)
Do weekly for best performance
```

**Verify Integrity** (Tools → Verify Database)
```
Checks for:
• Damaged entries
• Missing files
• Invalid coordinates
• Orphaned records

Reports issues and offers repair options
```

---

## NINA Integration

### Understanding NINA JSON Export Format

FITS Database exports observations in a format that NINA's sequencer can natively import.

**Exported JSON Structure:**

```json
{
  "$type": "Nightingale.Sequencer.SequenceEntity.DeepSkyObject",
  "$id": "DSO_M31_20260115",
  "Name": "M31 Session",
  "TargetName": "M31",
  "Description": "Andromeda Galaxy - Wide field imaging session",
  "InputCoordinates": {
    "RAHours": 0.7123456,
    "DecDegrees": 41.2690,
    "NegativeDec": false
  },
  "Metadata": {
    "Telescope": "Newtonian 200/1000mm",
    "Camera": "ZWO ASI533MM-Pro",
    "Filter": "Ha (656nm)",
    "ExpTime": 300,
    "Gain": 200,
    "Offset": 20,
    "Notes": "Focus achieved. Seeing 2.1\" FWHM"
  }
}
```

### Importing into NINA

**Step-by-Step:**

1. **Export from FITS Database** (see Workflow 3)
   - Right-click observation → Export as NINA JSON
   - Save file with descriptive name

2. **Open NINA Sequencer**
   - Start NINA desktop application
   - Open Sequencer interface

3. **Create New Observation**
   ```
   Sequencer → File → New Observation
   Or: Edit → ImportDeepSkyObject
   ```

4. **Import JSON**
   ```
   Click "Import" button
   Select exported JSON file from Step 1
   ```

5. **NINA Auto-Populates**
   ```
   ✓ Target Name: M31
   ✓ Coordinates: Exact RA/Dec
   ✓ Equipment: Your telescope/camera
   ✓ Settings: Exposure, gain, offset
   ✓ Notes: Session information
   ```

6. **Configure Sequence** (Optional)
   ```
   Add dither pattern
   Set focus check intervals
   Configure plate solving
   Add filter wheel automation
   ```

7. **Run Observation**
   ```
   Sequence → Start
   NINA uses all your saved parameters
   Automated imaging begins!
   ```

**Benefits of This Workflow:**
- ✅ Consistent equipment settings
- ✅ Proven exposure lengths
- ✅ Exact target coordinates
- ✅ Complete data transfer
- ✅ Zero manual entry needed

---

## Troubleshooting

### Common Issues and Solutions

#### Issue 1: "No FITS Files Found"

**Symptoms:**
- Scan completes but database is empty
- Tree shows nothing even though folder contains FITS files

**Possible Causes & Solutions:**

1. **Wrong Folder Structure**
   ```
   ✗ Wrong:
   D:\M31_Ha_001.fits      (FITS in root)
   D:\M31_Ha_002.fits

   ✓ Correct:
   D:\2026-01-15\M31/M31_Ha_001.fits   (Organized by date)
   ```
   **Fix:** Reorganize files into date/target folders

2. **FITS Extension Case Sensitive (Linux)**
   ```
   ✗ Won't match: M31_Ha.FIT (uppercase)
   ✓ Works: M31_Ha.fits (lowercase)
   ```
   **Fix:** On Linux, rename extensions to lowercase

3. **Hidden System Folders**
   ```
   May skip: $RECYCLE.BIN, ~temp, .hidden
   ```
   **Fix:** Use tools to show hidden files if needed

4. **Insufficient Permissions**
   ```
   Windows: Some folders require admin access
   ```
   **Fix:** Run FITS_Database as Administrator

**Testing:**
```
1. Place 1 FITS file in: D:\test\2026-01-15\test.fits
2. Try scanning just that folder
3. If it works, original folder has structural issue
```

#### Issue 2: FITS Viewer Won't Open

**Symptoms:**
- Click "Launch FITS Viewer" button, nothing happens
- Or error message appears

**Possible Causes & Solutions:**

1. **FITS_Viewer Folder Missing**
   ```
   Check: F:\Documentos\Python\FITS_Database\FITS_Viewer\
   Should contain: fits_viewer.py (and dependencies)
   ```
   **Fix:** Reinstall or restore FITS_Viewer folder

2. **Python Not In PATH** (Source version only)
   ```
   Test: Open PowerShell
   Type: python --version
   If error: Python not in PATH variable
   ```
   **Fix:** Reinstall Python, check "Add Python to PATH"

3. **Library Installation Missing**
   ```
   Python needs: matplotlib, numpy, astropy
   ```
   **Fix:** Run: `pip install matplotlib numpy astropy pillow`

4. **Port Already In Use** (Network version)
   ```
   FITS Viewer runs on port 5000 (default)
   If another app uses it: conflict occurs
   ```
   **Fix:** Close other applications or configure different port

**Testing:**
```
From PowerShell:
cd F:\Documentos\Python\FITS_Database\FITS_Viewer
python fits_viewer.py

If it launches from command line, UI integration issue
If error occurs, missing dependencies
```

#### Issue 3: NINA JSON Export Fails

**Symptoms:**
- Export button does nothing
- Or error: "Could not write file"

**Possible Causes & Solutions:**

1. **Missing RA/Dec Coordinates**
   ```
   FITS file must have: RA and DEC keywords
   Not all software writes these
   ```
   **Fix:** Check FITS header with external tool
   Manually add if missing

2. **Write Permission Denied**
   ```
   Export folder is read-only
   ```
   **Fix:** Choose different destination folder
   Desktop, Documents, or user-created folders

3. **Disk Space Full**
   ```
   JSON file needs space to write
   ```
   **Fix:** Free up disk space
   Check available space: Properties → Storage

4. **Filename Contains Invalid Characters**
   ```
   ✗ Cannot use: < > : " / \ | ? *
   ```
   **Fix:** Export with simpler name (e.g., M31_session.json)

**Testing Export:**
```
1. Try exporting to Desktop
2. If successful there, permission issue elsewhere
3. If fails on Desktop, coordinate or disk issue
```

#### Issue 4: Database Slow with Large Collections

**Symptoms:**
- Searching takes several seconds
- Scrolling through tree is sluggish
- Application feels unresponsive

**Solutions for 10,000+ Files:**

1. **Use Executable Version**
   ```
   Compiled version: ~3x faster
   Download: dist/FITS_Database.exe
   ```

2. **Reduce Active Database**
   ```
   Archive old observations to separate folder
   12 months → separate "Archive_2025" folder
   Reduces active size significantly
   ```

3. **Use Search Before Browsing**
   ```
   Instead of: Scrolling through all 10,000 files
   Better: Search first (instant filter)
   Result: Browse only matched entries
   ```

4. **Compact Database Weekly**
   ```
   Tools → Compact Database
   Takes: 10-30 seconds
   Improves: Search speed by 20-40%
   ```

5. **Add More RAM**
   ```
   Minimum: 4 GB
   Recommended: 8+ GB for very large collections
   ```

**Performance Benchmark:**
```
Database Size    |  Search Time  |  Scan Time
────────────────────────────────────────────
1,000 files      |  <100ms       |  1 minute
5,000 files      |  200-300ms    |  5 minutes
10,000 files     |  400-600ms    |  10 minutes
50,000 files     |  1-2 seconds  |  30+ minutes
```

#### Issue 5: Wrong Observations Being Matched in Search

**Symptoms:**
- Searching for "M31" shows observations that don't mention M31
- Too many unrelated results

**Solutions:**

1. **Use More Specific Search**
   ```
   Instead of: "M31"
   Better: "2026-01 M31" (adds date)
   Or: "M31 Ha" (adds filter)
   Result: Much narrower matches
   ```

2. **Check Search Scope**
   ```
   View → Search Options
   Uncheck fields you don't want searched:
   ☐ Search object names
   ☑ Search telescope details
   ☑ Search notes
   ```

3. **Use Advanced Search**
   ```
   Click [Advanced] button
   Specify exact fields to search:
   Object = "M31"
   Filter = "Ha"
   Date >= "2026-01-01"
   Date <= "2026-01-31"
   Result: Precise matching
   ```

---

## Tips & Best Practices

### Best Practice 1: Folder Organization

**Why It Matters:**
- FITS Database works best with organized folders
- Makes searching and finding observations easier
- Improves scanning performance

**Recommended Structure:**

```
D:\Observations\                    (Root)
├─ 2026-01-15\                      (Observation Date - YYYYMMDD)
│  ├─ M31_Ha\                       (Target - Session Folder)
│  │  ├─ M31_Ha_001.fits
│  │  ├─ M31_Ha_002.fits
│  │  └─ M31_Ha_metadata.csv        (Optional: Metadata export)
│  ├─ M33_RGB\
│  │  ├─ M33_R_001.fits
│  │  ├─ M33_G_001.fits
│  │  └─ M33_B_001.fits
│  └─ Calibration\                  (Keep calibration frames grouped)
│     ├─ Flats\
│     ├─ Darks\
│     └─ Bias\
├─ 2026-01-14\
│  ├─ NGC224\
│  └─ ...
└─ Archive\                         (Old observations - separate)
   ├─ 2025-12\
   ├─ 2025-11\
   └─ ...
```

**Naming Conventions:**

```
FITS Files:
  GOOD: M31_Ha_300s_001.fits        (Object_Filter_Exposure_Number)
        Andromeda_R_001.fits        (Object_Filter_Number)
  AVOID: file123.fits               (Too generic)
         m31_ha.fits                (Ambiguous)

Session Folders:
  GOOD: M31_Ha_Mapping
        NGC224_RGB
        Calibration
  AVOID: Session1                   (Not descriptive)
         Data                       (Too vague)
```

### Best Practice 2: Regular Backups

**Backup Strategy:**

```
Weekly:
  Tools → Export Database
  Save to: External drive or cloud storage
  e.g., Google Drive, OneDrive, USB drive

Monthly:
  Tools → Backup Database
  Create full backup archive
  Store offsite (cloud or external location)

Annually:
  Create master archive
  Store with observation data
  Document for archival
```

**Three-2-1 Backup Rule:**
```
Keep 3 copies of important data:
  • Original (F:\Documentos\Python\FITS_Database\fits_database.json)
  • Local backup (External USB drive)
  • Off-site backup (Cloud storage)
```

### Best Practice 3: Naming Observations for Easy Searching

**Problem:**
```
FITS files with generic names:
  object_001.fits, object_002.fits
You forget what filter, exposure, etc.
```

**Solution - Use Descriptive Names:**

```
Format: {Object}_{Filter}_{ExposureTime}_{Sequence}.fits

Examples:
  M31_Ha_300s_001.fits       (Ha filter, 300s exposure)
  M31_Ha_300s_002.fits       (Same, sequence 2)
  M31_R_180s_001.fits        (Red, 180s exposure)
  M33_Ha_240s_001.fits       (Different object)
  Calibration_Flat_Ha_001.fits (Calibration frame)

Benefits:
  ✓ Searchable in database ("Ha", "300s")
  ✓ Quick identification of exposure type
  ✓ Helps with automation ("All Ha 300s")
  ✓ Professional documentation
```

### Best Practice 4: Metadata CSV Usage

**When to Export CSV:**
- NINA automatically logs all imaging information
- Export at end of imaging session
- Place in same folder as FITS files

**How to Use:**

```
In NINA:
  1. End imaging session
  2. File → Export Session → CSV
  3. Save to: F:\Observations\2026-01-15\M31_Ha\

In FITS Database:
  1. Scan folder (FITS files + CSV loaded)
  2. Right-click session
  3. "Read Image Metadata"
  4. View comprehensive analysis
```

**What You Get:**
```
✓ Individual exposure times
✓ Filter usage breakdown
✓ Camera gain/offset per frame
✓ Acquisition timestamps
✓ Integration totals
✓ Quality metrics (if recorded)
```

### Best Practice 5: Efficient Searching

**Search Tips:**

```
Fast Searches (Sub-second):
  • "2026-01"              (Month - very specific)
  • "M31"                  (Object name)
  • "Ha"                   (Filter)
  • "300"                  (Exposure time)

Slow Searches (Multiple seconds):
  • "imaging"              (Generic word in many files)
  • "2026"                 (Entire year - broad)
  • Special characters     (May require escaping)

Pro Tips:
  ✓ Date filter first, then specific term
  ✓ Use object catalog numbers (M31, NGC224)
  ✓ Include filter names (Ha, SII, RGB)
  ✗ Avoid very common words
  ✗ Don't search for generic terms
```

### Best Practice 6: NINA Workflow Optimization

**Recommended Process:**

```
1. Week Before Observation
   └─ Export last year's observations to NINA
     └─ Review proven settings
     └─ Confirm coordinates

2. Night Before Observation
   └─ Create NINA sequence from database export
   └─ Add focus checks and dithering
   └─ Test all equipment

3. Night of Observation
   └─ Run NINA automation using imported targets
   └─ Collect CSV metadata during session

4. Night After Observation
   └─ Move FITS files to organized folders
   └─ Place CSV metadata in same folder
   └─ Scan into FITS Database
   └─ Export for future reference
```

### Best Practice 7: Performance Optimization

**Keep Database Fast:**

```
Do This:
  ✓ Weekly: Tools → Compact Database
  ✓ Monthly: Archive old observations to separate folder
  ✓ Quarterly: Verify database integrity
  ✓ Annually: Create full backup/export

Don't Do This:
  ✗ Leave thousands of duplicate entries
  ✗ Store entire life archive in active database
  ✗ Never optimize or maintain database
  ✗ Keep temporary files mixed with permanent data
```

**Maintenance Schedule:**

```
Daily:
  • Use application as normal

Weekly:
  • Compact database (1 minute)
  • Review recent scans

Monthly:
  • Export backup to external drive
  • Archive old observations (if >5,000 files)

Quarterly:
  • Verify database integrity
  • Check for orphaned entries
  • Update FITS Database (if new version available)

Annually:
  • Create complete archive
  • Document all observations
  • Review folder structure organization
```

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| **Ctrl+O** | Select Directory |
| **Ctrl+S** | Scan FITS Files |
| **Ctrl+F** | Focus on Search Box |
| **Ctrl+E** | Export All as NINA JSON |
| **Ctrl+D** | Export Database |
| **Ctrl+Q** | Quit Application |
| **F1** | Open User Manual |
| **F2** | Quick Reference (keyboard shortcuts) |
| **F11** | Toggle Fullscreen |
| **Arrow Keys** | Navigate tree items |
| **Enter** | Expand/collapse selected item |
| **Delete** | Clear selection |
| **Ctrl+A** | Select all visible items |
| **Ctrl+C** | Copy selected item path |
| **Ctrl+Z** | Undo (last operation) |

---

## Conclusion

**FITS Database Makes Astrophotography Easier:**

- 📚 Organize thousands of observations
- 🔍 Find exactly what you're looking for
- 🎯 Export to NINA automatically
- 📊 Analyze imaging sessions
- 💾 Backup your observation library

**Next Steps:**

1. Start scanning your FITS library
2. Export your first observation to NINA
3. Try analyzing your metadata
4. Share your observations with the astronomy community!

**Questions?**
- Check the Help menu in FITS Database
- Review the README.md for quick reference
- See NINA_INTEGRATION.md for sequencer-specific topics

---

Happy observing! 🔭✨

**FITS Database v2.3 - Professional Astrophotography Cataloging**
