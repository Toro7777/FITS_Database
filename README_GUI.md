# FITS Database GUI Application

A comprehensive GUI application to browse and analyze FITS files organized in date-named folders.

## Features

✅ **Automatic Folder Scanning** - Finds folders with format `YYYY-MM-DD TargetName`

✅ **FITS Header Reading** - Extracts:
   - `OBJECT` - Target object identifier
   - `TELESCOP` - Telescope information
   - `FOCALLEN` - Focal length
   - `IMAGETYP` - Image type (LIGHT, BIAS, DARK, FLAT, etc.)
   - `FILTER` - Filter name
   - `GAIN` - Sensor gain value
   - `EXPTIME` - Exposure time

✅ **Database Display** - Interactive table showing:
   - Capture Date (from folder name)
   - Target Name
   - FITS Object Header
   - Telescope & Focal Length
   - Total File Count
   - LIGHT Frame Count
   - Filter Information
   - Gain & Exposure Time Ranges

✅ **Filtering & Search** - Filter by target name or filter type

✅ **Detailed View** - Double-click any row to see complete details including:
   - Per-filter statistics
   - Gain ranges per filter
   - Exposure time ranges per filter
   - All image types present

✅ **Export** - Save filtered results to CSV

## Installation

1. Make sure you have Python 3.7+ installed
2. Install required packages:

```bash
pip install -r requirements.txt
```

Or manually:
```bash
pip install astropy
```

## Usage

### Method 1: Run directly
```bash
python fits_gui_database.py
```

### Method 2: Create a batch file (Windows)
Create a file called `launch_fits_gui.bat`:
```batch
@echo off
python fits_gui_database.py
pause
```

Then double-click the batch file to run.

## How to Use the Application

1. **Select Root Directory**
   - Click "Select Folder..." button
   - Choose the root directory containing your organized FITS folders
   - Example structure:
     ```
     MyObservations/
     ├── 2020-11-25 M1 Crab Nebula/
     │   ├── Light/
     │   │   ├── m1_light_001.fits
     │   │   ├── m1_light_002.fits
     │   └── Dark/
     │       └── m1_dark_001.fits
     ├── 2020-11-26 M31 Andromeda/
     │   └── Light/
     │       └── m31_light_001.fits
     ```

2. **Scan Directory**
   - Click "Scan Directory" to analyze all FITS files
   - Status bar shows progress and results

3. **Browse Results**
   - Table displays one row per organized folder
   - Shows aggregated statistics for all FITS files in that folder

4. **Filter Results**
   - Enter target name or filter type
   - Click "Apply Filters" to show only matching entries
   - Click "Clear Filters" to reset

5. **View Details**
   - Double-click any row to open a detailed information window
   - Shows individual filter statistics, gain ranges, and exposure times

6. **Export Data**
   - Click "Export to CSV" to save current table to a CSV file
   - CSV can be imported into Excel or other tools

## Example Folder Structure

```
D:\Astronomy\Observations\
├── 2020-11-25 M1 Crab Nebula\
│   ├── m1_light_Ha.fits
│   ├── m1_light_OIII.fits
│   ├── m1_dark.fits
│   └── m1_flat.fits
├── 2020-12-10 M51 Whirlpool\
│   ├── Red\
│   │   ├── m51_light_red_001.fits
│   │   └── m51_light_red_002.fits
│   └── Green\
│       └── m51_light_green_001.fits
```

## Understanding the Table Columns

| Column | Description |
|--------|-------------|
| Date | Capture date extracted from folder name (YYYY-MM-DD) |
| Target | Target name extracted from folder name |
| Object | FITS OBJECT header value (what was being observed) |
| Telescope | FITS TELESCOP header value |
| Focal Length | FITS FOCALLEN header value (in mm) |
| Total Files | Count of all FITS files in folder |
| LIGHT Frames | Count of files with IMAGETYP='LIGHT' |
| Filters | All unique filter names used (comma-separated) |
| Gain Range | Min-Max sensor gain values across all frames |
| Exptime Range | Min-Max exposure time values (in seconds) |

## Notes

- **Recursive Scanning**: The application scans subfolders automatically, so you can have FITS files in subdirectories
- **Case Insensitive**: File extensions .fits, .fit, .FIT, .FITS are all recognized
- **Multiple Values**: If a folder contains files from different telescopes or with different focal lengths, they are listed with "|" separator
- **Performance**: Large directories with thousands of files may take time to scan initially
- **CSV Export**: The exported CSV shows the currently filtered table

## Troubleshooting

**"No data" message**
- Ensure your folders use the format: `YYYY-MM-DD TargetName`
- Verify FITS files are in subfolders of these named directories

**Import Error: No module named 'astropy'**
- Run: `pip install astropy`

**Slow scanning**
- Large directories or network drives will be slower
- Scanning happens only when you click the button - subsequent filtering is instant

## License

Use freely for astronomical purposes.
