import struct
import numpy as np
from PIL import Image
import os

# ======= NEUE PARAMETER (aus C#-Skript übernehmen) ======= #
Columns = 300
Rows = 90
SizeX = 30
SizeY = 150
Step = 1.0  # (Nicht direkt relevant für das Laden)

# Berechnete Breite & Höhe
width = SizeX * Columns
height = SizeY * Rows

# Datei-Pfad
file_path = "hmap_high.dat"
output_path = "heightmap.png"

# Prüfen, ob die Datei existiert
if not os.path.exists(file_path):
    raise FileNotFoundError(f"Die Datei {file_path} wurde nicht gefunden. Bitte überprüfe den Pfad.")

# ======= DATEI LADEN ======= #
# Wir wissen, dass die Datei nur Float32-Werte enthält
expected_size = width * height * 4  # Jedes Float hat 4 Bytes

# Datei lesen
with open(file_path, "rb") as f:
    file_data = f.read()

if len(file_data) != expected_size:
    raise ValueError(f"⚠️ Unerwartete Dateigröße! Erwartet: {expected_size} Bytes, aber gefunden: {len(file_data)} Bytes.")

# Daten in ein NumPy-Array umwandeln
height_data = np.frombuffer(file_data, dtype=np.float32).reshape((height, width))

# ======= HINTERGRUND SCHWARZ & NORMALISIERUNG ======= #
valid_mask = height_data > 0  # Nur echte Werte berücksichtigen
if np.any(valid_mask):
    min_h = np.min(height_data[valid_mask])
    max_h = np.max(height_data)
    norm_data = np.zeros_like(height_data, dtype=np.uint16)  # Hintergrund bleibt schwarz
    norm_data[valid_mask] = ((height_data[valid_mask] - min_h) / (max_h - min_h) * 65535).astype(np.uint16)
else:
    norm_data = np.zeros_like(height_data, dtype=np.uint16)  # Falls alles 0 ist, bleibt es schwarz

# ======= BILD ERSTELLEN & SPEICHERN ======= #
image = Image.fromarray(norm_data, mode="I;16")
image = image.transpose(Image.FLIP_TOP_BOTTOM)  # Falls nötig, vertikal spiegeln
image.save(output_path)

print(f"✅ Bild erfolgreich gespeichert als {output_path}")
