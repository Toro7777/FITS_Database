# FITS Database v2.3 - Quick Start Guide

**Get up and running in 5 minutes**

---

## 1. Install & Launch (2 minutes)

### Option A: Executable (Windows - Fastest)
```
1. Download FITS_Database.exe
2. Double-click it
3. Done! Application starts immediately
```

### Option B: Python (All Platforms)
```bash
git clone https://github.com/Toro7777/FITS_Database.git
cd FITS_Database
pip install -r requirements.txt
python fits_gui_database.py
```

---

## 2. Load Your FITS Files (2 minutes)

```
1. Click "Select Directory"
2. Choose folder with your FITS observations
3. Click "Scan"
4. Wait for completion...
5. Your observations appear in the tree!
```

**Folder Structure (FITS Database works best with this):**
```
D:\Observations\
├─ 2026-01-15\
│  ├─ M31_Session\
│  │  ├─ M31_Ha_001.fits
│  │  ├─ M31_Ha_002.fits
│  │  └─ M31_Ha_metadata.csv (optional)
└─ 2026-01-14\
   └─ M33_Session\
      ├─ M33_Ha_001.fits
```

---

## 3. Find an Observation (30 seconds)

**Use the search box:**
```
Type "M31"      → Finds all M31 observations
Type "Ha"       → Finds all Ha filter exposures
Type "2026-01"  → Finds all January observations
```

Results filter instantly as you type!

---

## 4. View Observation Details (30 seconds)

```
1. Click on observation in tree
2. Details panel appears on the right
3. See: coordinates, telescope, filters, exposure time, etc.
```

---

## 5. Export to NINA (1 minute)

**Single observation:**
```
1. Right-click observation
2. Select "Export as NINA JSON"
3. Choose save location
4. Open NINA → Import this JSON file
5. Run automated observation sequence!
```

**All observations at once:**
```
1. Click "Export All as NINA JSON" button
2. Choose destination folder
3. All observations exported as separate JSON files
4. Batch import into NINA!
```

---

## 6. Analyze Imaging Session (1 minute)

```
1. Right-click session (if CSV metadata exists)
2. Select "Read Image Metadata"
3. See analysis:
   • Total images captured
   • Average exposure time
   • Filter breakdown
   • Total integration time
```

---

## 7. View FITS File Headers

**Option 1: Built-in Details Panel**
- Click any observation
- View in right panel

**Option 2: Integrated FITS Viewer**
```
1. Right-click observation
2. Select "Launch in FITS Viewer"
3. Full FITS header inspector opens
```

---

## Keyboard Shortcuts (Cheat Sheet)

| Shortcut | Action |
|----------|--------|
| **Ctrl+O** | Select Directory |
| **Ctrl+S** | Scan |
| **Ctrl+F** | Search |
| **Ctrl+E** | Export All as NINA JSON |
| **F1** | Full User Manual |

---

## Common Tasks

### Task 1: Add New Observations
```
New observations to D:\Observations\2026-01-20\ ?
1. Copy FITS files there
2. Click "Scan" again
3. New observations appear automatically!
```

### Task 2: Search for Specific Target
```
Looking for M51 in June?
1. Type in search box: "2026-06 M51"
2. Press Enter or just click result
3. Details show up instantly!
```

### Task 3: Backup Your Database
```
1. Tools → Backup Database
2. Choose save location (external drive recommended)
3. Your database is backed up!
```

### Task 4: Switch Theme (Dark/Light)
```
1. View → Dark Theme (or Light Theme)
2. Interface updates immediately
```

---

## Troubleshooting Quick Fixes

| Problem | Solution |
|---------|----------|
| No FITS files found | Organize into Date/Target folders |
| Search is slow | Use Compact Database (Tools menu) |
| FITS Viewer won't open | Run as Administrator (Windows) |
| NINA export fails | Check that folder has write permissions |
| Database is huge | Archive old observations to separate folder |

---

## Tips for Best Results

1. **Organize by Date**
   - Use folders like: 2026-01-15, 2026-01-16
   - Database recognizes and organizes automatically

2. **Use Descriptive Names**
   - Good: M31_Ha_300s_001.fits
   - Bad: image_001.fits

3. **Export CSV Metadata**
   - If using NINA, export CSV at end of session
   - Place in same folder as FITS files
   - Use "Read Image Metadata" to analyze

4. **Search Before Browsing**
   - For large databases, search first
   - Reduces results dramatically
   - Much faster than scrolling

5. **Backup Regularly**
   - Weekly: Book to external drive
   - Monthly: Create full archive
   - Remember: 3-2-1 rule (3 copies, 2 locations, 1 offsite)

---

## What Can Be Exported?

✅ **NINA JSON** (for automated observations)
- Target coordinates
- Equipment settings
- Filter & exposure info

✅ **Database Backup** (full archive)
- All observations
- Search indexes
- Metadata

✅ **CSV Reports** (spreadsheet format)
- Session statistics
- Integration times
- Filter usage

---

## File Size Reference

| FITS Library Size | Scan Time | Search Speed |
|---|---|---|
| 1,000 files | 2-3 min | Instant |
| 5,000 files | 10-15 min | <1 second |
| 10,000 files | 20-30 min | 1-2 seconds |
| 50,000 files | 60+ min | 3-5 seconds |

**Tip:** Use Compact Database weekly to keep fastest performance

---

## Getting Help

**In FITS Database:**
- Press **F1** for full User Manual
- Check **Help → About** for version info
- See **Tools** menu for all features

**Online:**
- GitHub Issues: Report bugs
- README.md: Comprehensive guide
- USER_MANUAL.md: Detailed documentation

---

## Next Steps

1. ✅ Scan your FITS library
2. ✅ Try searching
3. ✅ Export one observation to NINA
4. ✅ Run automated imaging sequence
5. ✅ Add observations weekly

---

**That's it! You're ready to organize and manage your FITS library like a pro!** 🔭✨

For detailed documentation, see **USER_MANUAL.md**

Happy observing!
