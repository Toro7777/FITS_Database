"""
Analyze FITS files to estimate star counts and mean ADU values.

This script recursively scans a folder for FITS files, computes:
- Estimated star count per file (local maxima above a robust threshold)
- Mean ADU value per file

Results are saved to a CSV table.

Usage:
    python fits_star_adu_table.py --input "C:\\Temp\\2026-03-25 SN2026ewa - ESPRIT 100"
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
from astropy.io import fits


FITS_EXTENSIONS = {".fits", ".fit", ".fts"}


@dataclass
class FitsMetrics:
    file_path: Path
    stars_estimated: int
    stars_used: int
    stars_source: str
    mean_adu: float
    shape: str
    exptime: str
    filter_name: str
    stars_metadata: int | None
    mean_adu_metadata: float | None
    stars_delta: int | None
    mean_adu_delta: float | None


def find_fits_files(root: Path) -> Iterable[Path]:
    for path in root.rglob("*"):
        if path.is_file() and path.suffix.lower() in FITS_EXTENSIONS:
            yield path


def _to_int(value: str | None) -> int | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        return int(float(text))
    except ValueError:
        return None


def _to_float(value: str | None) -> float | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        result = float(text)
    except ValueError:
        return None
    if not np.isfinite(result):
        return None
    return result


def load_image_metadata(root: Path) -> dict[str, dict[str, int | float | None]]:
    metadata_path = root / "ImageMetaData.csv"
    if not metadata_path.exists():
        return {}

    rows: dict[str, dict[str, int | float | None]] = {}
    try:
        with metadata_path.open("r", newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for rec in reader:
                file_path_raw = rec.get("FilePath")
                if not file_path_raw:
                    continue
                file_name = Path(file_path_raw).name.lower()
                rows[file_name] = {
                    "detected_stars": _to_int(rec.get("DetectedStars")),
                    "adu_mean": _to_float(rec.get("ADUMean")),
                }
    except Exception as exc:
        print(f"[WARN] Could not parse {metadata_path}: {exc}")
        return {}

    print(f"[INFO] Loaded metadata for {len(rows)} files from {metadata_path.name}")
    return rows


def lookup_metadata_for_file(
    file_name: str,
    metadata_by_name: dict[str, dict[str, int | float | None]],
) -> dict[str, int | float | None] | None:
    key = file_name.lower()

    if key in metadata_by_name:
        return metadata_by_name[key]

    # Allow local tags like BAD_ or VBAD_ prepended to the original file name.
    for prefix in ("bad_", "vbad_"):
        if key.startswith(prefix):
            stripped = key[len(prefix) :]
            if stripped in metadata_by_name:
                return metadata_by_name[stripped]

    # Final fallback for slight naming differences: suffix match.
    for meta_name, meta_row in metadata_by_name.items():
        if key.endswith(meta_name) or meta_name.endswith(key):
            return meta_row

    return None


def extract_image_data(file_path: Path) -> tuple[np.ndarray | None, fits.Header | None]:
    try:
        # Some calibrated FITS files use BZERO/BSCALE and cannot be memmapped.
        with fits.open(file_path, memmap=False) as hdul:
            for hdu in hdul:
                data = hdu.data
                if data is None:
                    continue
                arr = np.asarray(data, dtype=np.float32)
                if arr.size == 0:
                    continue
                header = hdu.header
                return arr, header
    except Exception as exc:
        print(f"[WARN] Could not read {file_path}: {exc}")
    return None, None


def normalize_to_2d(image: np.ndarray) -> np.ndarray:
    if image.ndim == 2:
        return image
    if image.ndim == 3:
        # Handle common 3D FITS cubes by collapsing the first axis.
        return np.nanmean(image, axis=0)
    if image.ndim > 3:
        collapsed = image
        while collapsed.ndim > 2:
            collapsed = np.nanmean(collapsed, axis=0)
        return collapsed
    return image.reshape(1, -1)


def estimate_star_count(image_2d: np.ndarray, sigma_threshold: float = 4.0) -> int:
    finite = np.isfinite(image_2d)
    if not finite.any():
        return 0

    img = np.where(finite, image_2d, np.nan)

    median = np.nanmedian(img)
    mad = np.nanmedian(np.abs(img - median))
    robust_sigma = 1.4826 * mad

    if not np.isfinite(robust_sigma) or robust_sigma <= 0:
        robust_sigma = np.nanstd(img)
    if not np.isfinite(robust_sigma) or robust_sigma <= 0:
        return 0

    threshold = median + sigma_threshold * robust_sigma

    padded = np.pad(img, 1, mode="edge")
    center = padded[1:-1, 1:-1]

    neighbors = [
        padded[:-2, :-2],
        padded[:-2, 1:-1],
        padded[:-2, 2:],
        padded[1:-1, :-2],
        padded[1:-1, 2:],
        padded[2:, :-2],
        padded[2:, 1:-1],
        padded[2:, 2:],
    ]

    is_peak = np.ones_like(center, dtype=bool)
    for nbr in neighbors:
        is_peak &= center > nbr

    stars = is_peak & (center > threshold) & np.isfinite(center)
    return int(np.count_nonzero(stars))


def compute_metrics(
    file_path: Path,
    metadata_entry: dict[str, int | float | None] | None = None,
) -> FitsMetrics | None:
    image, header = extract_image_data(file_path)
    if image is None:
        return None

    image_2d = normalize_to_2d(image)

    finite = np.isfinite(image_2d)
    if not finite.any():
        mean_adu = float("nan")
    else:
        mean_adu = float(np.nanmean(image_2d))

    stars = estimate_star_count(image_2d)

    exptime = ""
    filter_name = ""
    if header is not None:
        exptime = str(header.get("EXPTIME", ""))
        filter_name = str(header.get("FILTER", ""))

    stars_metadata: int | None = None
    mean_adu_metadata: float | None = None
    if metadata_entry is not None:
        stars_raw = metadata_entry.get("detected_stars")
        adu_raw = metadata_entry.get("adu_mean")
        stars_metadata = int(stars_raw) if isinstance(stars_raw, int) else None
        mean_adu_metadata = float(adu_raw) if isinstance(adu_raw, float) else None

    stars_delta = stars - stars_metadata if stars_metadata is not None else None
    mean_adu_delta = (
        mean_adu - mean_adu_metadata if mean_adu_metadata is not None and np.isfinite(mean_adu) else None
    )

    if stars_metadata is not None:
        stars_used = stars_metadata
        stars_source = "ImageMetaData.csv"
    else:
        stars_used = stars
        stars_source = "algorithm"

    return FitsMetrics(
        file_path=file_path,
        stars_estimated=stars,
        stars_used=stars_used,
        stars_source=stars_source,
        mean_adu=mean_adu,
        shape="x".join(str(v) for v in image_2d.shape),
        exptime=exptime,
        filter_name=filter_name,
        stars_metadata=stars_metadata,
        mean_adu_metadata=mean_adu_metadata,
        stars_delta=stars_delta,
        mean_adu_delta=mean_adu_delta,
    )


def write_csv(rows: list[FitsMetrics], output_csv: Path, root: Path) -> None:
    output_csv.parent.mkdir(parents=True, exist_ok=True)

    with output_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "file",
                "stars_used",
                "stars_source",
                "stars_estimated",
                "stars_metadata",
                "stars_delta",
                "mean_adu",
                "mean_adu_metadata",
                "mean_adu_delta",
                "shape",
                "exptime",
                "filter",
            ]
        )
        for row in rows:
            try:
                relative_path = row.file_path.relative_to(root)
            except ValueError:
                relative_path = row.file_path

            writer.writerow(
                [
                    str(relative_path),
                    row.stars_used,
                    row.stars_source,
                    row.stars_estimated,
                    row.stars_metadata if row.stars_metadata is not None else "",
                    row.stars_delta if row.stars_delta is not None else "",
                    f"{row.mean_adu:.3f}" if np.isfinite(row.mean_adu) else "",
                    f"{row.mean_adu_metadata:.3f}" if row.mean_adu_metadata is not None else "",
                    f"{row.mean_adu_delta:.3f}" if row.mean_adu_delta is not None else "",
                    row.shape,
                    row.exptime,
                    row.filter_name,
                ]
            )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Estimate star counts and mean ADU for FITS files in a folder."
    )
    parser.add_argument("--input", required=True, help="Root folder to scan for FITS files")
    parser.add_argument(
        "--output",
        default="fits_star_adu_table.csv",
        help="Output CSV path (default: fits_star_adu_table.csv)",
    )
    args = parser.parse_args()

    root = Path(args.input)
    if not root.exists() or not root.is_dir():
        print(f"[ERROR] Input folder does not exist or is not a folder: {root}")
        return 1

    fits_files = list(find_fits_files(root))
    if not fits_files:
        print(f"[INFO] No FITS files found under: {root}")
        return 0

    print(f"[INFO] Found {len(fits_files)} FITS files. Processing...")
    metadata_by_name = load_image_metadata(root)

    rows: list[FitsMetrics] = []
    for idx, file_path in enumerate(sorted(fits_files), start=1):
        metadata_entry = lookup_metadata_for_file(file_path.name, metadata_by_name)
        metrics = compute_metrics(file_path, metadata_entry=metadata_entry)
        if metrics is None:
            continue
        rows.append(metrics)
        if idx % 25 == 0:
            print(f"[INFO] Processed {idx}/{len(fits_files)} files...")

    output_csv = Path(args.output)
    write_csv(rows, output_csv, root)

    total_stars = sum(r.stars_used for r in rows)
    mean_of_means = float(np.mean([r.mean_adu for r in rows])) if rows else float("nan")

    print(f"[INFO] Wrote table: {output_csv.resolve()}")
    print(f"[INFO] Files analyzed: {len(rows)}")
    print(f"[INFO] Total stars (primary): {total_stars}")
    if np.isfinite(mean_of_means):
        print(f"[INFO] Average of per-file mean ADU: {mean_of_means:.3f}")

    rows_with_meta = [r for r in rows if r.stars_metadata is not None]
    if rows_with_meta:
        stars_abs_deltas = [abs(r.stars_delta) for r in rows_with_meta if r.stars_delta is not None]
        if stars_abs_deltas:
            print(
                "[INFO] Mean absolute stars delta (algo - metadata): "
                f"{float(np.mean(stars_abs_deltas)):.2f}"
            )

    rows_with_meta_adu = [r for r in rows if r.mean_adu_metadata is not None and r.mean_adu_delta is not None]
    if rows_with_meta_adu:
        adu_abs_deltas = [abs(r.mean_adu_delta) for r in rows_with_meta_adu]
        print(
            "[INFO] Mean absolute ADU delta (algo - metadata): "
            f"{float(np.mean(adu_abs_deltas)):.3f}"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
