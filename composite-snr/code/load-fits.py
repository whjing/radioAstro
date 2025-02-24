import sys
sys.path.append(".")
from loadSkyview import load_from_Skyview
import pandas as pd
file_csv = "../cat/three-cat.csv"

df = pd.read_csv(file_csv)

l = df['l'].astype(float)
b = df['b'].astype(float)
size = df['size_coarse (arcmin)'].astype(float)/60

for l,b,size in zip(l,b,size):
    load_from_Skyview(l, b, "G", size, "./short-radio-X-ray-IR.txt", outDir=".", max_retries=5)
