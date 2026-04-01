# FITS Database Viewer - Distribution Checklist

## For Colleagues Testing

### Files Included in Package
```
FITS_Library/
├── fits_gui_database.py             (Main application)
├── fits_database.json               (Sample database)
├── FITS_Viewer/
│   ├── fits_viewer.py               (FITS file viewer)
│   └── [supporting files]
├── launch_fits_gui.bat              (Windows launcher)
├── INSTALL.bat                      (Dependency installer)
├── requirements.txt                 (Python package list)
├── DISTRIBUTION_README.md          (This distribution guide)
├── START_HERE.md                    (Quick start)
├── README.md                        (Detailed documentation)
└── [other documentation]
```

## Installation Steps for Colleagues

### Option 1: Automated Installation (Windows)
1. Extract the FITS_Library folder to desired location (e.g., `C:\Tools\FITS_Library`)
2. Double-click `INSTALL.bat`
3. Follow on-screen prompts (may take 2-3 minutes)
4. Once complete, double-click `launch_fits_gui.bat` to start

### Option 2: Manual Installation
1. Ensure Python 3.7+ is installed and in PATH
2. Open terminal/command prompt in FITS_Library folder
3. Run: `python -m pip install -r requirements.txt`
4. Launch: `python fits_gui_database.py`

### Option 3: Mac/Linux Installation
1. Ensure Python 3 is installed: `python3 --version`
2. Open terminal in FITS_Library folder
3. Run: `python3 -m pip install -r requirements.txt`
4. Launch: `python3 fits_gui_database.py`

## Quick Testing Workflow

### 1. First Launch
- **Expected**: GUI window opens with empty database
- **Controls**: All buttons enabled and visible
- **Status**: "Ready" shown in status bar

### 2. Test Database Scanning
- **Action**: Click "Scan & Save Database"
- **Select**: A folder containing FITS files
- **Expected**: 
  - Progress bar shows scanning progress
  - Once complete: database loads with observations
  - Status shows "Last scan: [timestamp]"

### 3. Test Database Functions
- **Search**: Type something in search box (e.g., "M101")
- **Sort**: Click column headers (expect ascending/descending toggle)
- **Details**: Double-click a row
- **Right-click**: On a row to see context menu options

### 4. Test ImageMetaData Analysis
- **Prerequisite**: Observation folder must contain ImageMetaData.csv
- **Action**: Right-click → "Read Image Metadata"
- **Expected**: Plot window opens showing available metrics
- **Advanced**: Try dragging time range sliders (if time data present)

### 5. Test FITS Viewer Integration
- **Option A**: Click "Launch FITS Viewer" button (blank launch)
  - Expect: FITS Viewer window opens, user picks folder
- **Option B**: Right-click observation → "Launch in FITS Viewer"
  - Expect: FITS Viewer opens with that folder pre-loaded

### 6. Test NINA JSON Export
- **Action 1** (Single): Right-click observation → "Export as NINA JSON"
  - Expect: Save dialog, creates JSON file
- **Action 2** (Batch): Click "Export All as NINA JSON"
  - Expect: Choose folder, exports all observations

### 7. Test CSV Export
- **Action**: Click "Export to CSV"
- **Expected**: File browser dialog, exports filtered view to CSV

## Feedback Checklist for Colleagues

Request feedback on these areas:

### Functionality
- [ ] Database scanning works
- [ ] Search filtering functions correctly
- [ ] Column sorting toggles ascending/descending
- [ ] ImageMetaData plotting displays metrics
- [ ] FITS Viewer launches from button
- [ ] FITS Viewer launches with folder-specific data
- [ ] NINA JSON export creates valid files
- [ ] CSV export works as expected

### Usability
- [ ] UI is intuitive
- [ ] Button layout is clear
- [ ] Right-click menu is useful
- [ ] Search interface is obvious
- [ ] Progress feedback is visible during scans

### Performance
- [ ] Database scan completes in reasonable time
- [ ] No frozen windows during operations
- [ ] Plots display smoothly
- [ ] FITS Viewer loads quickly

### Compatibility
- [ ] Works on their Windows version
- [ ] Works on their Mac (if applicable)
- [ ] Python installation process was clear
- [ ] No missing dependencies

### Data Handling
- [ ] Recognizes their FITS folder structure
- [ ] Extracts FITS headers correctly
- [ ] ImageMetaData CSV parsing works
- [ ] Coordinate extraction is accurate
- [ ] JSON exports are valid for NINA

## Package for Distribution

### Create Distribution Archive:

```powershell
# Windows PowerShell
Compress-Archive -Path "F:\Documentos\Python\FITS_Library" `
  -DestinationPath "FITS_Library_v2.3_Distribution.zip" `
  -Force
```

### Send to Colleagues:
1. Email the ZIP file with instructions to:
   - Extract to local drive (not network/cloud)
   - Run INSTALL.bat (Windows) or pip install from requirements.txt
   - Launch fits_gui_database.py

2. Include this checklist and a contact method for feedback

## Troubleshooting Support

### Common Issues and Solutions:

**"Python not found"**
- Solution: Download and install from https://www.python.org/
- Verify in terminal: `python --version`

**"Module not found" errors**
- Solution: Run INSTALL.bat again or: `pip install -r requirements.txt`

**Blank database after scan**
- Solution: Verify folder structure matches YYYY-MM-DD format
- Check that FITS files have .fits/.fit/.fts extension (case-insensitive)

**FITS Viewer won't launch**
- Solution: Verify FITS_Viewer folder exists in same directory as fits_gui_database.py
- Check that fits_viewer.py is present

**ImageMetaData won't plot**
- Solution: Verify CSV column names match supported names (see DISTRIBUTION_README.md)
- Check that CSV file is in observation folder
- Look at console output for column name hints

**NINA JSON import fails**
- Solution: Open generated JSON in text editor
- Verify it matches expected NINA DeepSkyObjectContainer format
- Check that RA/DEC coordinates are present

## Version Information

- **Application**: FITS Database Viewer v2.3+
- **Python Required**: 3.7 or higher
- **Main Dependencies**: 
  - astropy (FITS file reading)
  - pandas (data manipulation)
  - matplotlib (plotting)
  - numpy (numerical operations)

## Contact & Feedback

After testing, colleagues should provide feedback on:
1. What works well
2. What could be improved
3. Any errors encountered
4. Feature requests
5. Performance issues (if any)

---

**Distribution Date**: April 1, 2026
**Package Version**: v2.3
**Target Users**: Astrophotography enthusiasts, observation data managers
