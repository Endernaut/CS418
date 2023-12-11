from PIL import Image
import sys
import numpy as np
import math

# Png
text = open(sys.argv[1], "r")
l = text.readline().split()
w = int(l[1])
h = int(l[2])
fn = l[3].strip("\n")

image = Image.new("RGBA", (w, h), (0,0,0,0))

color = np.array([1,1,1])


for i in text:
    l = np.array(i.split())

    # Skip empty lines
    if l.size == 0:
        continue

    # Color
    if l[0] == "color":
        pass
    # Sphere
    if l[0] == "sphere":
        inside = float(l[1]) ** 2 + float(l[2]) ** 2 + float(l[3]) ** 2 < float(l[4]) ** 2
        tc = 

    # Sun
    if l[0] == "sun":
        pass


image.save(fn)