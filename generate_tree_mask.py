import struct
import numpy as np
from PIL import Image
import os
from scipy.ndimage import maximum_filter, minimum_filter

# Datei-Pfad (bitte anpassen, falls nötig)
file_path = "hmap_high.dat"
bitmask_output_path = "tree_mask.png"

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

# **Bitmaske für isolierte high spots erstellen**
threshold = 8.0  # Differenzgrenze, anpassbar

# 1. Lokale Maxima in einem 3x3 Bereich finden
local_maxima = (height_data == maximum_filter(height_data, size=71))

# 2. Minimum in einem größeren Radius (z.B. 5x5) berechnen
min_in_radius = minimum_filter(height_data, size=2, mode='constant', cval=np.inf)

# 3. Bitmaske: lokale Maxima, die signifikant höher als das Minimum im Radius sind
bitmask = local_maxima & (height_data - min_in_radius >= threshold)

# Konvertieren zu uint8
bitmask = bitmask.astype(np.uint8)

# Bitmaske als PNG speichern (0 wird schwarz, 1 wird weiß)
bitmask_image = Image.fromarray(bitmask * 255, mode="L")
bitmask_image = bitmask_image.transpose(Image.FLIP_TOP_BOTTOM)  # Vertikal spiegeln, wie beim Original
bitmask_image.save(bitmask_output_path)
print(f"✅ Bitmaske gespeichert als {bitmask_output_path}")
