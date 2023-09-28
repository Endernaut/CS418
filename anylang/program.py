from PIL import Image
import sys

text = open(sys.argv[1], "r")
l = text.readline().split(" ")
w = int(l[1])
h = int(l[2])
fn = l[3].strip("\n")
image = Image.new("RGBA", (w, h), (0,0,0,0))

for i in text:
    l = i.split()
    
    # Color
    if l[0] == "color":
        num = (len(l) - 2) // 4
        cs = [[int(l[4*i+2]), int(l[4*i+3]), int(l[4*i+4]), int(l[4*i+5].strip("\n"))] for i in range(num)]

    # Position
    if l[0] == "position":
        num = (len(l) - 2) // 2
        pos = [[int(l[2*i+2]), int(l[2*i+3].strip("\n"))] for i in range(num)]
        
    # Pixel count
    if l[0] == "drawPixels":
        ps = int(l[1].strip("\n"))
        for i in range(0, ps):
            image.im.putpixel((pos[i][0],pos[i][1]), (cs[i][0], cs[i][1], cs[i][2], cs[i][3]))

image.save(fn)
