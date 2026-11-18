#!/usr/bin/env python3
"""Bereitet Fotos für die Website vor.

Aufruf (im Hauptordner der Website):  python3 tools/bilder.py

Für jedes Foto in assets/gallery/, das noch keine Vorschau hat:
  - Großansicht auf höchstens 1920 px verkleinern
  - Vorschau mit 800 px in assets/gallery/thumbs/ anlegen
  - Metadaten (EXIF, z. B. GPS-Ort, Kameradaten) entfernen
Teamfotos in assets/team/ werden auf höchstens 800 px verkleinert.

Bereits bearbeitete Fotos bleiben unverändert, das Skript kann also
beliebig oft laufen. Benötigt Pillow:  pip install Pillow
"""
import os
import sys

try:
    from PIL import Image, ImageOps
except ImportError:
    sys.exit("Pillow fehlt. Bitte installieren:  pip install Pillow")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GALLERY = os.path.join(ROOT, "assets", "gallery")
THUMBS = os.path.join(GALLERY, "thumbs")
TEAM = os.path.join(ROOT, "assets", "team")


def save_jpeg(im, path, max_side, quality):
    """Dreht nach EXIF, verkleinert, speichert ohne Metadaten."""
    im = ImageOps.exif_transpose(im).convert("RGB")
    w, h = im.size
    scale = min(1.0, max_side / max(w, h))
    if scale < 1:
        im = im.resize((round(w * scale), round(h * scale)), Image.LANCZOS)
    im.save(path, "JPEG", quality=quality, optimize=True, progressive=True)
    return im.size


def main():
    os.makedirs(THUMBS, exist_ok=True)
    done = 0
    for name in sorted(os.listdir(GALLERY)):
        src = os.path.join(GALLERY, name)
        if not os.path.isfile(src):
            continue
        if not name.lower().endswith((".jpg", ".jpeg")):
            print(f"übersprungen (bitte als .jpg speichern): {name}")
            continue
        thumb = os.path.join(THUMBS, name)
        if os.path.exists(thumb):
            continue
        with Image.open(src) as im:
            im.load()
        save_jpeg(im.copy(), thumb, 800, 76)
        size = save_jpeg(im, src, 1920, 82)
        print(f"Galerie: {name}  {size[0]}x{size[1]}, Vorschau angelegt")
        done += 1

    if os.path.isdir(TEAM):
        for name in sorted(os.listdir(TEAM)):
            src = os.path.join(TEAM, name)
            if not name.lower().endswith((".jpg", ".jpeg")):
                continue
            with Image.open(src) as im:
                im.load()
            if max(im.size) <= 800 and not im.getexif():
                continue
            size = save_jpeg(im, src, 800, 80)
            print(f"Team: {name}  {size[0]}x{size[1]}")
            done += 1

    print("Fertig." if done else "Nichts zu tun, alle Fotos sind schon vorbereitet.")


if __name__ == "__main__":
    main()
