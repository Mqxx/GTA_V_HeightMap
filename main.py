import struct
import numpy as np
from PIL import Image
import os

# Map-Grenzen aus dem C#-Code
map_x_min, map_x_max = -4100, 4300
map_y_min, map_y_max = -4300, 7825

# Datei-Pfad der hochgeladenen Datei
file_path = "GTAV_HeightMap_Data.data"
output_path = "heightmap.png"  # Jetzt als PNG speichern

# Prüfen, ob die Datei existiert
if not os.path.exists(file_path):
    raise FileNotFoundError(f"Die Datei {file_path} wurde nicht gefunden. Bitte überprüfe den Pfad und stelle sicher, dass die Datei im richtigen Verzeichnis liegt.")

# Größe des Höhenrasters bestimmen
width = map_x_max - map_x_min
height = map_y_max - map_y_min

# Leeres Array für die Höhenwerte
height_data = np.zeros((height, width), dtype=np.float32)

# Datei einlesen und in das Array übertragen
try:
    with open(file_path, "rb") as f:
        for y in range(height):
            for x in range(width):
                data = f.read(4)
                if not data:
                    break
                height_data[y, x] = struct.unpack("f", data)[0]
except Exception as e:
    raise RuntimeError(f"Fehler beim Lesen der Datei: {e}")

# Werte normalisieren, wobei Hintergrund (height_data <= 0) schwarz bleibt
valid_mask = height_data > -100000  # Maske für gültige Höhenwerte
if np.any(valid_mask):
    min_h = np.min(height_data[valid_mask])
    max_h = np.max(height_data)
    norm_data = np.zeros_like(height_data, dtype=np.uint16)  # Hintergrund bleibt schwarz
    norm_data[valid_mask] = ((height_data[valid_mask] - min_h) / (max_h - min_h) * 65535).astype(np.uint16)
else:
    norm_data = np.zeros_like(height_data, dtype=np.uint16)  # Falls keine gültigen Werte da sind, bleibt alles schwarz

# Bild erstellen und umdrehen
image = Image.fromarray(norm_data, mode="I;16")
image = image.transpose(Image.FLIP_TOP_BOTTOM)  # <-- Hier wird das Bild umgedreht!

# Speichern als 16-Bit-PNG
image.save(output_path)
print(f"Bild gespeichert als {output_path}")
