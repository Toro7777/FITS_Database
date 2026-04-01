# FITS Database Viewer - Distribution Package

Complete astrophotography FITS file database management tool with integrated FITS viewer and NINA sequencer export.

## Quick Start

### Option 1: Run Executable (RECOMMENDED - No Python Required)

**Windows Users:**
1. Download: `FITS_Database.exe` from dist folder
2. Double-click to launch
3. Select your observation folders
4. Start managing your FITS database!

**That's it!** No installation, no Python, no dependencies.

### Option 2: Run from Python Source (Requires Python)

**Windows Users**
1. **Install Python** (if not already installed): https://www.python.org/downloads/
   - During installation, check "Add Python to PATH"

2. **Install Dependencies**
   - Double-click `INSTALL.bat` in this folder
   - This will install all required Python packages

3. **Launch the Application**
   - Double-click `launch_fits_database.bat`
   - Select your observation folders to scan
   - Start managing your FITS database!

### Mac/Linux Users
1. **Install Python** (if not already installed)
   ```bash
   # macOS (using Homebrew)
   brew install python3
   
   # Ubuntu/Debian
   sudo apt-get install python3 python3-pip
   ```

2. **Install Dependencies**
   ```bash
   python3 -m pip install astropy pillow numpy pandas matplotlib
   ```

3. **Launch the Application**
   ```bash
   python3 fits_gui_database.py
   ```

## Features

### Database Management
- **Smart Scanning**: Automatically discovers FITS files in organized folder structures
- **Multi-Object Sessions**: Handles folders with multiple observed targets
- **Real-time Search**: Filter observations with comma-separated AND logic
- **Column Sorting**: Click any column header to sort ascending/descending
- **Dual Directory Support**: Scan multiple folders simultaneously

### ImageMetaData Analysis
- **Flexible Metrics**: Automatically detects available observation metrics (ADU Mean, HFR, Detected Stars, etc.)
- **Time-Based Plotting**: Interactive plots with time range sliders
- **Frame-Based Fallback**: Works even without timestamp data
- **HFR Extraction**: Automatically extracts HFR values from FITS filenames
- **Adaptive Layouts**: Adjusts plot grid based on available metrics

### FITS Viewer Integration
- **High-Resolution Viewer**: Browse and analyze FITS files frame-by-frame
- **Interactive Tools**: Pan, zoom, and adjust contrast/brightness in real-time
- **Metadata Display**: View FITS headers and observation parameters
- **Playback Mode**: Automatic framestack playback at adjustable speed
- **Dedicated Launch Button**: Quick access from the database viewer

### NINA Sequencer Export
- **Direct Export**: Export single observations as NINA JSON targets
- **Batch Export**: Export entire observation database at once
- **Full Template**: Compatible with NINA v2.5+ sequencer format
- **Coordinate Precision**: Maintains RA/DEC accuracy from FITS headers

## Key Functions

### Right-Click Context Menu
- **Export as NINA JSON**: Export single observation
- **Launch in FITS Viewer**: Open folder in dedicated viewer
- **Read Image Metadata**: Plot metrics from ImageMetaData.csv
- **Show Details**: View comprehensive observation information
- **Open Folder**: Navigate to observation directory

### Main Buttons
- **Scan & Save Database**: Scan selected folders and cache results
- **Refresh Last Scan**: Reload cached database without re-scanning
- **Export to CSV**: Export current view to spreadsheet format
- **Export All as NINA JSON**: Batch export all observations
- **Launch FITS Viewer**: Open standalone FITS viewer

## Folder Structure Requirements

For automatic detection, organize FITS files using the standard naming convention:

```
YOUR_OBSERVATIONS_FOLDER/
├── 2026-03-28 M101 - ESPRIT 100/
│   ├── 2026-03-28 M101 - Light - 001.fits
│   ├── 2026-03-28 M101 - Light - 002.fits
│   └── ImageMetaData.csv (optional)
├── 2026-03-29 NGC 281/
│   └── ...
```

The tool recognizes: `YYYY-MM-DD TargetName` folders automatically.

## ImageMetaData CSV Format

Optional CSV file for plotting observation metrics. Supported column names (case-sensitive):
- Time columns: `ExposureStartUTC`, `ExposureStart`, `StartUTC`, `Time`, `Timestamp`
- Metrics: `ADUMean`, `Mean ADU`, `DetectedStars`, `Stars`, `HFR`, `GuidingRMS`, `RMS`
- File reference: `FileName` (for automatic HFR extraction from filenames)

Example pattern for HFR extraction: `Light-001-3.45.fits` (extracts 3.45 as HFR)

## File Size and Performance

- **Database Size**: ~50 KB per 100 observations (even with 1000+ files per observation)
- **Scan Time**: ~2-5 seconds for 100 observations on typical hardware
- **Memory**: ~100 MB typical usage

## Troubleshooting

### "Python not found"
- Install Python from https://www.python.org/
- During installation, ensure "Add Python to PATH" is checked

### "Module not found" errors
- Run `INSTALL.bat` manually to install dependencies
- Or run: `python -m pip install astropy pillow numpy pandas matplotlib`

### FITS Viewer won't launch
- Ensure both files are in the correct locations
- Check that FITS_Viewer folder exists in the same directory as fits_gui_database.py

### ImageMetaData not plotting
- Verify the CSV column names match the supported list above
- Check that the FileName column exists for HFR extraction
- Console output will show available columns for debugging

## Database Files

**fits_database.json**: Stores cached observation data
- Auto-created on first scan
- Located in application directory
- ~50 KB per 100 observations
- Delete to force full re-scan

## Advanced Features

### Multi-Filter Search
Use commas for AND logic:
- `"M101"` → Show only M101
- `"NGC, halpha"` → Show NGC targets with H-alpha filter
- `"2026-03"` → Show March 2026 observations

### Column Dragging
Under each column header: drag to select/reorder columns (experimental)

### CSV Export
Export filtered/sorted view to Excel-compatible CSV format

## Support

For issues or feature requests:
1. Check console output (visible when running from terminal)
2. Verify Python packages are installed
3. Ensure folder structure matches requirements
4. Check file permissions on FITS folders

## Version

FITS Database Viewer v2.3+
- Integrated FITS Viewer
- Flexible metadata analysis
- Enhanced NINA JSON export

---

**Built for astrophotography enthusiasts and automated observation processing.**
