"""
FITS Database GUI Application

This application creates a GUI database viewer for FITS files in organized folders.
It scans folders with the format: YYYY-MM-DD TargetName
and displays detailed information about the FITS files within them.

Features:
- Scans directory recursively for organized folders
- Reads FITS headers (OBJECT, TELESCOP, FOCALLEN, IMAGETYP, FILTER, GAIN, EXPTIME)
- Displays comprehensive database in interactive table
- Filter and sort capabilities
- Statistical summary

Usage:
    python fits_gui_database.py
"""

import os
import sys
import subprocess
from pathlib import Path
from collections import defaultdict
from datetime import datetime
import re
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from astropy.io import fits
import json
from typing import Dict, List, Tuple, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import signal
import csv
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import pandas as pd


class FITSDatabase:
    """Manages FITS file scanning and database operations"""
    
    DATABASE_FILE = "fits_database.json"
    METADATA_KEY = "__metadata__"
    
    def __init__(self):
        self.entries = []  # List of scan entries
        self.raw_data = {}  # Raw FITS data by folder
        self.last_scan_path = None
        self.last_scan_time = None
        self.last_load_duration = 0  # Load duration in seconds
        
    def scan_directory(self, root_path: str, ignore_cal_frames: bool = False, only_light_frames: bool = False, trust_filename: bool = False, progress_callback=None) -> Dict:
        """
        Scan directory for folders and extract FITS file information
        
        Args:
            root_path: Root directory to scan
            ignore_cal_frames: If True, ignore DARK/FLAT/BIAS frames
            only_light_frames: If True, only include LIGHT frames (excludes all others)
            trust_filename: If True, skip files based on filename (DARK, FLAT, BIAS)
            progress_callback: Optional callback function for progress updates
            
        Returns:
            Dictionary with scanning results
        """
        import time
        start_time = time.time()
        
        results = {
            'total_folders': 0,
            'folders_processed': 0,
            'total_files': 0,
            'errors': [],
            'load_duration': 0
        }
        
        self.entries = []
        self.raw_data = {}
        
        # Pattern: YYYY-MM-DD something
        folder_pattern = re.compile(r'^(\d{4}-\d{2}-\d{2})\s+(.+)$')
        
        try:
            for item in Path(root_path).iterdir():
                if not item.is_dir():
                    continue
                
                # Skip folders starting with hash
                if item.name.startswith('#'):
                    continue
                    
                results['total_folders'] += 1
                match = folder_pattern.match(item.name)
                
                if progress_callback:
                    progress_callback(f"Checking: {item.name}")
                
                if not match:
                    continue
                
                capture_date = match.group(1)
                target_name = match.group(2)
                
                # Find all FITS files in this folder (including subfolders)
                # Use set to avoid duplicates (rglob is case-insensitive on Windows)
                fits_files_set = set(item.rglob('*.fits')) | set(item.rglob('*.fit')) | set(item.rglob('*.FIT')) | set(item.rglob('*.FITS'))
                fits_files = list(fits_files_set)
                
                if not fits_files:
                    continue
                
                results['folders_processed'] += 1
                
                if progress_callback:
                    progress_callback(f"Processing: {item.name} ({len(fits_files)} files)")
                
                # Process FITS files in this folder - returns list of entries (one per object)
                entries_list = self._process_fits_folder_multi_object(
                    folder_path=item,
                    capture_date=capture_date,
                    target_name=target_name,
                    fits_files=fits_files,
                    ignore_cal_frames=ignore_cal_frames,
                    only_light_frames=only_light_frames,
                    trust_filename=trust_filename
                )
                
                if entries_list:
                    self.entries.extend(entries_list)
                    results['total_files'] += len(fits_files)
                    self.raw_data[item.name] = entries_list
                    
        except Exception as e:
            results['errors'].append(f"Error scanning directory: {str(e)}")
        
        # Calculate load duration
        results['load_duration'] = time.time() - start_time
        self.last_load_duration = results['load_duration']
        
        return results
    
    def save_database(self, root_path: str):
        """
        Save scanned data to JSON database file
        
        Args:
            root_path: The path that was scanned
        """
        try:
            # Prepare data for JSON serialization
            data = {
                self.METADATA_KEY: {
                    'scan_path': root_path,
                    'scan_time': datetime.now().isoformat(),
                    'version': '1.0'
                },
                'entries': []
            }
            
            # Convert entries to JSON-serializable format
            for entry in self.entries:
                json_entry = {k: v for k, v in entry.items()}
                # Convert image_types dict to list for JSON
                if 'image_types' in json_entry:
                    json_entry['image_types'] = json_entry['image_types']
                data['entries'].append(json_entry)
            
            with open(self.DATABASE_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str)
            
            self.last_scan_path = root_path
            self.last_scan_time = datetime.now()
            return True
        except Exception as e:
            print(f"Error saving database: {str(e)}")
            return False
    
    def load_database(self) -> Dict:
        """
        Load database from JSON file
        
        Returns:
            Dictionary with loaded entries and metadata, or empty dict if file not found
        """
        try:
            if not Path(self.DATABASE_FILE).exists():
                return {'metadata': None, 'entries': []}
            
            with open(self.DATABASE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            metadata = data.get(self.METADATA_KEY, {})
            
            # Handle both old and new database formats
            if 'entries' in data:
                # New format: entries are under 'entries' key
                entries = data.get('entries', [])
            else:
                # Old format: each entry is a top-level key (except metadata)
                entries = [v for k, v in data.items() if k != self.METADATA_KEY]
            
            # Convert image_types back to dict if needed
            for entry in entries:
                if 'image_types' in entry and isinstance(entry['image_types'], list):
                    entry['image_types'] = dict(entry['image_types'])
            
            self.entries = entries
            self.last_scan_path = metadata.get('scan_path')
            if metadata.get('scan_time'):
                self.last_scan_time = datetime.fromisoformat(metadata['scan_time'])
            
            return {'metadata': metadata, 'entries': entries}
        except Exception as e:
            print(f"Error loading database: {str(e)}")
            return {'metadata': None, 'entries': []}
    
    def get_database_info(self) -> Dict:
        """
        Get information about the current database
        
        Returns:
            Dictionary with database info
        """
        return {
            'scan_path': self.last_scan_path,
            'scan_time': self.last_scan_time,
            'entry_count': len(self.entries),
            'file': self.DATABASE_FILE,
            'load_duration': getattr(self, 'last_load_duration', 0)
        }
    
    def _process_fits_folder_multi_object(self, folder_path: Path, capture_date: str, target_name: str, fits_files: List[Path], ignore_cal_frames: bool = False, only_light_frames: bool = False, trust_filename: bool = False) -> List[Dict]:
        """
        Process FITS files in a folder and create separate entries for each object found.
        
        Returns:
            List of dictionaries, one per object found in the folder
        """
        try:
            # Process all FITS files in parallel
            results = []
            with ThreadPoolExecutor(max_workers=4) as executor:
                futures = {executor.submit(self._read_fits_header_with_timeout, fits_file, ignore_cal_frames, only_light_frames, trust_filename): fits_file 
                          for fits_file in fits_files}
                
                for future in as_completed(futures):
                    try:
                        result = future.result()
                        if result:
                            results.append(result)
                    except Exception as e:
                        print(f"Warning: Error processing FITS file: {str(e)}")
                        continue
            
            if not results:
                return []
            
            # Group results by object
            objects_data = defaultdict(lambda: {
                'files': [],
                'telescopes': set(),
                'focal_lengths': set(),
                'light_count': 0,
                'filters_info': defaultdict(lambda: {'count': 0, 'gains': [], 'offsets': [], 'exptimes': []}),
                'all_gains': set(),
                'all_offsets': set(),
                'all_exptimes': set(),
                'image_types': defaultdict(int),
                'ra_hms': None,
                'dec_dms': None,
            })
            
            # Distribute results per object
            for result in results:
                obj = result['object'] if result['object'] else 'Unknown'
                objects_data[obj]['files'].append(result)
                
                if result['telescope']:
                    objects_data[obj]['telescopes'].add(result['telescope'])
                if result['focal_length'] is not None:
                    objects_data[obj]['focal_lengths'].add(result['focal_length'])
                
                image_type = result['imagetype']
                objects_data[obj]['image_types'][image_type] += 1
                if image_type == 'LIGHT':
                    objects_data[obj]['light_count'] += 1
                
                filter_val = result['filter']
                fdata = objects_data[obj]['filters_info'][filter_val]
                fdata['count'] += 1
                if result['gain'] is not None:
                    fdata['gains'].append(result['gain'])
                    objects_data[obj]['all_gains'].add(result['gain'])
                if result['offset'] is not None:
                    fdata['offsets'].append(result['offset'])
                    objects_data[obj]['all_offsets'].add(result['offset'])
                if result['exptime'] is not None:
                    fdata['exptimes'].append(result['exptime'])
                    objects_data[obj]['all_exptimes'].add(result['exptime'])
                
                if not objects_data[obj]['ra_hms'] and result.get('ra_hms'):
                    objects_data[obj]['ra_hms'] = result['ra_hms']
                if not objects_data[obj]['dec_dms'] and result.get('dec_dms'):
                    objects_data[obj]['dec_dms'] = result['dec_dms']
            
            # Create separate entries for each object
            entries = []
            for obj_name, obj_data in sorted(objects_data.items()):
                filter_list = []
                for fname, fdata in sorted(obj_data['filters_info'].items()):
                    # Format gains
                    if fdata['gains']:
                        unique_gains = list(set(fdata['gains']))
                        if len(unique_gains) == 1:
                            gains_str = f"{unique_gains[0]:.0f}"
                        else:
                            gains_str = f"{min(fdata['gains']):.0f}-{max(fdata['gains']):.0f}"
                    else:
                        gains_str = "N/A"
                    
                    # Format offsets
                    if fdata['offsets']:
                        unique_offsets = list(set(fdata['offsets']))
                        if len(unique_offsets) == 1:
                            offsets_str = f"{unique_offsets[0]:.0f}"
                        else:
                            offsets_str = f"{min(fdata['offsets']):.0f}-{max(fdata['offsets']):.0f}"
                    else:
                        offsets_str = "N/A"
                    
                    # Format exptimes
                    exptimes_str = self._format_range_smart(fdata['exptimes'], decimal_places=1) if fdata['exptimes'] else "N/A"
                    
                    filter_list.append({
                        'name': fname,
                        'count': fdata['count'],
                        'gains': gains_str,
                        'offsets': offsets_str,
                        'exptimes': exptimes_str,
                        'exptimes_list': fdata['exptimes'],
                        'gains_list': fdata['gains'],
                        'offsets_list': fdata['offsets']
                    })
                
                entry = {
                    'capture_date': capture_date,
                    'target_name': target_name,
                    'folder_name': str(folder_path),
                    'object': obj_name,
                    'telescope': ' | '.join(sorted(obj_data['telescopes'])) if obj_data['telescopes'] else 'Unknown',
                    'focal_length': ' | '.join(f"{fl:.0f}mm" for fl in sorted(obj_data['focal_lengths'])) if obj_data['focal_lengths'] else 'Unknown',
                    'total_files': len(obj_data['files']),
                    'light_frames': obj_data['light_count'],
                    'image_types': dict(obj_data['image_types']),
                    'filters': filter_list,
                    'unique_filters': self._format_filter_names_as_matrix([f['name'] for f in filter_list]),
                    'gain_range': self._format_range_smart(list(obj_data['all_gains']), decimal_places=0) if obj_data['all_gains'] else "N/A",
                    'offset_range': self._format_range_smart(list(obj_data['all_offsets']), decimal_places=0) if obj_data['all_offsets'] else "N/A",
                    'exptime_range': self._format_range_smart(list(obj_data['all_exptimes']), decimal_places=1) if obj_data['all_exptimes'] else "N/A",
                    'ra_hms': obj_data['ra_hms'],
                    'dec_dms': obj_data['dec_dms'],
                }
                entries.append(entry)
            
            return entries
            
        except Exception as e:
            print(f"Error processing folder {folder_path.name}: {str(e)}")
            return []
    
    def _process_fits_folder(self, folder_path: Path, capture_date: str, target_name: str, fits_files: List[Path], ignore_cal_frames: bool = False, only_light_frames: bool = False, trust_filename: bool = False) -> Optional[Dict]:
        """
        Process all FITS files in a folder and extract relevant data
        
        Args:
            folder_path: Path to the folder
            capture_date: Date string (YYYY-MM-DD)
            target_name: Target name
            fits_files: List of FITS file paths
            ignore_cal_frames: If True, skip DARK/FLAT/BIAS frames
            only_light_frames: If True, only include LIGHT frames (excludes all others)
            trust_filename: If True, skip files based on filename (DARK, FLAT, BIAS)
            
        Returns:
            Dictionary with processed information or None if error
        """
        try:
            # Initialize data collectors with thread-safe locks
            objects = set()
            telescopes = set()
            focal_lengths = set()
            light_count = 0
            filters_info = defaultdict(lambda: {'count': 0, 'gains': [], 'offsets': [], 'exptimes': []})
            all_gains = set()
            all_offsets = set()
            all_exptimes = set()
            image_types = defaultdict(int)
            ra_hms = None  # Store first valid RA
            dec_dms = None  # Store first valid DEC
            
            # Process FITS files in parallel
            results = []
            with ThreadPoolExecutor(max_workers=4) as executor:
                futures = {executor.submit(self._read_fits_header_with_timeout, fits_file, ignore_cal_frames, only_light_frames, trust_filename): fits_file 
                          for fits_file in fits_files}
                
                for future in as_completed(futures):
                    try:
                        result = future.result()
                        if result:
                            results.append(result)
                    except Exception as e:
                        print(f"Warning: Error processing FITS file: {str(e)}")
                        continue
            
            # Aggregate results from all threads
            for result in results:
                if result['object']:
                    objects.add(result['object'])
                if result['telescope']:
                    telescopes.add(result['telescope'])
                if result['focal_length'] is not None:
                    focal_lengths.add(result['focal_length'])
                
                image_types[result['imagetype']] += 1
                if result['imagetype'] == 'LIGHT':
                    light_count += 1
                
                filter_val = result['filter']
                filters_info[filter_val]['count'] += 1
                if result['gain'] is not None:
                    filters_info[filter_val]['gains'].append(result['gain'])
                    all_gains.add(result['gain'])
                if result['offset'] is not None:
                    filters_info[filter_val]['offsets'].append(result['offset'])
                    all_offsets.add(result['offset'])
                if result['exptime'] is not None:
                    filters_info[filter_val]['exptimes'].append(result['exptime'])
                    all_exptimes.add(result['exptime'])
                
                # Capture first valid RA/DEC
                if not ra_hms and result.get('ra_hms'):
                    ra_hms = result['ra_hms']
                if not dec_dms and result.get('dec_dms'):
                    dec_dms = result['dec_dms']
            
            if not objects and not telescopes and not focal_lengths:
                return None
            
            # Compile results for this folder
            filter_list = []
            for fname, fdata in sorted(filters_info.items()):
                # Format gains: single value or range
                if fdata['gains']:
                    unique_gains = list(set(fdata['gains']))
                    if len(unique_gains) == 1:
                        gains_str = f"{unique_gains[0]:.0f}"
                    else:
                        gains_str = f"{min(fdata['gains']):.0f}-{max(fdata['gains']):.0f}"
                else:
                    gains_str = "N/A"
                
                # Format offsets: single value or range
                if fdata['offsets']:
                    unique_offsets = list(set(fdata['offsets']))
                    if len(unique_offsets) == 1:
                        offsets_str = f"{unique_offsets[0]:.0f}"
                    else:
                        offsets_str = f"{min(fdata['offsets']):.0f}-{max(fdata['offsets']):.0f}"
                else:
                    offsets_str = "N/A"
                
                # Format exptimes: single value or range (using smart formatting)
                exptimes_str = self._format_range_smart(fdata['exptimes'], decimal_places=1) if fdata['exptimes'] else "N/A"
                filter_list.append({
                    'name': fname,
                    'count': fdata['count'],
                    'gains': gains_str,
                    'offsets': offsets_str,
                    'exptimes': exptimes_str,
                    'exptimes_list': fdata['exptimes'],  # Store actual list for integration time calculation
                    'gains_list': fdata['gains'],  # Store actual list for stats
                    'offsets_list': fdata['offsets']  # Store actual list for stats
                })
            
            entry = {
                'capture_date': capture_date,
                'target_name': target_name,
                'folder_name': folder_path.name,
                'object': ' | '.join(sorted(objects)) if objects else 'Unknown',
                'telescope': ' | '.join(sorted(telescopes)) if telescopes else 'Unknown',
                'focal_length': ' | '.join(f"{fl:.0f}mm" for fl in sorted(focal_lengths)) if focal_lengths else 'Unknown',
                'total_files': len(fits_files),
                'light_frames': light_count,
                'image_types': image_types,
                'filters': filter_list,
                'unique_filters': self._format_filter_names_as_matrix([f['name'] for f in filter_list]),
                'gain_range': self._format_range_smart(list(all_gains), decimal_places=0) if all_gains else "N/A",
                'offset_range': self._format_range_smart(list(all_offsets), decimal_places=0) if all_offsets else "N/A",
                'exptime_range': self._format_range_smart(list(all_exptimes), decimal_places=1) if all_exptimes else "N/A",
                'ra_hms': ra_hms,
                'dec_dms': dec_dms,
            }
            
            return entry
            
        except Exception as e:
            print(f"Error processing folder {folder_path.name}: {str(e)}")
            return None
    
    @staticmethod
    def _read_fits_header_with_timeout(fits_file: Path, ignore_cal_frames: bool, only_light_frames: bool = False, trust_filename: bool = False, timeout_seconds: int = 10) -> Optional[Dict]:
        """
        Wrapper for _read_fits_header with timeout protection
        Falls back to None if file takes too long to read
        """
        result = [None]  # Use list to share result between threads
        error_flag = [False]
        
        def read_with_timeout():
            try:
                result[0] = FITSDatabase._read_fits_header(fits_file, ignore_cal_frames, only_light_frames, trust_filename)
            except Exception as e:
                print(f"Timeout or error reading {fits_file.name}: {str(e)}")
                error_flag[0] = True
        
        thread = threading.Thread(target=read_with_timeout, daemon=True)
        thread.start()
        thread.join(timeout=timeout_seconds)
        
        if thread.is_alive():
            print(f"Warning: FITS file reading timeout (>10s): {fits_file.name} - skipping")
            return None
        
        return result[0] if not error_flag[0] else None
    
    @staticmethod
    def _format_filter_names_as_matrix(filter_names: List[str]) -> str:
        """
        Format filter names as a simple space-separated list of acronyms
        Example: "L R G B" or "L R G B Other"
        """
        # Normalize filter name to abbreviation
        abbrev_map = {
            'L': 'L', 'Luminosity': 'L', 'luminosity': 'L',
            'R': 'R', 'Red': 'R', 'red': 'R',
            'G': 'G', 'Green': 'G', 'green': 'G',
            'B': 'B', 'Blue': 'B', 'blue': 'B',
            'Ha': 'H', 'H': 'H', 'h': 'H', 'Alpha': 'H', 'HALPHA': 'H', 'halpha': 'H', 'Halpha': 'H',
            'OIII': 'O', 'O': 'O', 'o': 'O', 'O3': 'O', 'o3': 'O',
            'SII': 'S', 'S': 'S', 's': 'S', 'S2': 'S', 's2': 'S',
        }
        
        # Standard filter order
        standard_filters = ['L', 'R', 'G', 'B', 'H', 'O', 'S']
        
        # Normalize and collect present filters
        present_abbrevs = set()
        has_other = False
        for fname in filter_names:
            # Try direct match first
            if fname in abbrev_map:
                present_abbrevs.add(abbrev_map[fname])
            elif fname.upper() in abbrev_map:
                present_abbrevs.add(abbrev_map[fname.upper()])
            elif fname.lower() in abbrev_map:
                present_abbrevs.add(abbrev_map[fname.lower()])
            else:
                # Unknown filter type
                has_other = True
        
        # Build filter string with only present filters
        result_abbrevs = []
        for filt in standard_filters:
            if filt in present_abbrevs:
                result_abbrevs.append(filt)
        
        # Add "Other" only if there are unknown filters
        if has_other:
            result_abbrevs.append("Other")
        
        return " ".join(result_abbrevs) if result_abbrevs else "(none)"
    
    @staticmethod
    def _read_image_metadata_csv(folder_path: str) -> Optional[pd.DataFrame]:
        """
        Read ImageMetaData.csv file from folder
        
        Args:
            folder_path: Path to folder containing ImageMetaData.csv
            
        Returns:
            DataFrame or None if file not found
        """
        csv_path = Path(folder_path) / "ImageMetaData.csv"
        
        if not csv_path.exists():
            return None
        
        try:
            df = pd.read_csv(csv_path)
            return df
        except Exception as e:
            print(f"Error reading CSV: {str(e)}")
            return None
    
    @staticmethod
    def _plot_image_metadata(df: pd.DataFrame, target_name: str) -> bool:
        """
        Plot image metadata metrics from DataFrame
        
        Args:
            df: DataFrame with image metadata
            target_name: Name of target for title
            
        Returns:
            True if successful, False if no data to plot
        """
        # Check for required columns
        required_cols = ['ADUMean', 'DetectedStars', 'HFR', 'GuidingRMS']
        available_cols = [col for col in required_cols if col in df.columns]
        
        if not available_cols:
            return False
        
        # Create figure with subplots
        fig, axes = plt.subplots(len(available_cols), 1, figsize=(10, 2.5*len(available_cols)))
        if len(available_cols) == 1:
            axes = [axes]
        
        fig.suptitle(f"Image Metadata - {target_name}", fontsize=14, fontweight='bold')
        
        # Plot each metric
        for idx, col in enumerate(available_cols):
            ax = axes[idx]
            x_vals = range(len(df))
            y_vals = pd.to_numeric(df[col], errors='coerce')
            
            ax.plot(x_vals, y_vals, marker='o', linewidth=2, markersize=4, color='steelblue')
            ax.set_xlabel('Frame Number')
            ax.set_ylabel(col)
            ax.set_title(f'{col} Evolution')
            ax.grid(True, alpha=0.3)
            
            # Add statistics
            mean_val = y_vals.mean()
            min_val = y_vals.min()
            max_val = y_vals.max()
            ax.axhline(y=mean_val, color='red', linestyle='--', alpha=0.5, label=f'Mean: {mean_val:.2f}')
            ax.legend()
        
        plt.tight_layout()
        plt.show()
        return True
    
    @staticmethod
    def _format_range_smart(values: List[float], decimal_places: int = 1) -> str:
        """
        Format a list of values as single value or range
        If all values are the same, returns single value. Otherwise returns min-max range.
        
        Args:
            values: List of numeric values
            decimal_places: Number of decimal places for formatting
            
        Returns:
            Formatted string (e.g., "30.0" or "30.0-45.0")
        """
        if not values:
            return "N/A"
        
        unique_vals = list(set(values))
        if len(unique_vals) == 1:
            fmt = f"{{:.{decimal_places}f}}"
            return fmt.format(unique_vals[0])
        else:
            fmt = f"{{:.{decimal_places}f}}"
            return f"{fmt.format(min(values))}-{fmt.format(max(values))}"
    
    @staticmethod
    def _extract_ra_hms(header) -> Tuple[Optional[int], Optional[int], Optional[float]]:
        """
        Extract RA in hours, minutes, seconds from FITS header
        Supports: RA, OBJCTRA, RA_OBJ, RA_TELE and component formats
        
        Args:
            header: FITS header
            
        Returns:
            Tuple of (hours, minutes, seconds) or (None, None, None) if not found
        """
        try:
            # Try different RA keywords (in priority order)
            ra_keywords = ['RA', 'OBJCTRA', 'RA_OBJ', 'RA_TELE', 'CRVAL1']
            
            for keyword in ra_keywords:
                ra_val = header.get(keyword)
                if ra_val is not None:
                    # Try to parse as string format first (HH:MM:SS.SS)
                    ra_str = str(ra_val).strip()
                    if ':' in ra_str:
                        try:
                            parts = ra_str.split(':')
                            if len(parts) >= 2:
                                ra_h = int(parts[0])
                                ra_m = int(parts[1])
                                ra_s = float(parts[2]) if len(parts) > 2 else 0.0
                                return (ra_h, ra_m, ra_s)
                        except (ValueError, IndexError):
                            pass
                    
                    # Try as decimal degrees
                    try:
                        ra_deg = float(ra_val)
                        ra_hours_val = int(ra_deg / 15.0)  # 360 deg = 24 hours
                        ra_minutes_val = int((ra_deg / 15.0 - ra_hours_val) * 60)
                        ra_seconds_val = ((ra_deg / 15.0 - ra_hours_val) * 60 - ra_minutes_val) * 60
                        return (ra_hours_val, ra_minutes_val, ra_seconds_val)
                    except (ValueError, TypeError):
                        pass
            
            # Try component-based extraction
            ra_h = header.get('RA_H') or header.get('CRVAL1_H')
            ra_m = header.get('RA_M') or header.get('CRVAL1_M')
            ra_s = header.get('RA_S') or header.get('CRVAL1_S')
            
            if ra_h is not None and ra_m is not None and ra_s is not None:
                return (int(ra_h), int(ra_m), float(ra_s))
        except Exception as e:
            pass
        
        return (None, None, None)
    
    @staticmethod
    def _extract_dec_dms(header) -> Tuple[Optional[int], Optional[int], Optional[float]]:
        """
        Extract DEC in degrees, minutes, seconds from FITS header
        Supports: DEC, OBJCTDEC, DEC_OBJ, DEC_TELE and component formats
        
        Args:
            header: FITS header
            
        Returns:
            Tuple of (degrees, minutes, seconds) or (None, None, None) if not found
        """
        try:
            # Try different DEC keywords (in priority order)
            dec_keywords = ['DEC', 'OBJCTDEC', 'DEC_OBJ', 'DEC_TELE', 'CRVAL2']
            
            for keyword in dec_keywords:
                dec_val = header.get(keyword)
                if dec_val is not None:
                    # Try to parse as string format first (±DD:MM:SS.SS)
                    dec_str = str(dec_val).strip()
                    if ':' in dec_str:
                        try:
                            is_negative = dec_str.startswith('-') or dec_str.startswith('−')
                            dec_str_clean = dec_str.lstrip('+-−')
                            parts = dec_str_clean.split(':')
                            if len(parts) >= 2:
                                dec_d = int(parts[0])
                                dec_m = int(parts[1])
                                dec_s = float(parts[2]) if len(parts) > 2 else 0.0
                                if is_negative:
                                    dec_d = -dec_d
                                return (dec_d, dec_m, dec_s)
                        except (ValueError, IndexError):
                            pass
                    
                    # Try as decimal degrees
                    try:
                        dec_deg = float(dec_val)
                        is_negative = dec_deg < 0
                        dec_deg_abs = abs(dec_deg)
                        
                        dec_deg_val = int(dec_deg_abs)
                        dec_min_val = int((dec_deg_abs - dec_deg_val) * 60)
                        dec_sec_val = ((dec_deg_abs - dec_deg_val) * 60 - dec_min_val) * 60
                        
                        if is_negative:
                            dec_deg_val = -dec_deg_val
                        
                        return (dec_deg_val, dec_min_val, dec_sec_val)
                    except (ValueError, TypeError):
                        pass
            
            # Try component-based extraction
            dec_d = header.get('DEC_D') or header.get('CRVAL2_D')
            dec_m = header.get('DEC_M') or header.get('CRVAL2_M')
            dec_s = header.get('DEC_S') or header.get('CRVAL2_S')
            
            if dec_d is not None and dec_m is not None and dec_s is not None:
                return (int(dec_d), int(dec_m), float(dec_s))
        except Exception as e:
            pass
        
        return (None, None, None)
    
    @staticmethod
    def _read_fits_header(fits_file: Path, ignore_cal_frames: bool, only_light_frames: bool = False, trust_filename: bool = False) -> Optional[Dict]:
        """
        Read header from a single FITS file (optimized for speed)
        Only reads primary HDU to minimize I/O
        
        Args:
            fits_file: Path to FITS file
            ignore_cal_frames: If True, skip DARK/FLAT/BIAS frames
            only_light_frames: If True, only include LIGHT frames (excludes all others)
            trust_filename: If True, skip files based on filename (DARK, FLAT, BIAS)
            
        Returns:
            Dictionary with extracted header values or None if should skip
        """
        try:
            # Check if file is accessible and not suspiciously large (>2GB)
            try:
                file_size = fits_file.stat().st_size
                if file_size > 2_000_000_000:  # 2GB
                    print(f"Warning: FITS file too large (>2GB): {fits_file.name} - skipping")
                    return None
            except (OSError, IOError) as e:
                print(f"Warning: Cannot access file {fits_file.name}: {str(e)}")
                return None
            
            # Check filename first if trust_filename is enabled
            if trust_filename:
                # Only include files with 'LIGHT' in the filename
                filename_lower = fits_file.name.lower()
                if 'light' not in filename_lower:
                    return None
            
            with fits.open(fits_file, memmap=True) as hdul:
                header = hdul[0].header
                
                # Image type and filtering
                imagetype = header.get('IMAGETYP', '').strip().upper()
                
                # Only LIGHT frames filter (strictest)
                if only_light_frames and imagetype != 'LIGHT':
                    return None
                
                # Skip DARK/FLAT/BIAS frames if requested
                if ignore_cal_frames and imagetype in ('DARK', 'FLAT', 'BIAS'):
                    return None
                
                # Extract headers
                obj = header.get('OBJECT', '').strip()
                tele = header.get('TELESCOP', '').strip()
                
                focal = None
                focal_val = header.get('FOCALLEN')
                if focal_val is not None:
                    try:
                        focal = float(focal_val)
                    except (ValueError, TypeError):
                        focal = None
                
                # Filter information
                filter_val = header.get('FILTER', 'Unknown').strip()
                
                gain = None
                gain_val = header.get('GAIN')
                if gain_val is not None:
                    try:
                        gain = float(gain_val)
                    except (ValueError, TypeError):
                        gain = None
                
                offset = None
                offset_val = header.get('OFFSET')
                if offset_val is not None:
                    try:
                        offset = float(offset_val)
                    except (ValueError, TypeError):
                        offset = None
                
                exptime = None
                exptime_val = header.get('EXPTIME')
                if exptime_val is not None:
                    try:
                        exptime = float(exptime_val)
                    except (ValueError, TypeError):
                        exptime = None
                
                # Extract RA/DEC coordinates
                ra_hms = FITSDatabase._extract_ra_hms(header)
                dec_dms = FITSDatabase._extract_dec_dms(header)
                
                return {
                    'object': obj,
                    'telescope': tele,
                    'focal_length': focal,
                    'imagetype': imagetype if imagetype else 'UNKNOWN',
                    'filter': filter_val,
                    'gain': gain,
                    'offset': offset,
                    'exptime': exptime,
                    'ra_hms': ra_hms,
                    'dec_dms': dec_dms
                }
        except Exception as e:
            print(f"Warning: Could not read {fits_file.name}: {str(e)}")
            return None
    
    @staticmethod
    def generate_nina_json(target_name: str, ra_hms: Tuple, dec_dms: Tuple, filters: Optional[List[str]] = None, exposures: Optional[List[float]] = None, gains: Optional[List[float]] = None) -> Optional[Dict]:
        """
        Generate NINA DeepSkyObjectContainer JSON for target
        
        Args:
            target_name: Name of the target
            ra_hms: Tuple of (hours, minutes, seconds)
            dec_dms: Tuple of (degrees, arcmin, arcsec)
            filters: List of filters used
            exposures: List of exposure times
            gains: List of gains used
            
        Returns:
            Dictionary representing NINA DeepSkyObjectContainer JSON
        """
        # Handle missing coordinates
        if not ra_hms or None in ra_hms or not dec_dms or None in dec_dms:
            return None
        
        ra_h, ra_m, ra_s = ra_hms
        dec_d, dec_m, dec_s = dec_dms
        
        # Handle negative declination
        negative_dec = dec_d < 0
        dec_d_abs = abs(dec_d)
        
        # Build the NINA DeepSkyObjectContainer JSON structure
        nina_json = {
            "$id": "1",
            "$type": "NINA.Sequencer.Container.DeepSkyObjectContainer, NINA.Sequencer",
            "Target": {
                "$id": "2",
                "$type": "NINA.Astrometry.InputTarget, NINA.Astrometry",
                "Expanded": True,
                "TargetName": target_name,
                "PositionAngle": 0.0,
                "InputCoordinates": {
                    "$id": "3",
                    "$type": "NINA.Astrometry.InputCoordinates, NINA.Astrometry",
                    "RAHours": int(ra_h),
                    "RAMinutes": int(ra_m),
                    "RASeconds": float(ra_s),
                    "NegativeDec": negative_dec,
                    "DecDegrees": int(dec_d_abs),
                    "DecMinutes": int(dec_m),
                    "DecSeconds": float(dec_s)
                }
            },
            "ExposureInfoListExpanded": False,
            "ExposureInfoList": {
                "$id": "4",
                "$type": "NINA.Core.Utility.AsyncObservableCollection`1[[NINA.Sequencer.Utility.ExposureInfo, NINA.Sequencer]], NINA.Core",
                "$values": []
            },
            "Strategy": {
                "$type": "NINA.Sequencer.Container.ExecutionStrategy.SequentialStrategy, NINA.Sequencer"
            },
            "Name": target_name,
            "Conditions": {
                "$id": "5",
                "$type": "System.Collections.ObjectModel.ObservableCollection`1[[NINA.Sequencer.Conditions.ISequenceCondition, NINA.Sequencer]], System.ObjectModel",
                "$values": []
            },
            "IsExpanded": True,
            "Items": {
                "$id": "6",
                "$type": "System.Collections.ObjectModel.ObservableCollection`1[[NINA.Sequencer.SequenceItem.ISequenceItem, NINA.Sequencer]], System.ObjectModel",
                "$values": []
            },
            "Triggers": {
                "$id": "7",
                "$type": "System.Collections.ObjectModel.ObservableCollection`1[[NINA.Sequencer.Trigger.ISequenceTrigger, NINA.Sequencer]], System.ObjectModel",
                "$values": []
            },
            "Parent": None,
            "ErrorBehavior": 0,
            "Attempts": 1
        }
        
        return nina_json


class ThemeManager:
    """Manages GUI themes (dark/light mode)"""
    
    # Dark theme colors - FITS Viewer inspired (professional dark blue)
    DARK_THEME = {
        'bg': '#11161f',              # Very dark blue (main bg)
        'fg': '#d8e1f0',              # Light bright blue text
        'button_bg': '#1e2430',       # Dark blue-grey
        'button_fg': '#d8e1f0',       # Bright text
        'button_hover': '#2d3a4d',    # Lighter blue-grey
        'entry_bg': '#0f1419',        # Almost black blue
        'entry_fg': '#e9f1ff',        # Very bright blue-white
        'tree_bg': '#1a2132',         # Dark blue
        'tree_fg': '#d8e1f0',         # Light text
        'tree_selection': '#264f8c',  # Professional blue
        'accent': '#4a9eff',          # Sky blue accent
        'border': '#2d3a4d',          # Blue-grey border
        'label_fg': '#aac4ff',        # Light blue labels
    }
    
    # Light theme colors
    LIGHT_THEME = {
        'bg': '#f5f5f5',
        'fg': '#212121',
        'button_bg': '#e8e8e8',
        'button_fg': '#212121',
        'button_hover': '#d8d8d8',
        'entry_bg': '#ffffff',
        'entry_fg': '#212121',
        'tree_bg': '#fafafa',
        'tree_fg': '#212121',
        'tree_selection': '#bbdefb',
        'accent': '#1976d2',
        'border': '#cccccc',
        'label_fg': '#666666',
    }
    
    def __init__(self, root, dark_mode=False):
        self.root = root
        self.dark_mode = dark_mode
        self.current_theme = self.DARK_THEME if dark_mode else self.LIGHT_THEME
        self._apply_theme()
    
    def _apply_theme(self):
        """Apply theme to ttk styles"""
        style = ttk.Style()
        theme = self.current_theme
        
        # Use 'clam' theme as base (like FITS Viewer) for better customization
        style.theme_use('clam')
        
        # Configure button style
        style.configure('TButton',
                       background=theme['button_bg'],
                       foreground=theme['button_fg'],
                       borderwidth=1,
                       focuscolor='none',
                       padding=8,
                       relief='flat')
        style.map('TButton',
                 background=[('active', theme['button_hover']),
                            ('pressed', theme['accent']),
                            ('disabled', theme['border'])],
                 foreground=[('active', theme['fg']),
                            ('pressed', theme['fg']),
                            ('disabled', theme['label_fg'])])
        
        # Configure label style
        style.configure('TLabel',
                       background=theme['bg'],
                       foreground=theme['fg'])
        
        # Configure frame style
        style.configure('TFrame',
                       background=theme['bg'])
        
        # Configure LabelFrame style
        style.configure('TLabelFrame',
                       background=theme['tree_bg'],
                       foreground=theme['label_fg'],
                       bordercolor=theme['border'],
                       relief='flat')
        style.configure('TLabelFrame.Label',
                       background=theme['tree_bg'],
                       foreground=theme['label_fg'],
                       font=('Segoe UI', 9, 'bold'))
        
        # Configure FolderBox frame for folder selection
        # White/light background in both modes for maximum contrast
        folder_box_bg = '#ffffff' if not self.dark_mode else '#1a2132'
        style.configure('FolderBox.TFrame',
                       background=folder_box_bg,
                       borderwidth=1,
                       relief='solid')
        
        # Configure FolderButton style for "Select Folder" buttons (more obvious - accent color)
        folder_btn_color = '#1976d2' if not self.dark_mode else '#4a9eff'
        folder_btn_hover = '#1565c0' if not self.dark_mode else '#5aaeee'
        folder_btn_press = '#0d47a1' if not self.dark_mode else '#3a8ecc'
        
        style.configure('Folder.TButton',
                       background=folder_btn_color,
                       foreground='#ffffff',
                       borderwidth=1,
                       focuscolor='none',
                       padding=8,
                       relief='flat')
        style.map('Folder.TButton',
                 background=[('active', folder_btn_hover),
                            ('pressed', folder_btn_press),
                            ('disabled', theme['border'])],
                 foreground=[('active', '#ffffff'),
                            ('pressed', '#ffffff'),
                            ('disabled', theme['label_fg'])])
        
        # Configure entry style
        style.configure('TEntry',
                       fieldbackground=theme['entry_bg'],
                       background=theme['entry_bg'],
                       foreground=theme['entry_fg'],
                       borderwidth=1,
                       relief='solid')
        style.map('TEntry',
                 fieldbackground=[('focus', theme['entry_bg'])],
                 foreground=[('focus', theme['entry_fg'])])
        
        # Configure treeview - THIS IS THE KEY PART
        style.configure('Treeview',
                       background=theme['tree_bg'],
                       foreground=theme['tree_fg'],
                       fieldbackground=theme['tree_bg'],
                       borderwidth=0,
                       relief='flat')
        style.configure('Treeview.Heading',
                       background=theme['button_bg'],
                       foreground=theme['button_fg'],
                       borderwidth=1,
                       relief='raised')
        style.map('Treeview',
                 background=[('selected', theme['tree_selection']),
                            ('focus', theme['tree_selection'])],
                 foreground=[('selected', theme['tree_fg']),
                            ('focus', theme['tree_fg'])])
        style.map('Treeview.Heading',
                 background=[('active', theme['button_hover'])])
        
        # Configure progressbar
        style.configure('TProgressbar',
                       background=theme['accent'],
                       borderwidth=0,
                       relief='flat')
        
        # Configure scrollbar
        style.configure('TScrollbar',
                       background=theme['button_bg'],
                       troughcolor=theme['bg'],
                       borderwidth=1,
                       arrowcolor=theme['button_fg'],
                       darkcolor=theme['button_bg'],
                       lightcolor=theme['button_hover'])
        
        # Configure checkbutton
        style.configure('TCheckbutton',
                       background=theme['bg'],
                       foreground=theme['fg'],
                       focuscolor='none',
                       relief='flat',
                       borderwidth=0)
        style.map('TCheckbutton',
                 background=[('active', theme['bg']),
                            ('pressed', theme['bg']),
                            ('focus', theme['bg'])],
                 foreground=[('active', theme['fg']),
                            ('pressed', theme['fg'])])
        
        # Update root window background
        self.root.configure(bg=theme['bg'])
    
    def toggle_theme(self):
        """Toggle between dark and light modes"""
        self.dark_mode = not self.dark_mode
        self.current_theme = self.DARK_THEME if self.dark_mode else self.LIGHT_THEME
        self._apply_theme()
        return self.dark_mode
    
    def get_color(self, key):
        """Get color from current theme"""
        return self.current_theme.get(key, '#000000')


class FITSGUIDatabaseApp:
    """Main GUI Application"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("FITS Database Viewer")
        self.root.geometry("1400x750")
        
        # Initialize theme manager (start with light theme)
        self.theme_manager = ThemeManager(root, dark_mode=False)
        self.dark_mode = False
        
        self.database = FITSDatabase()
        self.current_data = []
        self.tree_id_to_entry = {}  # Maps tree item ID to database entry
        self.sort_column = None
        self.sort_reverse = False
        
        # Column dragging state
        self.drag_col = None
        self.drag_x = 0
        
        # Directory selection
        self.selected_directory = None
        self.selected_directory_2 = None
        self.only_light_frames = tk.BooleanVar(value=True)  # Checked by default - only show LIGHT frames
        self.trust_filename = tk.BooleanVar(value=False)
        self.search_filter = tk.StringVar()  # Universal search filter
        
        # Setup UI
        self._create_widgets()
        
        # Load existing database on startup
        self._load_existing_database()
        
    def _create_widgets(self):
        """Create GUI widgets"""
        
        # Top frame for controls
        control_frame = ttk.Frame(self.root, padding="10")
        control_frame.pack(fill=tk.X)
        
        # Folder selection box
        folder_box = ttk.Frame(control_frame, style='FolderBox.TFrame', padding="8")
        folder_box.pack(side=tk.LEFT, padx=5, pady=3)
        
        # Browse button 1
        ttk.Button(folder_box, text="Select Folder 1...", command=self._browse_folder, style='Folder.TButton').pack(side=tk.LEFT, padx=3)
        self.folder1_label = ttk.Label(folder_box, text="No folder")
        self.folder1_label.pack(side=tk.LEFT, padx=2)
        
        # Browse button 2
        ttk.Button(folder_box, text="Select Folder 2...", command=self._browse_folder_2, style='Folder.TButton').pack(side=tk.LEFT, padx=3)
        self.folder2_label = ttk.Label(folder_box, text="No folder")
        self.folder2_label.pack(side=tk.LEFT, padx=2)
        
        # Scan button
        ttk.Button(control_frame, text="Scan & Save Database", command=self._scan_directory).pack(side=tk.LEFT, padx=5)
        
        # Refresh button
        ttk.Button(control_frame, text="Refresh Last Scan", command=self._refresh_database).pack(side=tk.LEFT, padx=5)
        
        # Import CSV button
        ttk.Button(control_frame, text="Import CSV", command=self._import_csv).pack(side=tk.LEFT, padx=5)
        
        # Export button
        ttk.Button(control_frame, text="Export to CSV", command=self._export_csv).pack(side=tk.LEFT, padx=5)
        
        # Export All NINA JSON button
        ttk.Button(control_frame, text="Export All as NINA JSON", command=self._export_all_nina_json).pack(side=tk.LEFT, padx=5)
        
        # Launch FITS Viewer button
        ttk.Button(control_frame, text="Launch FITS Viewer", command=self._launch_fits_viewer_blank).pack(side=tk.LEFT, padx=5)
        
        # Theme toggle button (right aligned)
        # In light mode (default), show "🌙 Dark" to let user switch to dark
        # In dark mode, show "☀️ Light" to let user switch to light
        theme_btn_text = "🌙 Dark" if not self.dark_mode else "☀️ Light"
        self.theme_toggle_btn = ttk.Button(control_frame, text=theme_btn_text, command=self._toggle_theme, width=10)
        self.theme_toggle_btn.pack(side=tk.RIGHT, padx=5)
        
        # Status label
        self.status_label = ttk.Label(control_frame, text="Ready", relief=tk.SUNKEN)
        self.status_label.pack(side=tk.LEFT, padx=20, fill=tk.X, expand=True)
        
        # Progress bar frame
        progress_frame = ttk.Frame(self.root, padding="10")
        progress_frame.pack(fill=tk.X, padx=10)
        
        self.progress_label = ttk.Label(progress_frame, text="")
        self.progress_label.pack(side=tk.LEFT, padx=5)
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='determinate', length=300, maximum=100)
        self.progress_bar.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Filter frame - Now a universal search box
        filter_frame = ttk.LabelFrame(self.root, text="Search & Tools", padding="10")
        filter_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(filter_frame, text="Search (target, object, date, filter, etc):").pack(side=tk.LEFT, padx=5)
        self.search_box = ttk.Entry(filter_frame, textvariable=self.search_filter, width=40)
        self.search_box.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.search_box.bind('<KeyRelease>', lambda e: self._apply_search_filter())  # Real-time filtering
        
        # Checkbox for only LIGHT frames
        ttk.Checkbutton(filter_frame, text="Only light frames", variable=self.only_light_frames).pack(side=tk.LEFT, padx=5)
        
        # Checkbox for trusting filename (searches for LIGHT)
        ttk.Checkbutton(filter_frame, text="Trust filename (searches for LIGHT)", variable=self.trust_filename).pack(side=tk.LEFT, padx=5)
        
        # Main table frame with scrollbar
        table_frame = ttk.Frame(self.root, padding="10")
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create Treeview
        columns = ('Date', 'Session folder', 'Object', 'Telescope', 'Focal Length', 'Total Files', 'LIGHT Frames', 'Filters', 'Gain', 'Offset', 'Exptime Range', 'Total Integration Time')
        self.tree = ttk.Treeview(table_frame, columns=columns, height=20)
        
        # Define column headings and widths
        self.tree.column('#0', width=0, stretch=tk.NO)
        self.tree.column('Date', anchor=tk.W, width=100)
        self.tree.column('Session folder', anchor=tk.W, width=150)
        self.tree.column('Object', anchor=tk.W, width=120)
        self.tree.column('Telescope', anchor=tk.W, width=100)
        self.tree.column('Focal Length', anchor=tk.W, width=100)
        self.tree.column('Total Files', anchor=tk.CENTER, width=100)
        self.tree.column('LIGHT Frames', anchor=tk.CENTER, width=100)
        self.tree.column('Filters', anchor=tk.W, width=150)
        self.tree.column('Gain', anchor=tk.W, width=100)
        self.tree.column('Offset', anchor=tk.W, width=100)
        self.tree.column('Exptime Range', anchor=tk.W, width=120)
        self.tree.column('Total Integration Time', anchor=tk.CENTER, width=150)
        
        # Define headings with sorting
        for col in columns:
            self.tree.heading(col, text=col, command=lambda c=col: self._sort_by_column(c))
        
        # Add scrollbars
        vsb = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        
        self.tree.configure(yscroll=vsb.set, xscroll=hsb.set)
        
        # Grid layout for table
        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)
        
        # Bind double-click to show details
        self.tree.bind('<Double-1>', self._show_details)
        
        # Bind right-click to export menu
        self.tree.bind('<Button-3>', self._show_context_menu)
        
        # Bind column header dragging
        self.tree.bind('<Button-1>', self._on_col_drag_start)
        self.tree.bind('<B1-Motion>', self._on_col_drag_motion)
        self.tree.bind('<ButtonRelease-1>', self._on_col_drag_end)
        
        # Summary label
        self.summary_label = ttk.Label(self.root, text="", relief=tk.SUNKEN, padding="5")
        self.summary_label.pack(fill=tk.X, padx=10, pady=5)
        
        # Database info label
        self.db_info_label = ttk.Label(self.root, text="No database loaded", relief=tk.SUNKEN, padding="5")
        self.db_info_label.pack(fill=tk.X, padx=10, pady=2)
    
    def _load_existing_database(self):
        """Load existing database on startup"""
        result = self.database.load_database()
        if result['entries']:
            self._populate_table(result['entries'])
            self._update_db_info()
    
    def _refresh_database(self):
        """Refresh the last scanned directory"""
        if not self.database.last_scan_path:
            messagebox.showwarning("Warning", "No previous scan found. Please select a directory first.")
            return
        
        # Check if CSV exists in the last scanned folder
        csv_path = Path(self.database.last_scan_path) / "fits_database_index.csv"
        if csv_path.exists():
            result = messagebox.askyesno("Load from CSV", 
                f"Found recent scan index. Load from CSV instead of re-scanning?\n\n{csv_path}")
            if result:
                self._load_csv_data(csv_path)
                return
        
        # Otherwise, rescan
        self.selected_directory = self.database.last_scan_path
        self._scan_directory()
    
    def _toggle_theme(self):
        """Toggle between dark and light theme"""
        self.dark_mode = self.theme_manager.toggle_theme()
        
        # Update theme button text
        theme_btn_text = "☀️ Light" if self.dark_mode else "🌙 Dark"
        self.theme_toggle_btn.config(text=theme_btn_text)
    
    def _browse_folder(self):
        """Open folder browser for first directory"""
        folder = filedialog.askdirectory(initialdir=self.selected_directory, title="Select Folder 1")
        if folder:
            self.selected_directory = folder
            self.folder1_label.config(text=Path(folder).name[:20])
    
    def _browse_folder_2(self):
        """Open folder browser for second directory"""
        init_dir = self.selected_directory_2 if self.selected_directory_2 else str(Path.home() / 'Documents')
        folder = filedialog.askdirectory(initialdir=init_dir, title="Select Folder 2")
        if folder:
            self.selected_directory_2 = folder
            self.folder2_label.config(text=Path(folder).name[:20])
    
    def _update_progress(self, message: str):
        """Update progress display"""
        self.progress_label.config(text=message)
        self.root.update_idletasks()
    
    def _scan_directory(self):
        """Scan the selected directory/directories and save database"""
        if not self.selected_directory and not self.selected_directory_2:
            messagebox.showwarning("Warning", "Please select at least one directory")
            return
        
        self.status_label.config(text="Scanning... Please wait")
        self.progress_bar['value'] = 0
        self.progress_label.config(text="Initializing...")
        self.root.update()
        
        # Scan first directory
        results = {'total_folders': 0, 'folders_processed': 0, 'total_files': 0, 'errors': []}
        scan_paths = []
        
        if self.selected_directory:
            results_1 = self.database.scan_directory(self.selected_directory, ignore_cal_frames=False, only_light_frames=self.only_light_frames.get(), trust_filename=self.trust_filename.get(), progress_callback=self._update_progress)
            results['total_folders'] += results_1['total_folders']
            results['folders_processed'] += results_1['folders_processed']
            results['total_files'] += results_1['total_files']
            results['errors'].extend(results_1['errors'])
            scan_paths.append(self.selected_directory)
        
        # Scan second directory if provided
        if self.selected_directory_2:
            # Create a temporary database for the second scan
            temp_db = FITSDatabase()
            results_2 = temp_db.scan_directory(self.selected_directory_2, ignore_cal_frames=False, only_light_frames=self.only_light_frames.get(), trust_filename=self.trust_filename.get(), progress_callback=self._update_progress)
            results['total_folders'] += results_2['total_folders']
            results['folders_processed'] += results_2['folders_processed']
            results['total_files'] += results_2['total_files']
            results['errors'].extend(results_2['errors'])
            
            # Merge results from both directories
            self.database.entries.extend(temp_db.entries)
            scan_paths.append(self.selected_directory_2)
        
        # Save database to file
        if self.database.entries:
            # Use first directory as the scan path for metadata
            save_success = self.database.save_database(self.selected_directory if self.selected_directory else self.selected_directory_2)
            if save_success:
                save_msg = f" (Database saved to {self.database.DATABASE_FILE})"
            else:
                save_msg = " (Failed to save database)"
        else:
            save_msg = ""
        
        # Display results in table
        self._populate_table_default(self.database.entries)
        
        # Auto-save CSV to the scanned folder
        self._auto_save_csv_to_folder()
        
        # Update status
        scan_info = " + ".join([Path(p).name for p in scan_paths])
        msg = f"Scanned from: {scan_info}\nFolders: {results['total_folders']}, Found: {results['folders_processed']} with FITS, Total files: {results['total_files']}{save_msg}"
        filters_applied = []
        if self.only_light_frames.get():
            filters_applied.append("Only LIGHT frames")
        if self.trust_filename.get():
            filters_applied.append("Trust filename (LIGHT)")
        if filters_applied:
            msg += " (" + " + ".join(filters_applied) + ")"
        if results['errors']:
            msg += f"\nErrors: {len(results['errors'])}"
        self.status_label.config(text=msg)
        
        # Reset progress bar
        self.progress_bar['value'] = 100
        self.progress_label.config(text="✓ Scan complete!")
        
        self._update_db_info()
        
        if results['errors']:
            messagebox.showinfo("Scan Results", msg)
    
    def _calculate_integration_times(self, entry):
        """Calculate total integration time and per-filter breakdown for an entry.
        Returns (total_time_str, per_filter_dict)"""
        total_times = {}  # Filter name -> total integration time
        
        # Process each filter in this entry
        for filt in entry['filters']:
            filter_name = filt['name']
            frame_count = filt['count']
            exptimes_list = filt.get('exptimes_list', [])
            
            # Calculate average exposure time
            if exptimes_list:
                avg_exptime = sum(exptimes_list) / len(exptimes_list)
            else:
                # Fallback: try to parse the range string
                try:
                    exptime_str = filt.get('exptimes', 'N/A')
                    if '-' in exptime_str:
                        parts = exptime_str.split('-')
                        avg_exptime = (float(parts[0].strip()) + float(parts[1].strip())) / 2
                    else:
                        continue
                except (ValueError, IndexError, TypeError):
                    continue
            
            # Total integration time for this filter = frame_count * avg_exposure_time
            total_time = frame_count * avg_exptime
            total_times[filter_name] = total_time
        
        # Format total integration time string
        grand_total = sum(total_times.values()) if total_times else 0
        hours = int(grand_total // 3600)
        minutes = int((grand_total % 3600) // 60)
        seconds = int(grand_total % 60)
        
        if grand_total > 0:
            total_time_str = f"{hours}h {minutes}m {seconds}s"
        else:
            total_time_str = "N/A"
        
        return total_time_str, total_times
    
    def _get_entry_from_selection(self):
        """Get database entry from current tree selection
        
        Returns:
            Entry dict or None if no valid selection
        """
        selection = self.tree.selection()
        if not selection:
            return None
        
        item_id = selection[0]
        return self.tree_id_to_entry.get(item_id)
    
    def _populate_table_default(self, entries):
        """Populate table with entries sorted by date (most recent first)"""
        # Sort by date descending
        sorted_entries = sorted(entries, key=lambda x: x.get('capture_date', ''), reverse=True)
        self._populate_table(sorted_entries)
    
    def _populate_table(self, entries):
        """Populate table with entries as provided (no re-sorting)"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        self.current_data = entries
        
        if not entries:
            self._update_summary()
            return
        
        # Add each entry as a row (entries already sorted)
        for entry in entries:
            total_time_str, _ = self._calculate_integration_times(entry)
            
            values = (
                entry.get('capture_date', 'Unknown'),
                entry.get('target_name', 'Unknown'),
                entry.get('object', 'Unknown'),
                entry.get('telescope', 'Unknown'),
                entry.get('focal_length', 'Unknown'),
                entry.get('total_files', 0),
                entry.get('light_frames', 0),
                entry.get('unique_filters', 'N/A'),
                entry.get('gain_range', 'N/A'),
                entry.get('offset_range', 'N/A'),
                entry.get('exptime_range', 'N/A'),
                total_time_str,
            )
            self.tree.insert('', tk.END, values=values)
        
        self._update_summary()
    
    def _update_summary(self):
        """Update summary statistics"""
        if not self.current_data:
            self.summary_label.config(text="No data")
            return
        
        total_entries = len(self.current_data)
        total_files = sum(e['total_files'] for e in self.current_data)
        total_light = sum(e['light_frames'] for e in self.current_data)
        
        summary = f"Total Targets: {total_entries} | Total Files: {total_files} | Total LIGHT Frames: {total_light}"
        self.summary_label.config(text=summary)
    
    def _update_db_info(self):
        """Update database info label"""
        info = self.database.get_database_info()
        if info['scan_time']:
            time_str = info['scan_time'].strftime("%Y-%m-%d %H:%M:%S")
            duration_str = f"took {info['load_duration']:.1f}s" if info['load_duration'] > 0 else ""
            db_msg = f"Database loaded from: {info['scan_path']} | Last scan: {time_str} {duration_str} | Entries: {info['entry_count']}"
        else:
            db_msg = "No database loaded"
        self.db_info_label.config(text=db_msg)
    
    def _apply_search_filter(self):
        """Apply real-time search filter across all columns with comma-separated AND logic"""
        search_text = self.search_filter.get().lower().strip()
        
        if not search_text:
            # No filter, show all entries sorted by date
            self._populate_table_default(self.database.entries)
            return
        
        # Split by comma and strip whitespace from each term
        search_terms = [term.strip() for term in search_text.split(',') if term.strip()]
        
        # Search across all possible fields
        filtered = []
        for entry in self.database.entries:
            # Check against all searchable fields
            searchable_values = [
                str(entry.get('capture_date', '')).lower(),
                str(entry.get('target_name', '')).lower(),
                str(entry.get('object', '')).lower(),
                str(entry.get('telescope', '')).lower(),
                str(entry.get('focal_length', '')).lower(),
                str(entry.get('unique_filters', '')).lower(),
            ]
            
            # ALL search terms must match at least one field (AND logic)
            if all(any(term in field for field in searchable_values) for term in search_terms):
                filtered.append(entry)
        
        self._populate_table(filtered)
    
    def _apply_filters(self):
        """Legacy method for backward compatibility - now calls search filter"""
        self._apply_search_filter()
    
    def _clear_filters(self):
        """Legacy method for backward compatibility"""
        self.search_filter.set("")
        self._populate_table_default(self.database.entries)
    
    def _sort_by_column(self, col):
        """Sort table by column"""
        # Toggle sort direction if same column clicked
        if self.sort_column == col:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = col
            self.sort_reverse = False
        
        # Map column names to data keys
        sort_key_map = {
            'Date': 'capture_date',
            'Session folder': 'target_name',
            'Object': 'object',
            'Telescope': 'telescope',
            'Focal Length': 'focal_length',
            'Total Files': 'total_files',
            'LIGHT Frames': 'light_frames',
            'Filters': 'unique_filters',
            'Gain': 'gain_range',
            'Offset': 'offset_range',
            'Exptime Range': 'exptime_range'
        }
        
        sort_key = sort_key_map.get(col)
        if not sort_key:
            return
        
        # Sort numeric columns numerically
        numeric_keys = {'total_files', 'light_frames'}
        
        if sort_key in numeric_keys:
            sorted_data = sorted(self.current_data, key=lambda x: x.get(sort_key, 0), reverse=self.sort_reverse)
        else:
            sorted_data = sorted(self.current_data, key=lambda x: str(x.get(sort_key, '')).lower(), reverse=self.sort_reverse)
        
        self._populate_table(sorted_data)
    
    def _show_details(self, event):
        """Show detailed information for a row"""
        item_id = self.tree.identify('item', event.x, event.y)
        if not item_id:
            return
        
        # Get row values
        values = self.tree.item(item_id, 'values')
        if not values or not any(str(v).strip() for v in values):
            return
        
        # Find matching entry by target_name and date
        target_name = values[1] if len(values) > 1 else None
        capture_date = values[0] if len(values) > 0 else None
        
        if not target_name:
            return
        
        # Find matching entry in current_data
        matching_entry = None
        for entry in self.current_data:
            if (entry.get('target_name') == target_name and 
                entry.get('capture_date') == capture_date):
                matching_entry = entry
                break
        
        if matching_entry:
            self._show_details_from_entry(matching_entry)
    
    def _on_col_drag_start(self, event):
        """Start column drag"""
        region = self.tree.identify_region(event.x, event.y)
        if region == "heading":
            col = self.tree.identify_column(event.x)
            self.drag_col = col
            self.drag_x = event.x
    
    def _on_col_drag_motion(self, event):
        """Handle column drag motion"""
        if self.drag_col is None:
            return
        
        # Only process if cursor is still on heading
        region = self.tree.identify_region(event.x, event.y)
        if region != "heading":
            return
    
    def _on_col_drag_end(self, event):
        """End column drag and reorder columns"""
        if self.drag_col is None:
            return
        
        # Only process if drag was significant
        if abs(event.x - self.drag_x) < 10:
            self.drag_col = None
            return
        
        # Identify the target column
        target_col = self.tree.identify_column(event.x)
        if target_col == self.drag_col:
            self.drag_col = None
            return
        
        # Get all columns
        columns = list(self.tree['columns'])
        
        # Parse column indices (they end with #)
        try:
            drag_idx = int(self.drag_col.strip('#')) - 1
            target_idx = int(target_col.strip('#')) - 1
            
            if 0 <= drag_idx < len(columns) and 0 <= target_idx < len(columns):
                # Swap columns
                columns[drag_idx], columns[target_idx] = columns[target_idx], columns[drag_idx]
                
                # Update the treeview column order
                self.tree['columns'] = columns
                
                # Refresh display
                self._populate_table(self.current_data)
        except (ValueError, IndexError):
            pass
        
        self.drag_col = None
    
    def _show_context_menu(self, event):
        """Show context menu on right-click"""
        item_id = self.tree.identify('item', event.x, event.y)
        if not item_id:
            return
        
        # Get row values
        values = self.tree.item(item_id, 'values')
        if not values or not any(str(v).strip() for v in values):
            return
        
        # Find matching entry by target_name and date
        target_name = values[1] if len(values) > 1 else None
        capture_date = values[0] if len(values) > 0 else None
        
        if not target_name:
            return
        
        # Find matching entry in current_data
        matching_entry = None
        for entry in self.current_data:
            if (entry.get('target_name') == target_name and 
                entry.get('capture_date') == capture_date):
                matching_entry = entry
                break
        
        if not matching_entry:
            return
        
        # Create context menu
        context_menu = tk.Menu(self.root, tearoff=0)
        context_menu.add_command(label="Export as NINA JSON", command=lambda: self._export_nina_json_from_entry(matching_entry))
        context_menu.add_command(label="Open Folder", command=lambda: self._open_folder_from_entry(matching_entry))
        
        # Check for ImageMetaData.csv
        # Use full path from folder_name which should be absolute
        folder_path = matching_entry.get('folder_name', '')
        csv_path = os.path.join(folder_path, 'ImageMetaData.csv')
        
        # If folder_path is not absolute, try to find it
        if not os.path.isabs(folder_path):
            # Try to reconstruct from scan path and folder name
            info = self.database.get_database_info()
            if info['scan_path']:
                folder_path = os.path.join(info['scan_path'], os.path.basename(folder_path))
                csv_path = os.path.join(folder_path, 'ImageMetaData.csv')
        
        if os.path.exists(csv_path):
            context_menu.add_command(label="Read Image Metadata", command=lambda: self._read_image_metadata_from_path(csv_path))
        
        context_menu.add_command(label="Launch in FITS Viewer", command=lambda: self._launch_fits_viewer(matching_entry))
        context_menu.add_separator()
        context_menu.add_command(label="Rename Session Folder", command=lambda: self._rename_session_folder(matching_entry))
        context_menu.add_command(label="Show Details", command=lambda: self._show_details_from_entry(matching_entry))
        
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()
    
    def _export_nina_json(self, event):
        """Export selected target as NINA JSON file"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "No target selected")
            return
        
        item_index = self.tree.index(selection[0])
        entry = self.current_data[item_index]
        
        # Check if we have coordinates
        if not entry.get('ra_hms') or not entry.get('dec_dms'):
            messagebox.showwarning("Warning", f"No coordinates found for {entry['target_name']}\nCannot export NINA JSON without RA/DEC")
            return
        
        try:
            # Prepare data for NINA JSON
            filters = [f['name'] for f in entry['filters']]
            exposures = []
            gains = []
            
            for filt in entry['filters']:
                # Parse exposure times from string
                exptime_str = filt['exptimes']  # Format: "min-max"
                if '-' in exptime_str:
                    try:
                        min_exp, max_exp = exptime_str.split('-')
                        exposures.extend([float(min_exp.strip()), float(max_exp.strip())])
                    except (ValueError, AttributeError):
                        pass
                
                # Parse gains from string
                gain_str = filt['gains']  # Format: "min-max"
                if '-' in gain_str:
                    try:
                        min_gain, max_gain = gain_str.split('-')
                        gains.extend([float(min_gain.strip()), float(max_gain.strip())])
                    except (ValueError, AttributeError):
                        pass
            
            # Generate NINA JSON
            nina_json = FITSDatabase.generate_nina_json(
                target_name=entry['target_name'],
                ra_hms=entry.get('ra_hms'),
                dec_dms=entry.get('dec_dms'),
                filters=filters or None,
                exposures=exposures or None,
                gains=gains or None
            )
            
            if not nina_json:
                messagebox.showerror("Error", "Failed to generate NINA JSON")
                return
            
            # Ask user where to save
            file_name = f"{entry['target_name']}.json"
            save_path = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                initialfile=file_name
            )
            
            if not save_path:
                return  # User cancelled
            
            # Save JSON file
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(nina_json, f, indent=2)
            
            messagebox.showinfo("Success", f"NINA JSON exported to:\n{save_path}")
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export NINA JSON:\n{str(e)}")
    
    def _open_folder(self, event):
        """Open the folder where the selected target data lives"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "No target selected")
            return
        
        item_index = self.tree.index(selection[0])
        entry = self.current_data[item_index]
        
        try:
            # Get the folder path from the database root and the folder name
            # The folder path would be: root_path / (capture_date target_name)
            # We need to reconstruct this from the database info
            
            # First, try to find the folder by checking the scan paths
            folder_found = False
            
            # Check in the main database scanned paths
            if self.selected_directory:
                potential_path = Path(self.selected_directory) / entry['folder_name']
                if potential_path.exists():
                    # Open with Windows Explorer
                    if os.name == 'nt':  # Windows
                        os.startfile(str(potential_path))
                    else:  # Linux/Mac
                        subprocess.Popen(['xdg-open', str(potential_path)])
                    folder_found = True
                    return
            
            # Check in secondary directory if provided
            if self.selected_directory_2 and not folder_found:
                potential_path = Path(self.selected_directory_2) / entry['folder_name']
                if potential_path.exists():
                    # Open with Windows Explorer
                    if os.name == 'nt':  # Windows
                        os.startfile(str(potential_path))
                    else:  # Linux/Mac
                        subprocess.Popen(['xdg-open', str(potential_path)])
                    folder_found = True
                    return
            
            if not folder_found:
                messagebox.showwarning("Warning", f"Could not locate folder: {entry['folder_name']}\nPlease select the directory where the data is stored.")
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open folder:\n{str(e)}")
    
    def _read_image_metadata(self, event):
        """Read and plot image metadata from ImageMetaData.csv"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "No target selected")
            return
        
        item_index = self.tree.index(selection[0])
        entry = self.current_data[item_index]
        
        try:
            # Find the folder path
            folder_path = None
            
            if self.selected_directory:
                potential_path = Path(self.selected_directory) / entry['folder_name']
                if potential_path.exists():
                    folder_path = str(potential_path)
            
            if not folder_path and self.selected_directory_2:
                potential_path = Path(self.selected_directory_2) / entry['folder_name']
                if potential_path.exists():
                    folder_path = str(potential_path)
            
            if not folder_path:
                messagebox.showwarning("Warning", f"Could not locate folder: {entry['folder_name']}")
                return
            
            # Check if CSV exists
            csv_path = Path(folder_path) / "ImageMetaData.csv"
            if not csv_path.exists():
                messagebox.showwarning("Warning", f"ImageMetaData.csv not found in:\n{folder_path}")
                return
            
            # Read and plot metadata
            df = self.database._read_image_metadata_csv(folder_path)
            if df is None or df.empty:
                messagebox.showerror("Error", "Failed to read or parse CSV file")
                return
            
            # Check for required columns
            required_cols = ['ADUMean', 'DetectedStars', 'HFR', 'GuidingRMS']
            available_cols = [col for col in required_cols if col in df.columns]
            
            if not available_cols:
                messagebox.showerror("Error", f"CSV must contain at least one of: {', '.join(required_cols)}")
                return
            
            # Plot the data
            success = FITSDatabase._plot_image_metadata(df, entry['target_name'])
            if not success:
                messagebox.showerror("Error", "Could not plot metadata")
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read image metadata:\n{str(e)}")
    
    def _export_all_nina_json(self):
        """Batch export all targets as NINA JSON files"""
        if not self.current_data:
            messagebox.showwarning("Warning", "No targets to export")
            return
        
        # Ask user to select output folder
        output_folder = filedialog.askdirectory(title="Select folder to save NINA JSON files")
        if not output_folder:
            return  # User cancelled
        
        output_path = Path(output_folder)
        
        # Count valid targets (with coordinates)
        valid_targets = [e for e in self.current_data if e.get('ra_hms') and e.get('dec_dms')]
        invalid_targets = len(self.current_data) - len(valid_targets)
        
        if not valid_targets:
            messagebox.showwarning("Warning", "No targets with coordinates found\nCannot export any NINA JSON files")
            return
        
        try:
            success_count = 0
            error_list = []
            
            for entry in valid_targets:
                try:
                    # Prepare data for NINA JSON
                    filters = [f['name'] for f in entry['filters']]
                    exposures = []
                    gains = []
                    
                    for filt in entry['filters']:
                        # Parse exposure times
                        exptime_str = filt['exptimes']
                        if '-' in exptime_str:
                            try:
                                min_exp, max_exp = exptime_str.split('-')
                                exposures.extend([float(min_exp.strip()), float(max_exp.strip())])
                            except (ValueError, AttributeError):
                                pass
                        
                        # Parse gains
                        gain_str = filt['gains']
                        if '-' in gain_str:
                            try:
                                min_gain, max_gain = gain_str.split('-')
                                gains.extend([float(min_gain.strip()), float(max_gain.strip())])
                            except (ValueError, AttributeError):
                                pass
                    
                    # Generate NINA JSON
                    nina_json = FITSDatabase.generate_nina_json(
                        target_name=entry['target_name'],
                        ra_hms=entry.get('ra_hms'),
                        dec_dms=entry.get('dec_dms'),
                        filters=filters or None,
                        exposures=exposures or None,
                        gains=gains or None
                    )
                    
                    if not nina_json:
                        error_list.append(f"{entry['target_name']}: Failed to generate JSON")
                        continue
                    
                    # Sanitize filename
                    safe_name = "".join(c for c in entry['target_name'] if c.isalnum() or c in (' ', '-', '_')).replace(' ', '_')
                    file_path = output_path / f"{safe_name}.json"
                    
                    # Save JSON file
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(nina_json, f, indent=2)
                    
                    success_count += 1
                    
                except Exception as e:
                    error_list.append(f"{entry['target_name']}: {str(e)}")
            
            # Show results
            message = f"Successfully exported {success_count}/{len(valid_targets)} targets as NINA JSON\nLocation: {output_folder}"
            if invalid_targets > 0:
                message += f"\n\n({invalid_targets} targets skipped due to missing coordinates)"
            if error_list:
                message += f"\n\nErrors:\n" + "\n".join(error_list[:5])
                if len(error_list) > 5:
                    message += f"\n... and {len(error_list) - 5} more"
            
            messagebox.showinfo("Batch Export Complete", message)
            
        except Exception as e:
            messagebox.showerror("Error", f"Batch export failed:\n{str(e)}")
    
    def _auto_save_csv_to_folder(self):
        """Automatically save CSV to the first scanned folder"""
        if not self.selected_directory:
            return
        
        try:
            csv_path = Path(self.selected_directory) / "fits_database_index.csv"
            with open(csv_path, 'w', encoding='utf-8') as f:
                # Write header
                f.write("Date,Target,Object,Telescope,Focal Length,Total Files,LIGHT Frames,Filters,Gain,Offset,Exptime Range\n")
                
                # Write data
                for entry in self.current_data:
                    f.write(f'"{entry["capture_date"]}","{entry["target_name"]}","{entry["object"]}","{entry["telescope"]}","{entry["focal_length"]}",{entry["total_files"]},{entry["light_frames"]},"{entry["unique_filters"]}","{entry["gain_range"]}","{entry.get("offset_range", "N/A")}","{entry["exptime_range"]}"\n')
            
            self.status_label.config(text=self.status_label.cget("text") + f"\n✓ Index saved to: {csv_path}")
        except Exception as e:
            print(f"Error saving CSV: {str(e)}")
    
    def _load_csv_data(self, csv_path: Path):
        """Load data from previously saved CSV file"""
        try:
            entries = []
            with open(csv_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if len(lines) <= 1:
                    messagebox.showwarning("Error", "CSV file is empty")
                    return
                
                # Skip header
                for line in lines[1:]:
                    parts = []
                    in_quotes = False
                    current = ""
                    for char in line:
                        if char == '"':
                            in_quotes = not in_quotes
                        elif char == ',' and not in_quotes:
                            parts.append(current)
                            current = ""
                            continue
                        current += char
                    parts.append(current.strip())
                    
                    if len(parts) >= 10:
                        entry = {
                            'capture_date': parts[0].strip('"'),
                            'target_name': parts[1].strip('"'),
                            'object': parts[2].strip('"'),
                            'telescope': parts[3].strip('"'),
                            'focal_length': parts[4].strip('"'),
                            'total_files': int(parts[5]),
                            'light_frames': int(parts[6]),
                            'unique_filters': parts[7].strip('"'),
                            'gain_range': parts[8].strip('"'),
                            'exptime_range': parts[9].strip().strip('"'),
                            'folder_name': 'N/A',
                            'image_types': {},
                            'filters': []
                        }
                        entries.append(entry)
            
            if entries:
                self.current_data = entries
                self._populate_table(entries)
                self.status_label.config(text=f"Loaded {len(entries)} entries from CSV: {csv_path}")
                self._update_db_info()
            else:
                messagebox.showwarning("Error", "No valid data found in CSV")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load CSV: {str(e)}")
    
    def _export_csv(self):
        """Export data to CSV"""
        if not self.current_data:
            messagebox.showwarning("Warning", "No data to export")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                # Write header
                f.write("Date,Target,Object,Telescope,Focal Length,Total Files,LIGHT Frames,Filters,Gain,Offset,Exptime Range\n")
                
                # Write data
                for entry in self.current_data:
                    f.write(f'"{entry["capture_date"]}","{entry["target_name"]}","{entry["object"]}","{entry["telescope"]}","{entry["focal_length"]}",{entry["total_files"]},{entry["light_frames"]},"{entry["unique_filters"]}","{entry["gain_range"]}","{entry.get("offset_range", "N/A")}","{entry["exptime_range"]}"\n')
            
            messagebox.showinfo("Success", f"Data exported to {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export: {str(e)}")
    
    def _import_csv(self):
        """Import data from CSV and load into the database viewer"""
        file_path = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Select CSV file to import"
        )
        
        if not file_path:
            return
        
        try:
            self._load_csv_data(file_path)
            messagebox.showinfo("Success", f"Data imported from {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to import: {str(e)}")
    
    def _export_nina_json_from_entry(self, entry):
        """Export target as NINA JSON file using entry object"""
        if not entry.get('ra_hms') or not entry.get('dec_dms'):
            messagebox.showwarning("Warning", f"No coordinates found for {entry['target_name']}\nCannot export NINA JSON without RA/DEC")
            return
        
        try:
            # Prepare data for NINA JSON
            filters = [f['name'] for f in entry.get('filters', [])]
            exposures = []
            gains = []
            
            for filt in entry.get('filters', []):
                # Parse exposure times
                exptime_str = filt.get('exptimes', '')
                if '-' in exptime_str:
                    try:
                        min_exp, max_exp = exptime_str.split('-')
                        exposures.extend([float(min_exp.strip()), float(max_exp.strip())])
                    except (ValueError, AttributeError):
                        pass
                
                # Parse gains
                gain_str = filt.get('gains', '')
                if '-' in gain_str:
                    try:
                        min_gain, max_gain = gain_str.split('-')
                        gains.extend([float(min_gain.strip()), float(max_gain.strip())])
                    except (ValueError, AttributeError):
                        pass
            
            # Generate NINA JSON
            nina_json = FITSDatabase.generate_nina_json(
                target_name=entry['target_name'],
                ra_hms=entry.get('ra_hms'),
                dec_dms=entry.get('dec_dms'),
                filters=filters or None,
                exposures=exposures or None,
                gains=gains or None
            )
            
            if not nina_json:
                messagebox.showerror("Error", "Failed to generate NINA JSON")
                return
            
            # Ask user where to save
            file_name = f"{entry['target_name']}.json"
            save_path = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                initialfile=file_name
            )
            
            if not save_path:
                return
            
            # Save JSON file
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(nina_json, f, indent=2)
            
            messagebox.showinfo("Success", f"NINA JSON exported to:\n{save_path}")
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export NINA JSON:\n{str(e)}")
    
    def _open_folder_from_entry(self, entry):
        """Open the folder for a given entry"""
        try:
            folder_name = entry.get('folder_name', '')
            if not folder_name:
                messagebox.showwarning("Warning", "Folder path not found in entry")
                return
            
            # Try to find the folder in scanned directories
            folder_found = False
            
            if self.selected_directory:
                potential_path = Path(self.selected_directory) / folder_name
                if potential_path.exists():
                    if os.name == 'nt':
                        os.startfile(str(potential_path))
                    else:
                        subprocess.Popen(['xdg-open', str(potential_path)])
                    folder_found = True
                    return
            
            if self.selected_directory_2 and not folder_found:
                potential_path = Path(self.selected_directory_2) / folder_name
                if potential_path.exists():
                    if os.name == 'nt':
                        os.startfile(str(potential_path))
                    else:
                        subprocess.Popen(['xdg-open', str(potential_path)])
                    folder_found = True
                    return
            
            if not folder_found:
                messagebox.showwarning("Warning", f"Could not locate folder: {folder_name}\nPlease select the directory where the data is stored.")
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open folder:\n{str(e)}")
    
    def _launch_fits_viewer(self, entry):
        """Launch FITS Viewer with the folder for this entry"""
        try:
            folder_name = entry.get('folder_name', '')
            if not folder_name:
                messagebox.showwarning("Warning", "Folder path not found in entry")
                return
            
            # folder_name should be absolute path already
            if os.path.isabs(folder_name):
                folder_path = folder_name
            else:
                # Fallback: try to construct path from selected directory
                if self.selected_directory:
                    folder_path = os.path.join(self.selected_directory, os.path.basename(folder_name))
                elif self.selected_directory_2:
                    folder_path = os.path.join(self.selected_directory_2, os.path.basename(folder_name))
                else:
                    messagebox.showwarning("Warning", "Could not determine folder path")
                    return
            
            if not os.path.exists(folder_path):
                messagebox.showwarning("Warning", f"Folder not found: {folder_path}")
                return
            
            # Launch FITS Viewer - now in same FITS_Library folder
            script_dir = os.path.dirname(os.path.abspath(__file__))
            fits_viewer_path = os.path.join(script_dir, 'FITS_Viewer', 'fits_viewer.py')
            
            if not os.path.exists(fits_viewer_path):
                messagebox.showerror("Error", f"FITS Viewer not found at:\n{fits_viewer_path}")
                return
            
            # Start FITS Viewer with the folder as argument using --folder flag
            if os.name == 'nt':
                # Windows: use python to run the script with --folder flag
                subprocess.Popen([sys.executable, fits_viewer_path, '--folder', folder_path])
            else:
                # Linux/Mac
                subprocess.Popen([sys.executable, fits_viewer_path, '--folder', folder_path])
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch FITS Viewer:\n{str(e)}")
    
    def _launch_fits_viewer_blank(self):
        """Launch FITS Viewer without a folder (user will pick one inside the app)"""
        try:
            # Get path to FITS Viewer
            script_dir = os.path.dirname(os.path.abspath(__file__))
            fits_viewer_path = os.path.join(script_dir, 'FITS_Viewer', 'fits_viewer.py')
            
            if not os.path.exists(fits_viewer_path):
                messagebox.showerror("Error", f"FITS Viewer not found at:\n{fits_viewer_path}")
                return
            
            # Start FITS Viewer without folder (will open file picker inside app)
            subprocess.Popen([sys.executable, fits_viewer_path])
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch FITS Viewer:\n{str(e)}")
    
    def _rename_session_folder(self, entry):
        """Rename a session folder"""
        try:
            folder_name = entry.get('folder_name', '')
            if not folder_name:
                messagebox.showwarning("Warning", "Folder path not found in entry")
                return
            
            # Get current folder name (just the base name)
            current_name = os.path.basename(folder_name)
            
            # Create a simple dialog to get new name with current name pre-filled
            from tkinter.simpledialog import askstring
            new_name = askstring("Rename Session Folder", 
                                 f"Enter new name for session folder:",
                                 parent=self.root,
                                 initialvalue=current_name)
            
            if not new_name or new_name.strip() == '' or new_name == current_name:
                return  # User cancelled or entered same name
            
            new_name = new_name.strip()
            
            # Validate new name (no special characters that would be problematic)
            if any(char in new_name for char in ['<', '>', ':', '"', '|', '?', '*']):
                messagebox.showerror("Error", "New folder name contains invalid characters: < > : \" | ? *")
                return
            
            # Find the actual folder path
            folder_found = False
            old_folder_path = None
            parent_dir = None
            scan_directory = None
            
            if self.selected_directory:
                potential_path = Path(self.selected_directory) / folder_name
                if potential_path.exists():
                    old_folder_path = str(potential_path)
                    parent_dir = str(potential_path.parent)
                    scan_directory = self.selected_directory
                    folder_found = True
            
            if not folder_found and self.selected_directory_2:
                potential_path = Path(self.selected_directory_2) / folder_name
                if potential_path.exists():
                    old_folder_path = str(potential_path)
                    parent_dir = str(potential_path.parent)
                    scan_directory = self.selected_directory_2
                    folder_found = True
            
            if not folder_found:
                messagebox.showerror("Error", f"Could not locate folder: {folder_name}")
                return
            
            # Create new path
            new_folder_path = os.path.join(parent_dir, new_name)
            
            # Check if new name already exists
            if os.path.exists(new_folder_path):
                messagebox.showerror("Error", f"A folder with the name '{new_name}' already exists in this location")
                return
            
            # Rename the folder
            try:
                os.rename(old_folder_path, new_folder_path)
                messagebox.showinfo("Success", f"Successfully renamed folder from:\n{current_name}\n\nto:\n{new_name}")
                
                # Smart update: just update the renamed entry without full rescan
                # Parse new_name to separate date from target if date pattern exists
                date_pattern = re.compile(r'^(\d{4}-\d{2}-\d{2})\s+(.+)$')
                date_match = date_pattern.match(new_name)
                
                # Determine new capture_date and target_name from new_name
                if date_match:
                    # New name has date pattern: extract date and target separately
                    new_capture_date = date_match.group(1)
                    new_target_name = date_match.group(2)
                else:
                    # New name has NO date pattern: use only the name as target
                    new_capture_date = None  # Keep existing or use empty
                    new_target_name = new_name  # Use full new name as target
                
                # Find and update the entry in current_data by exact path match
                for entry in self.current_data:
                    if entry.get('folder_name', '') == old_folder_path:
                        # Update the entry with new folder path
                        entry['folder_name'] = new_folder_path
                        entry['target_name'] = new_target_name
                        # Only update capture_date if new name has date pattern
                        if new_capture_date:
                            entry['capture_date'] = new_capture_date
                
                # Also update in database entries - match by old path for precise update
                for entry in self.database.entries:
                    if entry.get('folder_name', '') == old_folder_path:
                        entry['folder_name'] = new_folder_path
                        entry['target_name'] = new_target_name
                        # Only update capture_date if new name has date pattern
                        if new_capture_date:
                            entry['capture_date'] = new_capture_date
                
                # Refresh table without full rescan
                self._populate_table(self.current_data)
                messagebox.showinfo("Updated", f"Folder data updated successfully!")
            except PermissionError:
                messagebox.showerror("Error", "Permission denied: Cannot rename folder. Make sure no files are in use.")
            except Exception as rename_error:
                messagebox.showerror("Error", f"Failed to rename folder:\n{str(rename_error)}")
        
        except Exception as e:
            messagebox.showerror("Error", f"Error during rename operation:\n{str(e)}")
    
    def _read_image_metadata_from_path(self, csv_path):
        """Read and plot image metadata from CSV path with flexible column detection"""
        try:
            df = pd.read_csv(csv_path)
            
            # Check available columns
            print(f"Available columns: {list(df.columns)}")
            
            # Detect x-axis column names
            time_col = None
            for col_name in ['ExposureStartUTC', 'ExposureStart', 'StartUTC', 'Time', 'Timestamp']:
                if col_name in df.columns:
                    time_col = col_name
                    break
            
            # Parse time if available
            has_time = False
            if time_col:
                try:
                    df['_time'] = pd.to_datetime(df[time_col])
                    has_time = True
                except:
                    pass
            
            # Find available metric columns
            possible_metrics = ['ADUMean', 'Mean ADU', 'DetectedStars', 'Stars', 'HFR', 'GuidingRMS', 'RMS']
            available_metrics = [col for col in possible_metrics if col in df.columns]
            
            # If HFR not found in CSV, try to extract from filenames
            if 'HFR' not in available_metrics and 'FileName' in df.columns:
                try:
                    hfr_values = []
                    for filename in df['FileName']:
                        # Pattern: -X.XX.fits where X.XX is the HFR value
                        match = re.search(r'-(\d+\.?\d*)\.(fits|fit)$', str(filename), re.IGNORECASE)
                        if match:
                            hfr_values.append(float(match.group(1)))
                        else:
                            hfr_values.append(None)
                    
                    if any(v is not None for v in hfr_values):
                        df['HFR'] = hfr_values
                        available_metrics.append('HFR')
                        print(f"Extracted HFR values from filenames: {sum(1 for v in hfr_values if v is not None)} frames")
                except Exception as e:
                    print(f"Could not extract HFR from filenames: {str(e)}")
            
            if not available_metrics:
                messagebox.showerror("Error", "No metric columns found in CSV (ADUMean, DetectedStars, HFR, GuidingRMS, etc.)")
                return
            
            # Create plot window
            plot_window = tk.Toplevel(self.root)
            plot_window.title("Image Metadata Analysis")
            
            # Determine layout based on available metrics
            num_plots = len(available_metrics)
            if num_plots == 1:
                plot_cols = 1
                plot_rows = 1
                plot_window.geometry("700x500")
            elif num_plots == 2:
                plot_cols = 2
                plot_rows = 1
                plot_window.geometry("1000x500")
            elif num_plots <= 4:
                plot_cols = 2
                plot_rows = 2
                plot_window.geometry("1000x700")
            else:
                plot_cols = 3
                plot_rows = (num_plots + 2) // 3
                plot_window.geometry("1200x400 + (plot_rows * 300)")
            
            # Control frame
            control_frame = ttk.Frame(plot_window)
            control_frame.pack(fill=tk.X, padx=10, pady=5)
            
            if has_time:
                ttk.Label(control_frame, text="Time Range (HH:mm):").pack(side=tk.LEFT, padx=5)
                
                time_min = df['_time'].min()
                time_max = df['_time'].max()
                time_range_seconds = (time_max - time_min).total_seconds()
                
                range_var = tk.StringVar(value=f"{time_min.strftime('%H:%M')} - {time_max.strftime('%H:%M')}")
                ttk.Label(control_frame, textvariable=range_var, font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=10)
                
                reset_button = ttk.Button(control_frame, text="Reset Zoom")
                reset_button.pack(side=tk.RIGHT, padx=5)
                
                ttk.Label(control_frame, text="Zoom:").pack(side=tk.LEFT, padx=5)
                
                # Create matplotlib figure
                fig = Figure(figsize=(max(7, plot_cols * 4), max(5, plot_rows * 3)), dpi=80)
                
                # Store state
                plot_state = {
                    'fig': fig,
                    'df': df,
                    'range_var': range_var,
                    'time_min': time_min,
                    'time_max': time_max,
                    'available_metrics': available_metrics,
                    'plot_rows': plot_rows,
                    'plot_cols': plot_cols,
                    'canvas': None
                }
                
                # Sliders frame
                slider_frame = ttk.Frame(plot_window)
                slider_frame.pack(fill=tk.X, padx=10, pady=5)
                
                start_slider = ttk.Scale(slider_frame, from_=0, to=100, orient=tk.HORIZONTAL,
                                        command=lambda v: self._update_time_range_flexible(df, fig, plot_state, int(float(v)), None, range_var))
                start_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
                
                end_slider = ttk.Scale(slider_frame, from_=0, to=100, orient=tk.HORIZONTAL,
                                      command=lambda v: self._update_time_range_flexible(df, fig, plot_state, None, int(float(v)), range_var))
                end_slider.set(100)
                end_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
                
                plot_state['start_slider'] = start_slider
                plot_state['end_slider'] = end_slider
                
                # Now set the reset button command with access to the sliders
                reset_button.config(command=lambda: (start_slider.set(0), end_slider.set(100)))
                
                # Plot within time range
                self._plot_metadata_range_flexible(df, fig, time_min, time_max, available_metrics, plot_rows, plot_cols)
            else:
                # No time column - use frame counter
                ttk.Label(control_frame, text="Plotting by frame number (no time data available)").pack(side=tk.LEFT, padx=5)
                
                fig = Figure(figsize=(max(7, plot_cols * 4), max(5, plot_rows * 3)), dpi=80)
                
                # Plot all available metrics
                for idx, metric in enumerate(available_metrics, 1):
                    ax = fig.add_subplot(plot_rows, plot_cols, idx)
                    
                    # Filter out NaN values
                    valid_mask = df[metric].notna()
                    x_data = df[valid_mask].index + 1  # Frame numbers (1-indexed)
                    y_data = df[valid_mask][metric]
                    
                    ax.plot(x_data, y_data, 'o-', markersize=4, linewidth=1.5)
                    ax.set_xlabel('Frame Number')
                    ax.set_ylabel(metric)
                    ax.set_title(f'{metric} Evolution')
                    ax.grid(True, alpha=0.3)
                
                fig.tight_layout()
            
            # Canvas frame
            canvas_frame = ttk.Frame(plot_window)
            canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
            
            canvas = FigureCanvasTkAgg(fig, master=canvas_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
            if has_time:
                plot_state['canvas'] = canvas
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read metadata: {str(e)}")
    
    def _plot_metadata_range_flexible(self, df, fig, time_min, time_max, available_metrics, plot_rows, plot_cols):
        """Plot available metrics within a time range"""
        fig.clear()
        
        # Filter data by time range
        mask = (df['_time'] >= time_min) & (df['_time'] <= time_max)
        df_filtered = df[mask]
        
        if len(df_filtered) == 0:
            return
        
        x_data = df_filtered['_time']
        
        # Plot each available metric
        for idx, metric in enumerate(available_metrics, 1):
            ax = fig.add_subplot(plot_rows, plot_cols, idx)
            
            # Filter out NaN values
            valid_mask = df_filtered[metric].notna()
            y_data = df_filtered[valid_mask][metric]
            x_filtered = x_data[valid_mask]
            
            if len(y_data) > 0:
                ax.plot(x_filtered, y_data, 'o-', markersize=4, linewidth=1.5)
                ax.set_ylabel(metric)
                ax.set_title(f'{metric} Evolution')
                ax.grid(True, alpha=0.3)
                ax.xaxis.set_major_formatter(DateFormatter("%H:%M"))
                fig.autofmt_xdate()
        
        fig.tight_layout()
    
    def _update_time_range_flexible(self, df, fig, plot_state, start_pct, end_pct, range_var):
        """Update time range for flexible metric plotting"""
        time_min = plot_state['time_min']
        time_max = plot_state['time_max']
        time_range = (time_max - time_min).total_seconds()
        
        start_val = plot_state['start_slider'].get()
        end_val = plot_state['end_slider'].get()
        
        if start_val >= end_val:
            return
        
        display_min = time_min + pd.Timedelta(seconds=time_range * start_val / 100)
        display_max = time_min + pd.Timedelta(seconds=time_range * end_val / 100)
        
        range_var.set(f"{display_min.strftime('%H:%M')} - {display_max.strftime('%H:%M')}")
        
        self._plot_metadata_range_flexible(df, fig, display_min, display_max, 
                                          plot_state['available_metrics'], 
                                          plot_state['plot_rows'], 
                                          plot_state['plot_cols'])
        
        if plot_state['canvas']:
            plot_state['canvas'].draw()
    
    def _show_details_from_entry(self, entry):
        """Show details window for a given entry"""
        try:
            # Create details window
            details_win = tk.Toplevel(self.root)
            details_win.title(f"Details - {entry['target_name']}")
            details_win.geometry("800x650")
            
            # Create two frames for two-column layout
            left_frame = ttk.Frame(details_win, width=400)
            right_frame = ttk.Frame(details_win, width=400)
            
            left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
            right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Left column: Main info
            left_label = ttk.Label(left_frame, text="Main Info", font=("Arial", 12, "bold"))
            left_label.pack(anchor=tk.W)
            
            left_text = tk.Text(left_frame, height=20, width=40, wrap=tk.WORD)
            left_text.pack(fill=tk.BOTH, expand=True)
            
            # Format image types nicely
            image_types = entry.get('image_types', {})
            image_types_str = ""
            if isinstance(image_types, dict):
                for img_type, count in image_types.items():
                    image_types_str += f"{img_type}: {count}\n"
            else:
                image_types_str = str(image_types)
            
            left_content = f"""Target: {entry.get('target_name', 'N/A')}
Date: {entry.get('capture_date', 'N/A')}
Object: {entry.get('object', 'N/A')}
Telescope: {entry.get('telescope', 'N/A')}
Focal Length: {entry.get('focal_length', 'N/A')}

Total Files: {entry.get('total_files', 'N/A')}
LIGHT Frames: {entry.get('light_frames', 'N/A')}

Gain Range: {entry.get('gain_range', 'N/A')}
Offset Range: {entry.get('offset_range', 'N/A')}
Exptime Range: {entry.get('exptime_range', 'N/A')}

Image Types:
{image_types_str}
Filters: {entry.get('unique_filters', 'N/A')}
"""
            left_text.insert(tk.END, left_content)
            left_text.config(state=tk.DISABLED)
            
            # Right column: Filter details
            right_label = ttk.Label(right_frame, text="Filter Details", font=("Arial", 12, "bold"))
            right_label.pack(anchor=tk.W)
            
            right_text = tk.Text(right_frame, height=20, width=40, wrap=tk.WORD)
            right_text.pack(fill=tk.BOTH, expand=True)
            
            right_content = "Filter Name | Count | Gains | Offsets | Exptimes\n" + "-" * 50 + "\n"
            for filt in entry.get('filters', []):
                right_content += f"""{filt.get('name', 'Unknown')}
  Count: {filt.get('count', 0)}
  Gains: {filt.get('gains', 'N/A')}
  Offsets: {filt.get('offsets', 'N/A')}
  Exptimes: {filt.get('exptimes', 'N/A')}

"""
            right_text.insert(tk.END, right_content)
            right_text.config(state=tk.DISABLED)
            
            # Add button for ImageMetaData analysis if CSV exists
            folder_path = entry.get('folder_name', '')
            csv_path = os.path.join(folder_path, 'ImageMetaData.csv')
            if os.path.exists(csv_path):
                button_frame = ttk.Frame(details_win)
                button_frame.pack(fill=tk.X, padx=10, pady=5)
                ttk.Button(button_frame, text="Analyze ImageMetaData", 
                          command=lambda: self._read_image_metadata_from_path(csv_path)).pack()
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to show details: {str(e)}")


def main():
    root = tk.Tk()
    app = FITSGUIDatabaseApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
