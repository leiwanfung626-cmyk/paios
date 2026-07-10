# 01_extract_exif.py — EXIF 元数据提取
# 支持：JPG/PNG/WebP/TIFF (PIL)、HEIC (pillow_heif)、CR2 (rawpy)
# 降级：无法读取时用文件修改时间兜底
import sys
import os
import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils import classify_media_type
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

try:
    import rawpy
    HAVE_RAWPY = True
except ImportError:
    HAVE_RAWPY = False

try:
    import pillow_heif
    pillow_heif.register_heif_opener()
    HAVE_HEIF = True
except ImportError:
    HAVE_HEIF = False


def _dms_to_deg(dms, ref):
    try:
        def f(v):
            if hasattr(v, "__getitem__") and len(v) == 2:
                return float(v[0]) / float(v[1])
            return float(v)

        d = f(dms[0])
        m = f(dms[1])
        s = f(dms[2])
        deg = d + m / 60.0 + s / 3600.0
        if ref in ("S", "W"):
            deg = -deg
        return round(deg, 6)
    except Exception:
        return None


def _pil_meta(img):
    out = {"date": None, "camera": None, "gps": None, "width": None, "height": None}
    try:
        out["width"], out["height"] = img.size
    except Exception:
        pass
    try:
        exif = img._getexif()
    except Exception:
        exif = None
    if not exif:
        return out
    for tag, val in exif.items():
        name = TAGS.get(tag, tag)
        if name == "DateTimeOriginal" and not out["date"]:
            out["date"] = val
        elif name == "Model" and not out["camera"]:
            out["camera"] = str(val)
        elif name == "GPSInfo":
            try:
                gps = {}
                for t in val:
                    gps[GPSTAGS.get(t, t)] = val[t]
                if "GPSLatitude" in gps and "GPSLatitudeRef" in gps:
                    lat = _dms_to_deg(gps["GPSLatitude"], gps["GPSLatitudeRef"])
                    lon = _dms_to_deg(gps["GPSLongitude"], gps["GPSLongitudeRef"])
                    if lat is not None and lon is not None:
                        out["gps"] = f"{lat:.6f},{lon:.6f}"
            except Exception:
                pass
    return out


def _parse_date(s):
    if not s:
        return None
    for fmt in ("%Y:%m:%d %H:%M:%S", "%Y:%m:%d %H:%M", "%Y:%m:%d"):
        try:
            return datetime.datetime.strptime(s, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None


def extract_exif(path):
    ext = os.path.splitext(path)[1].lower()
    media_type = classify_media_type(ext)
    result = {
        "date": None,
        "camera": None,
        "gps": None,
        "width": None,
        "height": None,
        "media_type": media_type,
    }
    # 文件修改时间兜底（任何情况下都有日期）
    try:
        st = os.stat(path)
        result["date"] = datetime.datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d")
    except Exception:
        result["date"] = None
    # RAW (CR2/NEF/ARW...)
    if media_type == "raw" and HAVE_RAWPY:
        try:
            with rawpy.imread(path) as raw:
                thumb = raw.extract_thumb()
                if thumb and hasattr(thumb, "width"):
                    result["width"], result["height"] = thumb.width, thumb.height
        except Exception:
            pass
    # PIL (JPG/PNG/WebP/HEIC/TIFF)
    try:
        with Image.open(path) as img:
            meta = _pil_meta(img)
            for k in ("camera", "gps", "width", "height"):
                if meta[k] is not None:
                    result[k] = meta[k]
            if meta["date"]:
                parsed = _parse_date(meta["date"])
                if parsed:
                    result["date"] = parsed
            return result
    except Exception:
        pass
    return result


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    args = ap.parse_args()
    print(extract_exif(args.path))
