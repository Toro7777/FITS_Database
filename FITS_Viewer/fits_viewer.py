"""Interactive FITS viewer with linear stretch preview, folder picker, and metadata panel."""

from __future__ import annotations

import argparse
from collections import OrderedDict
import math
from pathlib import Path
import re
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import NamedTuple
from datetime import datetime

import numpy as np
from astropy.io import fits
from PIL import Image, ImageTk

try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

FITS_EXTENSIONS = {".fits", ".fit", ".fts"}
_HFR_RE = re.compile(r"[-_](\d+\.\d+)\.(fits?|fts)$", re.IGNORECASE)
FILTERS = ["Luminosity", "Red", "Blue", "Green", "H-alpha", "O3", "S2"]


# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------

class FrameMetadata(NamedTuple):
    mean_adu: float | None
    ccd_temp: str
    dewpoint: str
    humidity: str
    ambtemp: str
    hfr: str
    filter_name: str
    obs_datetime: datetime | None


_EMPTY_META = FrameMetadata(None, "-", "-", "-", "-", "-", "-", None)


# ---------------------------------------------------------------------------
# FITS I/O helpers
# ---------------------------------------------------------------------------

def get_fits_files(folder: Path) -> list[Path]:
    files = [p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in FITS_EXTENSIONS]
    return sorted(files, key=lambda p: p.name.lower())


def normalize_to_2d(image: np.ndarray) -> np.ndarray:
    if image.ndim == 2:
        return image
    if image.ndim == 3:
        return np.nanmean(image, axis=0)
    if image.ndim > 3:
        out = image
        while out.ndim > 2:
            out = np.nanmean(out, axis=0)
        return out
    return image.reshape(1, -1)


def parse_hfr_from_filename(name: str) -> str:
    m = _HFR_RE.search(name)
    return m.group(1) if m else "-"


def _hv(header, key: str) -> str:
    """Return a formatted FITS header value or '-' if absent."""
    val = header.get(key, None)
    if val is None:
        return "-"
    try:
        return f"{float(val):.2f}"
    except (ValueError, TypeError):
        return str(val).strip() or "-"


def read_fits_frame(file_path: Path) -> tuple[np.ndarray, object]:
    """Read FITS file, return (2-D float32 array, primary header)."""
    with fits.open(file_path, memmap=False) as hdul:
        for hdu in hdul:
            data = getattr(hdu, "data", None)
            if data is not None:
                arr = normalize_to_2d(np.asarray(data, dtype=np.float32))
                return arr, hdu.header
    raise ValueError("No image data found in FITS")


def stretch_to_uint8(image_2d: np.ndarray, low_pct: float = 1.0, high_pct: float = 99.5) -> np.ndarray:
    """Linear stretch using a fast subsampled percentile estimate."""
    h = image_2d.shape[0]
    w = image_2d.shape[1] if image_2d.ndim > 1 else 1
    # Sample ~160k pixels max - far faster than the full 16 M pixel array
    step = max(1, min(h, w) // 400)
    sample = image_2d[::step, ::step].ravel()
    finite = sample[np.isfinite(sample)]
    if len(finite) == 0:
        return np.zeros_like(image_2d, dtype=np.uint8)
    low = float(np.percentile(finite, low_pct))
    high = float(np.percentile(finite, high_pct))
    if not (np.isfinite(low) and np.isfinite(high) and high > low):
        low, high = float(np.nanmin(finite)), float(np.nanmax(finite))
    if not (np.isfinite(low) and np.isfinite(high) and high > low):
        return np.zeros_like(image_2d, dtype=np.uint8)
    return np.clip((image_2d - low) / (high - low) * 255.0, 0, 255).astype(np.uint8)


def load_and_process(file_path: Path) -> tuple[np.ndarray, FrameMetadata]:
    """Load FITS, compute stretched uint8 frame + metadata in one pass."""
    arr, header = read_fits_frame(file_path)
    frame = stretch_to_uint8(arr)
    finite_vals = arr[np.isfinite(arr)]
    mean_adu = float(np.mean(finite_vals)) if len(finite_vals) > 0 else None
    
    # Extract filter name
    filter_name = _hv(header, "FILTER")
    if filter_name == "-":
        filter_name = _hv(header, "FILTNAME")
    if filter_name == "-":
        filter_name = "Luminosity"
    
    # Extract observation date/time
    obs_datetime = None
    date_obs = header.get("DATE-OBS", None)
    if date_obs:
        try:
            obs_datetime = datetime.fromisoformat(str(date_obs).replace("Z", "+00:00"))
        except (ValueError, TypeError):
            pass
    
    meta = FrameMetadata(
        mean_adu=mean_adu,
        ccd_temp=_hv(header, "CCD-TEMP"),
        dewpoint=_hv(header, "DEWPOINT"),
        humidity=_hv(header, "HUMIDITY"),
        ambtemp=_hv(header, "AMBTEMP"),
        hfr=parse_hfr_from_filename(file_path.name),
        filter_name=filter_name,
        obs_datetime=obs_datetime,
    )
    return frame, meta


def extract_metadata_only(file_path: Path) -> FrameMetadata:
    """Extract only metadata from FITS file (fast, no image processing)."""
    with fits.open(file_path, memmap=False) as hdul:
        for hdu in hdul:
            data = getattr(hdu, "data", None)
            if data is not None:
                arr = normalize_to_2d(np.asarray(data, dtype=np.float32))
                header = hdu.header
                break
    
    finite_vals = arr[np.isfinite(arr)]
    mean_adu = float(np.mean(finite_vals)) if len(finite_vals) > 0 else None
    
    # Extract filter name
    filter_name = _hv(header, "FILTER")
    if filter_name == "-":
        filter_name = _hv(header, "FILTNAME")
    if filter_name == "-":
        filter_name = "Luminosity"
    
    # Extract observation date/time
    obs_datetime = None
    date_obs = header.get("DATE-OBS", None)
    if date_obs:
        try:
            obs_datetime = datetime.fromisoformat(str(date_obs).replace("Z", "+00:00"))
        except (ValueError, TypeError):
            pass
    
    return FrameMetadata(
        mean_adu=mean_adu,
        ccd_temp=_hv(header, "CCD-TEMP"),
        dewpoint=_hv(header, "DEWPOINT"),
        humidity=_hv(header, "HUMIDITY"),
        ambtemp=_hv(header, "AMBTEMP"),
        hfr=parse_hfr_from_filename(file_path.name),
        filter_name=filter_name,
        obs_datetime=obs_datetime,
    )


# ---------------------------------------------------------------------------
# Thread-safe LRU cache with background preloader
# ---------------------------------------------------------------------------

class FitsCache:
    """Loads FITS frames on demand and preloads the rest in a background thread."""

    def __init__(self, max_size: int = 20) -> None:
        self._max = max_size
        self._frames: OrderedDict[Path, np.ndarray] = OrderedDict()
        self._metas: dict[Path, FrameMetadata] = {}
        self._lock = threading.Lock()
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None

    def _store(self, path: Path, frame: np.ndarray, meta: FrameMetadata) -> None:
        """Must be called with _lock held."""
        self._frames[path] = frame
        self._metas[path] = meta
        self._frames.move_to_end(path)
        while len(self._frames) > self._max:
            evicted = next(iter(self._frames))
            del self._frames[evicted]
            self._metas.pop(evicted, None)

    def get(self, path: Path) -> tuple[np.ndarray, FrameMetadata]:
        with self._lock:
            if path in self._frames:
                self._frames.move_to_end(path)
                return self._frames[path], self._metas[path]
        # Not cached - load synchronously (happens for first frame only)
        frame, meta = load_and_process(path)
        with self._lock:
            self._store(path, frame, meta)
        return frame, meta

    def contains(self, path: Path) -> bool:
        with self._lock:
            return path in self._frames

    def rename(self, old: Path, new: Path) -> None:
        with self._lock:
            if old in self._frames:
                frame = self._frames.pop(old)
                meta = self._metas.pop(old, None)
                self._frames[new] = frame
                if meta is not None:
                    self._metas[new] = meta
                self._frames.move_to_end(new)

    def start_preload(self, files: list[Path]) -> None:
        """Spawn/restart background thread that fills the cache for all files."""
        self._stop.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=0.3)
        self._stop.clear()
        self._thread = threading.Thread(
            target=self._worker, args=(list(files),), daemon=True
        )
        self._thread.start()

    def _worker(self, files: list[Path]) -> None:
        for path in files:
            if self._stop.is_set():
                return
            if not self.contains(path):
                try:
                    frame, meta = load_and_process(path)
                    with self._lock:
                        self._store(path, frame, meta)
                except Exception:
                    pass

    def clear(self) -> None:
        self._stop.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=0.3)
        with self._lock:
            self._frames.clear()
            self._metas.clear()
        self._stop.clear()


# ---------------------------------------------------------------------------
# Main application
# ---------------------------------------------------------------------------

class FitsViewerApp:
    def __init__(self, folder: Path | None = None, fps_default: float = 2.0):
        self.folder: Path | None = None
        self.files: list[Path] = []
        self.cache = FitsCache(max_size=20)
        self.metadata_cache: dict[Path, FrameMetadata] = {}
        self.index = 0
        self.playing = False
        self.tk_image: ImageTk.PhotoImage | None = None
        self.window_size = (900, 700)
        self.after_id: str | None = None

        self.root = tk.Tk()
        self.root.title("FITS Viewer")
        self.root.geometry("1460x920")
        self.root.minsize(1050, 740)

        self.style = ttk.Style(self.root)
        try:
            self.style.theme_use("clam")
        except tk.TclError:
            pass

        self.style.configure("Top.TFrame",     background="#1e2430")
        self.style.configure("Main.TFrame",    background="#11161f")
        self.style.configure("Side.TFrame",    background="#1a2132")
        self.style.configure("Info.TLabel",    background="#1e2430", foreground="#d8e1f0")
        self.style.configure("Title.TLabel",   background="#1e2430", foreground="#e9f1ff",
                             font=("Segoe UI", 11, "bold"))
        self.style.configure("MetaTitle.TLabel", background="#1a2132", foreground="#aac4ff",
                             font=("Segoe UI", 10, "bold"))
        self.style.configure("MetaKey.TLabel", background="#1a2132", foreground="#7a90b0",
                             font=("Segoe UI", 9))
        self.style.configure("MetaVal.TLabel", background="#1a2132", foreground="#ffffff",
                             font=("Segoe UI", 11, "bold"))
        self.style.configure("BAD.TLabel",     background="#1a2132", foreground="#ff5555",
                             font=("Segoe UI", 13, "bold"))
        self.style.configure("OK.TLabel",      background="#1a2132", foreground="#55cc55",
                             font=("Segoe UI", 13, "bold"))
        self.style.configure("Hint.TLabel",    background="#1a2132", foreground="#556080",
                             font=("Segoe UI", 8))

        self._build_ui(fps_default)
        self._bind_keys()
        self._render_placeholder("Choose a folder to start viewing FITS files")
        self._schedule_next_tick()
        if folder is not None:
            self.load_folder(folder)

    def _build_ui(self, fps_default: float) -> None:
        self.root.rowconfigure(1, weight=1)
        self.root.columnconfigure(0, weight=1)

        # Top bar
        top = ttk.Frame(self.root, style="Top.TFrame", padding=(12, 10))
        top.grid(row=0, column=0, sticky="ew")
        top.columnconfigure(1, weight=1)
        top.columnconfigure(2, weight=1)

        ttk.Label(top, text="FITS Viewer", style="Title.TLabel").grid(
            row=0, column=0, sticky="w", padx=(0, 14))
        self.folder_var = tk.StringVar(value="No folder selected")
        ttk.Label(top, textvariable=self.folder_var, style="Info.TLabel").grid(
            row=0, column=1, sticky="ew")
        self.filename_var = tk.StringVar(value="")
        ttk.Label(top, textvariable=self.filename_var, style="Info.TLabel").grid(
            row=0, column=2, sticky="ew", padx=(12, 12))
        ttk.Button(top, text="Choose Folder", command=self.choose_folder).grid(
            row=0, column=3, padx=(12, 6))
        ttk.Button(top, text="Reload", command=self.reload_folder).grid(row=0, column=4, padx=(0, 12))
        
        self.filter_bad_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(top, text="Hide BAD", variable=self.filter_bad_var,
                       command=self._on_filter_changed).grid(row=0, column=5, padx=(8, 0))
        
        self.show_bad_only_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(top, text="Show BAD Only", variable=self.show_bad_only_var,
                       command=self._on_filter_changed).grid(row=0, column=6, padx=(8, 0))

        # Main area
        main = ttk.Frame(self.root, style="Main.TFrame", padding=(6, 6))
        main.grid(row=1, column=0, sticky="nsew")
        main.rowconfigure(0, weight=1)
        main.columnconfigure(0, weight=1)
        main.columnconfigure(1, minsize=240, weight=0)

        # Image canvas (left)
        self.image_label = tk.Label(main, bg="#040608", fg="#d8e1f0")
        self.image_label.grid(row=0, column=0, sticky="nsew", padx=(4, 6), pady=4)
        self.image_label.bind("<Configure>", self._on_image_area_resize)

        # Right metadata panel
        side = ttk.Frame(main, style="Side.TFrame", padding=(14, 16))
        side.grid(row=0, column=1, sticky="nsew", padx=(0, 4), pady=4)
        side.columnconfigure(0, weight=1)

        ttk.Label(side, text="Frame Info", style="MetaTitle.TLabel").grid(
            row=0, column=0, sticky="w", pady=(0, 8))

        self._bad_status_var = tk.StringVar(value="")
        self._bad_lbl = ttk.Label(side, textvariable=self._bad_status_var, style="OK.TLabel")
        self._bad_lbl.grid(row=1, column=0, sticky="w", pady=(0, 8))

        ttk.Separator(side, orient="horizontal").grid(row=2, column=0, sticky="ew", pady=(0, 12))

        # metadata field definitions: (display label, internal attr suffix)
        meta_fields = [
            ("Filter",   "_meta_filter"),
            ("HFR",      "_meta_hfr"),
            ("Mean ADU", "_meta_adu"),
            ("CCD Temp", "_meta_ccdtemp"),
            ("Dewpoint", "_meta_dew"),
            ("Humidity", "_meta_hum"),
            ("Amb Temp", "_meta_amb"),
        ]
        for i, (label, attr) in enumerate(meta_fields):
            base_row = 3 + i * 3
            ttk.Label(side, text=label, style="MetaKey.TLabel").grid(
                row=base_row, column=0, sticky="w", pady=(6, 0))
            var = tk.StringVar(value="-")
            setattr(self, attr + "_var", var)
            ttk.Label(side, textvariable=var, style="MetaVal.TLabel").grid(
                row=base_row + 1, column=0, sticky="w")
            ttk.Separator(side, orient="horizontal").grid(
                row=base_row + 2, column=0, sticky="ew", pady=(6, 0))

        # Compare Frame button
        compare_row = 3 + len(meta_fields) * 3 + 1
        ttk.Button(side, text="Compare Frame", command=self._open_compare_plot).grid(
            row=compare_row, column=0, sticky="ew", pady=(8, 12))

        hint_row = compare_row + 2
        hint = (
            "B            Toggle BAD\n"
            "Space      Next Picture\n"
            "P            Play / Pause\n"
            "<  /  >    Prev / Next"
        )
        ttk.Label(side, text=hint, style="Hint.TLabel", justify="left").grid(
            row=hint_row, column=0, sticky="sw", pady=(18, 0))
        side.rowconfigure(hint_row, weight=1)

        # Controls bar
        controls = ttk.Frame(main, padding=(4, 8, 4, 2))
        controls.grid(row=1, column=0, columnspan=2, sticky="ew")
        controls.columnconfigure(7, weight=1)

        self.play_pause_btn = ttk.Button(controls, text="Play", width=10,
                                         command=self.toggle_play_pause)
        self.play_pause_btn.grid(row=0, column=0, padx=4)

        self.prev_btn = ttk.Button(controls, text="<< Prev", width=10, command=self.prev_frame)
        self.prev_btn.grid(row=0, column=1, padx=4)

        self.next_btn = ttk.Button(controls, text="Next >>", width=10, command=self.next_frame)
        self.next_btn.grid(row=0, column=2, padx=4)

        self.bad_btn = ttk.Button(controls, text="Toggle BAD", width=12,
                                  command=self.toggle_bad_status)
        self.bad_btn.grid(row=0, column=3, padx=4)

        ttk.Label(controls, text="Speed (fps)").grid(row=0, column=4, padx=(12, 4))
        self.speed_var = tk.DoubleVar(value=fps_default)
        ttk.Scale(controls, from_=0.5, to=10.0, orient=tk.HORIZONTAL,
                  variable=self.speed_var, length=200).grid(row=0, column=5, padx=4)

        self.speed_value_var = tk.StringVar(value=f"{fps_default:.1f} fps")
        ttk.Label(controls, textvariable=self.speed_value_var).grid(row=0, column=6, padx=(0, 8))
        self.speed_var.trace_add("write", self._on_speed_changed)

        self.status_var = tk.StringVar(value="")
        ttk.Label(controls, textvariable=self.status_var, anchor="w").grid(
            row=0, column=7, sticky="ew", padx=8)

        # Main trim bar: keep selected range, cut (mark BAD) outside it.
        trim_controls = ttk.Frame(controls)
        trim_controls.grid(row=1, column=0, columnspan=8, sticky="ew", pady=(8, 0))
        trim_controls.columnconfigure(2, weight=1)
        trim_controls.columnconfigure(5, weight=1)

        ttk.Label(trim_controls, text="Trim Range").grid(row=0, column=0, sticky="w", padx=(0, 10))

        self.main_trim_start_var = tk.IntVar(value=1)
        self.main_trim_end_var = tk.IntVar(value=1)
        self.main_trim_start_text = tk.StringVar(value="1")
        self.main_trim_end_text = tk.StringVar(value="1")

        ttk.Label(trim_controls, text="Start").grid(row=0, column=1, sticky="w")
        self.main_trim_start_scale = ttk.Scale(
            trim_controls,
            from_=1,
            to=1,
            orient=tk.HORIZONTAL,
            variable=self.main_trim_start_var,
            length=220,
            command=lambda _v: self._sync_main_trim_labels(),
        )
        self.main_trim_start_scale.grid(row=0, column=2, sticky="ew", padx=(6, 6))
        ttk.Label(trim_controls, textvariable=self.main_trim_start_text, width=4).grid(row=0, column=3, sticky="w")

        ttk.Label(trim_controls, text="End").grid(row=0, column=4, sticky="w", padx=(12, 0))
        self.main_trim_end_scale = ttk.Scale(
            trim_controls,
            from_=1,
            to=1,
            orient=tk.HORIZONTAL,
            variable=self.main_trim_end_var,
            length=220,
            command=lambda _v: self._sync_main_trim_labels(),
        )
        self.main_trim_end_scale.grid(row=0, column=5, sticky="ew", padx=(6, 6))
        ttk.Label(trim_controls, textvariable=self.main_trim_end_text, width=4).grid(row=0, column=6, sticky="w")

        self.main_trim_btn = ttk.Button(trim_controls, text="Cut Outside Range", command=self._apply_main_trim_cut)
        self.main_trim_btn.grid(row=0, column=7, sticky="e", padx=(12, 0))

        self.file_var = tk.StringVar(value="")
        ttk.Label(main, textvariable=self.file_var, anchor="w", style="MetaKey.TLabel").grid(
            row=2, column=0, columnspan=2, sticky="ew", padx=6, pady=(2, 6))

        self._update_control_states()

    def _bind_keys(self) -> None:
        self.root.bind("<space>", lambda _e: self.next_frame())
        self.root.bind("b",       lambda _e: self.toggle_bad_status())
        self.root.bind("B",       lambda _e: self.toggle_bad_status())
        self.root.bind("p",       lambda _e: self.toggle_play_pause())
        self.root.bind("P",       lambda _e: self.toggle_play_pause())
        self.root.bind("<Left>",  lambda _e: self.prev_frame())
        self.root.bind("<Right>", lambda _e: self.next_frame())

    def _on_image_area_resize(self, event: tk.Event) -> None:
        self.window_size = (max(100, event.width), max(100, event.height))
        if self.files:
            self._render_current_frame(prefetch=False)
        else:
            self._render_placeholder("Choose a folder to start viewing FITS files")

    def _current_file(self) -> Path:
        return self.files[self.index]

    def _on_speed_changed(self, *_args: object) -> None:
        self.speed_value_var.set(f"{max(0.5, float(self.speed_var.get())):.1f} fps")

    def _sync_main_trim_labels(self) -> None:
        start_val = int(round(self.main_trim_start_var.get()))
        end_val = int(round(self.main_trim_end_var.get()))
        self.main_trim_start_text.set(str(start_val))
        self.main_trim_end_text.set(str(end_val))

    def _apply_main_trim_cut(self) -> None:
        if not self.files:
            return

        start_idx = int(round(self.main_trim_start_var.get()))
        end_idx = int(round(self.main_trim_end_var.get()))
        if start_idx > end_idx:
            start_idx, end_idx = end_idx, start_idx

        cut_count = 0
        for i, file_path in enumerate(list(self.files), start=1):
            if i < start_idx or i > end_idx:
                if file_path.name.upper().startswith("BAD_"):
                    continue
                target = file_path.with_name(f"BAD_{file_path.name}")
                if target.exists():
                    continue
                try:
                    file_path.rename(target)
                    self.cache.rename(file_path, target)
                    if file_path in self.metadata_cache:
                        self.metadata_cache[target] = self.metadata_cache.pop(file_path)
                    self.files[i - 1] = target
                    cut_count += 1
                except Exception:
                    pass

        self._render_current_frame()
        self._update_control_states()
        messagebox.showinfo(
            "Trim Applied",
            f"Kept frames {start_idx}..{end_idx}. Marked {cut_count} outside frames as BAD.",
        )

    def _get_visible_files(self) -> list[Path]:
        """Return list of files to display (optionally filtering BAD)."""
        if self.show_bad_only_var.get():
            return [f for f in self.files if f.name.upper().startswith("BAD_")]
        elif self.filter_bad_var.get():
            return [f for f in self.files if not f.name.upper().startswith("BAD_")]
        else:
            return self.files

    def _on_filter_changed(self) -> None:
        """Handle when Hide BAD checkbox is toggled."""
        if not self.files:
            return
        visible = self._get_visible_files()
        if visible:
            self.index = self.files.index(visible[0])
            self._render_current_frame()
        else:
            self._render_placeholder("No frames match current filter")
        self._update_control_states()

    def _render_placeholder(self, text: str) -> None:
        self.image_label.configure(image="", text=text, font=("Segoe UI", 14), anchor="center")
        self.status_var.set("No folder loaded")
        self.file_var.set("")
        self.filename_var.set("")
        self._update_meta_panel(None, _EMPTY_META)

    def _update_meta_panel(self, file_path: Path | None, meta: FrameMetadata) -> None:
        if file_path is not None:
            is_bad = file_path.name.upper().startswith("BAD_")
            self._bad_status_var.set("BAD" if is_bad else "OK")
            self._bad_lbl.configure(style="BAD.TLabel" if is_bad else "OK.TLabel")
        else:
            self._bad_status_var.set("")
        self._meta_filter_var.set(meta.filter_name if meta.filter_name != "-" else "Luminosity")
        self._meta_hfr_var.set(meta.hfr)
        self._meta_adu_var.set(f"{meta.mean_adu:,.1f}" if meta.mean_adu is not None else "-")
        self._meta_ccdtemp_var.set(f"{meta.ccd_temp} C" if meta.ccd_temp != "-" else "-")
        self._meta_dew_var.set(f"{meta.dewpoint} C" if meta.dewpoint != "-" else "-")
        self._meta_hum_var.set(f"{meta.humidity} %" if meta.humidity != "-" else "-")
        self._meta_amb_var.set(f"{meta.ambtemp} C" if meta.ambtemp != "-" else "-")

    def _render_current_frame(self, prefetch: bool = True) -> None:
        if not self.files:
            self._render_placeholder("Choose a folder to start viewing FITS files")
            return

        visible = self._get_visible_files()
        if not visible:
            self._render_placeholder("No frames match current filter")
            self._update_control_states()
            return
        if self.files[self.index] not in visible:
            self.index = self.files.index(visible[0])

        current_file = self._current_file()
        try:
            frame, meta = self.cache.get(current_file)
        except Exception as exc:
            self._render_placeholder(f"Failed to load: {current_file.name}\n{exc}")
            return

        img = Image.fromarray(frame, mode="L")
        area_w, area_h = self.window_size
        scale = min(area_w / img.width, area_h / img.height)
        new_w = max(1, int(math.floor(img.width * scale)))
        new_h = max(1, int(math.floor(img.height * scale)))
        resized = img.resize((new_w, new_h), Image.Resampling.BILINEAR)
        self.tk_image = ImageTk.PhotoImage(resized)
        self.image_label.configure(image=self.tk_image, text="")

        is_bad = current_file.name.upper().startswith("BAD_")
        state = "| PLAY" if self.playing else "> PAUSE"
        bad_tag = "BAD" if is_bad else "OK"
        self.status_var.set(f"{self.index + 1} / {len(self.files)}  -  {bad_tag}  -  {state}")
        self.file_var.set(str(current_file))
        self.filename_var.set(current_file.name)
        self._update_meta_panel(current_file, meta)

        if prefetch:
            self._prefetch_neighbors()

    def _prefetch_neighbors(self) -> None:
        if not self.files:
            return
        total = len(self.files)
        for offset in (1, -1, 2):
            path = self.files[(self.index + offset) % total]
            if not self.cache.contains(path):
                self.root.after_idle(lambda p=path: self._bg_prefetch(p))

    def _bg_prefetch(self, path: Path) -> None:
        try:
            self.cache.get(path)
        except Exception:
            pass

    def _update_control_states(self) -> None:
        has_data = bool(self.files)
        has_visible = bool(self._get_visible_files()) if has_data else False
        self.play_pause_btn.config(state=tk.NORMAL if has_visible else tk.DISABLED)
        self.bad_btn.config(state=tk.NORMAL if has_visible else tk.DISABLED)
        self.main_trim_btn.config(state=tk.NORMAL if has_data else tk.DISABLED)
        if not has_data:
            self.play_pause_btn.config(text="Play")
            self.prev_btn.config(state=tk.DISABLED)
            self.next_btn.config(state=tk.DISABLED)
            return
        if not has_visible:
            self.play_pause_btn.config(text="Play")
            self.prev_btn.config(state=tk.DISABLED)
            self.next_btn.config(state=tk.DISABLED)
            return
        if self.playing:
            self.play_pause_btn.config(text="Pause")
            self.prev_btn.config(state=tk.DISABLED)
            self.next_btn.config(state=tk.DISABLED)
        else:
            self.play_pause_btn.config(text="Play")
            self.prev_btn.config(state=tk.NORMAL)
            self.next_btn.config(state=tk.NORMAL)

    def _schedule_next_tick(self) -> None:
        fps = max(0.1, float(self.speed_var.get()))
        self.after_id = self.root.after(int(1000.0 / fps), self._tick)

    def _tick(self) -> None:
        if self.playing and self.files:
            visible = self._get_visible_files()
            if visible:
                current = self.files[self.index]
                idx_in_visible = visible.index(current) if current in visible else 0
                next_visible = visible[(idx_in_visible + 1) % len(visible)]
                self.index = self.files.index(next_visible)
            else:
                self.index = (self.index + 1) % len(self.files)
            self._render_current_frame()
        self._schedule_next_tick()

    def choose_folder(self) -> None:
        selected = filedialog.askdirectory(title="Choose FITS Folder")
        if selected:
            self.load_folder(Path(selected))

    def reload_folder(self) -> None:
        if self.folder is None:
            self.choose_folder()
        else:
            self.load_folder(self.folder)

    def load_folder(self, folder: Path) -> None:
        if not folder.exists() or not folder.is_dir():
            messagebox.showerror("FITS Viewer", f"Folder not found:\n{folder}")
            return

        files = get_fits_files(folder)
        if not files:
            messagebox.showwarning("FITS Viewer", f"No FITS files found in:\n{folder}")
            self.folder = folder
            self.files = []
            self.cache.clear()
            self.metadata_cache.clear()
            self.playing = False
            self.main_trim_start_var.set(1)
            self.main_trim_end_var.set(1)
            self.main_trim_start_scale.configure(from_=1, to=1)
            self.main_trim_end_scale.configure(from_=1, to=1)
            self._sync_main_trim_labels()
            self.folder_var.set(str(folder))
            self._update_control_states()
            self._render_placeholder("No FITS files found in selected folder")
            return

        self.cache.clear()
        self.metadata_cache.clear()
        self.folder = folder
        self.folder_var.set(str(folder))
        self.files = files
        self.index = 0
        self.playing = False
        total = len(files)
        self.main_trim_start_var.set(1)
        self.main_trim_end_var.set(total)
        self.main_trim_start_scale.configure(from_=1, to=total)
        self.main_trim_end_scale.configure(from_=1, to=total)
        self._sync_main_trim_labels()
        self._update_control_states()
        # Show first frame immediately (synchronous), then background-load the rest
        self._render_current_frame()
        self.cache.start_preload(files)
        # Start metadata preload in background
        threading.Thread(target=self._preload_metadata, daemon=True).start()

    def _preload_metadata(self) -> None:
        """Background thread: preload metadata for all files."""
        for i, file_path in enumerate(self.files):
            try:
                if file_path not in self.metadata_cache:
                    meta = extract_metadata_only(file_path)
                    self.metadata_cache[file_path] = meta
                # Update status bar with progress
                progress = f"Loading metadata... {i + 1}/{len(self.files)}"
                self.root.after(0, lambda p=progress: self.status_var.set(p))
            except Exception:
                pass

    def toggle_play_pause(self) -> None:
        if not self.files:
            return
        self.playing = not self.playing
        self._update_control_states()
        self._render_current_frame()

    def next_frame(self) -> None:
        if self.playing or not self.files:
            return
        visible = self._get_visible_files()
        if not visible:
            return
        current = self.files[self.index]
        idx_in_visible = visible.index(current) if current in visible else len(visible) - 1
        next_visible = visible[(idx_in_visible + 1) % len(visible)]
        self.index = self.files.index(next_visible)
        self._render_current_frame()

    def prev_frame(self) -> None:
        if self.playing or not self.files:
            return
        visible = self._get_visible_files()
        if not visible:
            return
        current = self.files[self.index]
        idx_in_visible = visible.index(current) if current in visible else 0
        prev_visible = visible[(idx_in_visible - 1) % len(visible)]
        self.index = self.files.index(prev_visible)
        self._render_current_frame()

    def _open_compare_plot(self) -> None:
        """Open a comparison plot of mean ADU and HFR vs time."""
        if not MATPLOTLIB_AVAILABLE:
            messagebox.showerror("Compare Frame", "Matplotlib is not installed.\nInstall with: pip install matplotlib")
            return
        
        if not self.files:
            messagebox.showwarning("Compare Frame", "No files loaded")
            return
        
        # Pause playback
        self.playing = False
        self._update_control_states()
        
        # Use cached metadata (or extract if missing)
        data = []
        for file_path in self.files:
            try:
                if file_path in self.metadata_cache:
                    meta = self.metadata_cache[file_path]
                else:
                    meta = extract_metadata_only(file_path)
                    self.metadata_cache[file_path] = meta
                
                is_bad = file_path.name.upper().startswith("BAD_")
                if meta.mean_adu is not None:
                    hfr_val = float(meta.hfr) if meta.hfr != "-" else 0.0
                    data.append({
                        'path': file_path,
                        'time': meta.obs_datetime,
                        'mean_adu': meta.mean_adu,
                        'hfr': hfr_val,
                        'is_bad': is_bad,
                    })
            except Exception:
                pass
        
        if not data:
            messagebox.showwarning("Compare Frame", "No valid frame data to compare")
            return
        
        # Keep data in viewer order so plot index matches frame index in the UI.
        self._plot_data = data
        
        # Create plot window
        plot_window = tk.Toplevel(self.root)
        plot_window.title("Frame Comparison")
        plot_window.geometry("1000x700")
        
        # Create matplotlib figure
        fig = Figure(figsize=(10, 7), dpi=100)
        ax1 = fig.add_subplot(111)
        ax2 = ax1.twinx()
        self._current_plot_ax1 = ax1
        self._current_plot_ax2 = ax2
        
        # Prepare data
        indices = list(range(1, len(data) + 1))
        mean_adus = [d['mean_adu'] for d in data]
        hfrs = [d['hfr'] for d in data]
        point_colors = ['red' if d['is_bad'] else 'blue' for d in data]
        
        # Plot lines
        ax1.plot(indices, mean_adus, 'b-', alpha=0.6, linewidth=2, label='Mean ADU')
        ax2.plot(indices, hfrs, 'g-', alpha=0.6, linewidth=2, label='HFR')
        
        # Plot points with dynamic colors: BAD=red, OK=blue.
        points = ax1.scatter(indices, mean_adus, c=point_colors, s=70, alpha=0.75, zorder=5)
        hover_marker = ax1.scatter(
            [],
            [],
            s=180,
            facecolors='none',
            edgecolors='yellow',
            linewidths=1.8,
            zorder=6,
            visible=False,
        )
        
        ax1.set_xlabel('Frame Index (same as viewer)')
        ax1.set_ylabel('Mean ADU', color='b')
        ax2.set_ylabel('HFR', color='g')
        ax1.tick_params(axis='y', labelcolor='b')
        ax2.tick_params(axis='y', labelcolor='g')
        ax1.grid(True, alpha=0.3)
        
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, master=plot_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Handle events:
        # - single-click: navigate to frame
        # - double-click: toggle BAD and recolor point
        def on_pick(event):
            if hasattr(event, 'xdata') and event.xdata is not None:
                idx = int(round(event.xdata)) - 1
                if 0 <= idx < len(data):
                    file_path = data[idx]['path']

                    # Double-click toggles BAD status on the selected frame.
                    if event.dblclick:
                        is_bad = file_path.name.upper().startswith("BAD_")
                        if is_bad:
                            target_name = file_path.name[4:]
                            if not target_name:
                                return
                            target = file_path.with_name(target_name)
                        else:
                            target = file_path.with_name(f"BAD_{file_path.name}")

                        if target.exists():
                            return

                        try:
                            file_path.rename(target)
                            self.cache.rename(file_path, target)
                            if file_path in self.metadata_cache:
                                self.metadata_cache[target] = self.metadata_cache.pop(file_path)

                            file_idx = self.files.index(file_path)
                            self.files[file_idx] = target

                            data[idx]['path'] = target
                            data[idx]['is_bad'] = not is_bad

                            # Recolor points after BAD toggle.
                            updated_colors = ['red' if d['is_bad'] else 'blue' for d in data]
                            points.set_color(updated_colors)
                            canvas.draw_idle()

                            if self.index == file_idx:
                                self._render_current_frame()
                        except Exception as e:
                            messagebox.showerror("Toggle BAD", f"Failed: {e}")
                        return

                    # Single-click navigates to frame in the main viewer.
                    self.index = self.files.index(file_path)
                    self._render_current_frame()
        
        canvas.mpl_connect('button_press_event', on_pick)
        
        # Add controls frame
        controls_frame = ttk.Frame(plot_window)
        controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(controls_frame, text="Click: navigate | Double-click: toggle BAD").pack(side=tk.LEFT)
        ttk.Label(controls_frame, text="HFR Threshold:").pack(side=tk.LEFT, padx=(10, 0))
        
        hfr_threshold_var = tk.DoubleVar(value=2.0)
        ttk.Scale(controls_frame, from_=0.5, to=10.0, orient=tk.HORIZONTAL,
                  variable=hfr_threshold_var, length=150).pack(side=tk.LEFT, padx=5)
        
        hfr_value_label = ttk.Label(controls_frame, text="2.0")
        hfr_value_label.pack(side=tk.LEFT)
        
        def update_hfr_label(*args):
            hfr_value_label.config(text=f"{hfr_threshold_var.get():.2f}")
        hfr_threshold_var.trace_add("write", update_hfr_label)
        
        def apply_hfr_threshold():
            threshold = hfr_threshold_var.get()
            marked = 0
            for d in data:
                if d['hfr'] > threshold and not d['is_bad']:
                    file_path = d['path']
                    try:
                        target = file_path.with_name(f"BAD_{file_path.name}")
                        if not target.exists():
                            file_path.rename(target)
                            self.cache.rename(file_path, target)
                            if file_path in self.metadata_cache:
                                self.metadata_cache[target] = self.metadata_cache.pop(file_path)
                            self.files[self.files.index(file_path)] = target
                            d['path'] = target
                            d['is_bad'] = True
                            marked += 1
                    except Exception:
                        pass
            updated_colors = ['red' if d['is_bad'] else 'blue' for d in data]
            points.set_color(updated_colors)
            canvas.draw_idle()
            messagebox.showinfo("HFR Toggle", f"Marked {marked} frames with HFR > {threshold:.2f} as BAD")
            self._render_current_frame()
        
        ttk.Button(controls_frame, text="Mark by HFR", command=apply_hfr_threshold).pack(side=tk.LEFT, padx=10)
        
        # X-axis zoom controls
        ttk.Label(controls_frame, text="X-Axis Zoom:").pack(side=tk.LEFT, padx=(20, 0))
        x_min_var = tk.IntVar(value=1)
        x_max_var = tk.IntVar(value=len(data))
        
        ttk.Label(controls_frame, text="From:").pack(side=tk.LEFT, padx=(10, 0))
        ttk.Spinbox(controls_frame, from_=1, to=len(data), textvariable=x_min_var, width=5).pack(side=tk.LEFT, padx=2)
        
        ttk.Label(controls_frame, text="To:").pack(side=tk.LEFT, padx=(10, 0))
        ttk.Spinbox(controls_frame, from_=1, to=len(data), textvariable=x_max_var, width=5).pack(side=tk.LEFT, padx=2)
        
        def apply_zoom():
            x_min = x_min_var.get()
            x_max = x_max_var.get()
            if x_min < x_max and x_min >= 1 and x_max <= len(data):
                ax1.set_xlim(x_min - 0.5, x_max + 0.5)
                canvas.draw()
        
        ttk.Button(controls_frame, text="Zoom", command=apply_zoom).pack(side=tk.LEFT, padx=5)

        # Hover feedback: show frame filename and interaction reminder below graph.
        hover_frame = ttk.Frame(plot_window)
        hover_frame.pack(fill=tk.X, padx=8, pady=(0, 6))
        hover_text_var = tk.StringVar(value="Hover a point to see filename. Click: navigate | Double-click: toggle BAD")
        ttk.Label(hover_frame, textvariable=hover_text_var, anchor="w").pack(fill=tk.X)

        def on_hover(event):
            if event.xdata is None or event.inaxes not in (ax1, ax2):
                hover_text_var.set("Hover a point to see filename. Click: navigate | Double-click: toggle BAD")
                hover_marker.set_visible(False)
                canvas.draw_idle()
                return
            idx = int(round(event.xdata)) - 1
            if 0 <= idx < len(data):
                hover_text_var.set(
                    f"Frame {idx + 1}/{len(data)}: {data[idx]['path'].name} | Click: navigate | Double-click: toggle BAD"
                )
                hover_marker.set_offsets([[indices[idx], mean_adus[idx]]])
                hover_marker.set_visible(True)
                canvas.draw_idle()
            else:
                hover_text_var.set("Hover a point to see filename. Click: navigate | Double-click: toggle BAD")
                hover_marker.set_visible(False)
                canvas.draw_idle()

        canvas.mpl_connect('motion_notify_event', on_hover)

        # Trim controls: keep only a selected central range and mark outside as BAD.
        trim_frame = ttk.Frame(plot_window)
        trim_frame.pack(fill=tk.X, padx=8, pady=(0, 8))

        ttk.Label(trim_frame, text="Trim Range (keep inside):").grid(row=0, column=0, sticky="w", padx=(0, 10))

        trim_start_var = tk.IntVar(value=1)
        trim_end_var = tk.IntVar(value=len(data))
        trim_start_text = tk.StringVar(value="1")
        trim_end_text = tk.StringVar(value=str(len(data)))

        ttk.Label(trim_frame, text="Start").grid(row=0, column=1, sticky="w")
        start_scale = ttk.Scale(
            trim_frame,
            from_=1,
            to=len(data),
            orient=tk.HORIZONTAL,
            variable=trim_start_var,
            length=220,
        )
        start_scale.grid(row=0, column=2, sticky="ew", padx=(6, 6))
        ttk.Label(trim_frame, textvariable=trim_start_text, width=4).grid(row=0, column=3, sticky="w")

        ttk.Label(trim_frame, text="End").grid(row=0, column=4, sticky="w", padx=(12, 0))
        end_scale = ttk.Scale(
            trim_frame,
            from_=1,
            to=len(data),
            orient=tk.HORIZONTAL,
            variable=trim_end_var,
            length=220,
        )
        end_scale.grid(row=0, column=5, sticky="ew", padx=(6, 6))
        ttk.Label(trim_frame, textvariable=trim_end_text, width=4).grid(row=0, column=6, sticky="w")

        trim_frame.columnconfigure(2, weight=1)
        trim_frame.columnconfigure(5, weight=1)

        def _sync_trim_labels(*_args):
            s = int(round(trim_start_var.get()))
            e = int(round(trim_end_var.get()))
            trim_start_text.set(str(s))
            trim_end_text.set(str(e))

        trim_start_var.trace_add("write", _sync_trim_labels)
        trim_end_var.trace_add("write", _sync_trim_labels)

        def apply_trim_cut():
            start_idx = int(round(trim_start_var.get()))
            end_idx = int(round(trim_end_var.get()))
            if start_idx > end_idx:
                start_idx, end_idx = end_idx, start_idx

            cut_count = 0
            for i, d in enumerate(data, start=1):
                if i < start_idx or i > end_idx:
                    if not d['is_bad']:
                        file_path = d['path']
                        try:
                            target = file_path.with_name(f"BAD_{file_path.name}")
                            if target.exists():
                                continue
                            file_path.rename(target)
                            self.cache.rename(file_path, target)
                            if file_path in self.metadata_cache:
                                self.metadata_cache[target] = self.metadata_cache.pop(file_path)
                            self.files[self.files.index(file_path)] = target
                            d['path'] = target
                            d['is_bad'] = True
                            cut_count += 1
                        except Exception:
                            pass

            updated_colors = ['red' if d['is_bad'] else 'blue' for d in data]
            points.set_color(updated_colors)
            canvas.draw_idle()
            self._render_current_frame()
            messagebox.showinfo(
                "Trim Applied",
                f"Kept frames {start_idx}..{end_idx}. Marked {cut_count} outside frames as BAD.",
            )

        ttk.Button(trim_frame, text="Cut Outside Range", command=apply_trim_cut).grid(
            row=0, column=7, sticky="e", padx=(12, 0)
        )

    def toggle_bad_status(self) -> None:
        if not self.files:
            return
        current = self._current_file()
        is_bad = current.name.upper().startswith("BAD_")
        if is_bad:
            target_name = current.name[4:]
            if not target_name:
                messagebox.showerror("Toggle BAD", "Invalid BAD filename.")
                return
            target = current.with_name(target_name)
        else:
            target = current.with_name(f"BAD_{current.name}")

        if target.exists():
            messagebox.showerror("Toggle BAD", f"Cannot rename - target exists:\n{target.name}")
            return

        try:
            current.rename(target)
        except Exception as exc:
            messagebox.showerror("Toggle BAD", f"Failed to rename file:\n{exc}")
            return

        self.cache.rename(current, target)
        # Update metadata cache
        if current in self.metadata_cache:
            self.metadata_cache[target] = self.metadata_cache.pop(current)
        self.files[self.index] = target
        self._render_current_frame()

    def run(self) -> None:
        self.root.mainloop()


def main() -> int:
    parser = argparse.ArgumentParser(description="Interactive FITS viewer with linear stretch")
    parser.add_argument("folder_path", nargs="?", help="Folder containing FITS files (positional)")
    parser.add_argument("--folder", required=False, help="Folder containing FITS files")
    parser.add_argument("--fps", type=float, default=2.0, help="Initial playback speed in fps")
    args = parser.parse_args()

    folder: Path | None = None
    selected_folder = args.folder if args.folder else args.folder_path
    if selected_folder:
        folder = Path(selected_folder)
        if not folder.exists() or not folder.is_dir():
            print(f"[ERROR] Folder not found: {folder}")
            return 1

    try:
        app = FitsViewerApp(folder=folder, fps_default=args.fps)
    except Exception as exc:
        print(f"[ERROR] {exc}")
        return 1

    app.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

