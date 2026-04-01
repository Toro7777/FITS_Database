# FITS_Library - Quick Reference

## 🚀 Getting Started

### First Time?
1. Run `setup.bat` to install dependencies (Windows)
2. Double-click `launch_fits_gui.bat` to start
3. Read `START_HERE.md` for basics

## 📊 Table Structure

```
Date           → Observation night (expand to see targets)
  ├─ Session   → Folder name or target type
  │  ├─ Object → Sky object name (FITS header: OBJECT)
  │  ├─ Telescope → Instrument used
  │  ├─ Focal Length → Focal length in mm
  │  ├─ Total Files → Count of all FITS files
  │  ├─ LIGHT Frames → Exposure frames (ignores BIAS, DARK, FLAT)
  │  ├─ Filters → Filters used (L R G B Ha O3 S2 Other)
  │  ├─ Gain → Sensor gain value(s)
  │  ├─ Offset → Sensor offset value(s)
  │  ├─ Exptime → Exposure time range in seconds
  │  └─ Total Integration → Total exposure time (hrs:mins:secs)
```

## 🎯 Common Tasks

### Scan New Data
1. Click "Select Directory" button
2. Choose folder containing FITS observation folders
3. Click "Scan" → Wait for completion
4. Data appears in hierarchical tree

### Find Observations
- **Search box** (top) - Type to filter instantly
- **Sort** - Click column headers to sort
- **Expand/Collapse** - Click arrow next to dates/sessions

### View Details
- **Double-click** leaf row → Shows detailed info panel
- **Double-click** date/session → Expands/collapses that section

### Export for NINA
- **Right-click** → "Export as NINA JSON"
- Choose save location
- Opens in NINA desktop application

### Analyze Image Quality
- **Right-click** on session → "Read Image Metadata" (if CSV exists)
- Shows 4 plots:
  - ADU Mean (image brightness trend)
  - Detected Stars (tracking quality)
  - HFR (focus quality)
  - Guiding RMS (mount stability)

### Open in Explorer
- **Right-click** → "Open Folder"
- Opens Windows Explorer at that session's location

## 📁 Folder Organization Expected

```
MyObservations/
├── 2022-03-20 M31/
│   ├── M31_L_001.fits
│   ├── M31_L_002.fits
│   ├── ImageMetaData.csv (optional)
├── 2022-03-20 M33/
│   ├── M33_R_001.fits
│   ├── M33_G_001.fits
│   ├── M33_B_001.fits
└── 2022-03-21 NGC224/
    └── NGC224_Ha_001.fits
```

## ⚙️ Settings & Features

### Column Reordering
- Drag column headers to rearrange

### Data Persistence
- `fits_database.json` caches results
- Faster scans after first import

### Filter Display
L = Luminosity, R = Red, G = Green, B = Blue
Ha = H-Alpha, O3 = OIII, S2 = SII, Other = Unknown

### Gain/Offset/Exptime Format
- Single value shows as: `100`
- Range shows as: `50-100`
- Multiple types: `100 | 120` (separated by |)

## 🔍 Keyboard Shortcuts

| Action | Method |
|--------|--------|
| Search | Type in search box (top-left) |
| Expand all | Click date header (no shortcut yet) |
| Show details | Double-click row |
| Toggle expand | Double-click parent row |
| Context menu | Right-click row |
| Sort by column | Click column header |

## 📋 File Formats Supported

- **.fits, .fits.gz** - FITS image files
- **.csv** - ImageMetaData.csv for quality analysis

## 💾 Data Files Created

- `fits_database.json` - Database cache (auto-generated)
- Saved exports go to your chosen location

## 🆘 Need Help?

1. **Start Here** → `START_HERE.md`
2. **Full Guide** → `HOW_TO_USE_v2_2.md`
3. **GUI Reference** → `README_GUI.md`
4. **This File** → `QUICK_REF.md` (you are here)

---

Version 2.2+ | Last Updated: March 2026
