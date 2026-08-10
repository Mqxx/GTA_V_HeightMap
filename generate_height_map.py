import struct
import numpy as np
from PIL import Image
import os

# Datei-Pfad (bitte anpassen, falls nötig)
file_path = "hmap_high2.dat"
output_path = "heightmap2.png"

# Abmessungen der Heightmap aus dem C#-Script
columns, rows = 300, 90
size_x, size_y = 30, 150
step = 1  # Jeder Schritt = 1 Meter

# Berechnete Bildgröße (pro Meter ein Pixel)
width = columns * size_x
height = rows * size_y

# Erwartete Dateigröße berechnen
expected_size = width * height * 4  # 4 Bytes pro Float-Wert
if not os.path.exists(file_path):
    raise FileNotFoundError(f"Die Datei {file_path} wurde nicht gefunden.")

# Datei einlesen
with open(file_path, "rb") as f:
    file_data = f.read()

if len(file_data) != expected_size:
    raise ValueError(f"⚠️ Unerwartete Dateigröße! Erwartet: {expected_size} Bytes, aber gefunden: {len(file_data)} Bytes.")

# Daten in Float32 umwandeln
height_data = np.frombuffer(file_data, dtype=np.float32).reshape((height, width))

# ❗ Debug: Min- und Max-Werte der Höhen prüfen
print(f"🔍 Min-Höhe: {np.min(height_data)}, Max-Höhe: {np.max(height_data)}")

# ❗ Wichtig: Kopie erstellen, damit der Array schreibbar ist
height_data = height_data.copy()

# Negative Höhen (z. B. Wasser) auf 0 setzen
height_data[height_data < 0] = 0

# Höhendaten auf 0–65535 skalieren
min_h, max_h = np.min(height_data), np.max(height_data)

if max_h > min_h:
    height_image = ((height_data - min_h) / (max_h - min_h) * 65535).astype(np.uint16)
else:
    height_image = np.zeros_like(height_data, dtype=np.uint16)

# Bild erstellen und speichern
image = Image.fromarray(height_image, mode="I;16")
image = image.transpose(Image.FLIP_TOP_BOTTOM)  # Falls nötig, vertikal spiegeln
image.save(output_path)
print(f"✅ Heightmap gespeichert als {output_path}")
