from PIL import Image
import sys
import numpy as np
import math

def dda(l1, l2, i):
    if l1[i] == l2[i]:
        pass
    elif l1[i] > l2[i]:
        l1, l2 = l2, l1
    d = l2 - l1
    s = d /(l2[i] - l1[i])
    e = math.ceil(l1[i]) - l1[i]
    o = e * s
    p = t + o  
    print(p)
    return np.array([p, s])

text = open(sys.argv[1], "r")
l = text.readline().split()
w = int(l[1])
h = int(l[2])
fn = l[3].strip("\n")
image = Image.new("RGBA", (w, h), (0,0,0,0))

for i in text:
    l = i.split()
    if not l:
        continue
    # Color
    if l[0] == "color":
        print(l)
        c = int(l[1])
        num = (len(l) - 2) // c
        if c == 3:
            cs = [[int(l[3*i+2]), int(l[3*i+3]), int(l[3*i+4])] for i in range(num)]
        else:
            cs = [[int(l[4*i+2]), int(l[4*i+3]), int(l[4*i+4]), int(l[4*i+5])] for i in range(num)]
        print(cs)
    # Position
    if l[0] == "position":
        n = int(l[1])
        num = (len(l) - 2) // n
        if n == 2:
            pos = [[(float(l[2*i+2])+1) * w / 2, (float(l[2*i+3])+1) * h / 2] for i in range(num)]  
        elif n == 3:
            pos = [[(float(l[3*i+2])+1) * w / 2, (float(l[3*i+3])+1) * w / 2] for i in range(num)]  
        else:
            pos = [[(float(l[4*i+2])/float(l[4*i+5])+1) * w / 2, (float(l[4*i+3])/float(l[4*i+5])+1) * h / 2, float(l[4*i+4]), float(l[4*i+5])] for i in range(num)]
        print(pos)

    if l[0] == "drawArraysTriangles":
        s, count = int(l[1]), int(l[2])
        print(s)
        for i in range(count):

            # Get t,b,m values
            vals = np.array([pos[i % 4],pos[(i+1) % 4],pos[(i+2) % 4]])
            vals = vals[np.argsort(vals[:,1])]
            cols = np.array([cs[i % 4],cs[(i+1) % 4],cs[(i+2) % 4]])
            tot = np.concatenate((vals, cols),axis=1)
            t = tot[0]
            m = tot[1]
            b = tot[2]

            sp = dda(t, b, 1)

            th = dda(t, m, 1)
            while sp[0][1] < m[1]:
                xp1 = dda(sp[0], th[0], 0)
                image.im.putpixel((th[0][0],th[0][1]), ())
                th[0] += th[1]
                sp[0] += sp[1]

            bh = dda(m, b, 1)
            while sp[0][1] < b[1]:
                xp2 = dda(sp[0], bh[0], 0)
                image.im.putpixel((bh[i][0],bh[i][1]), (cs[i][0], cs[i][1], cs[i][2], cs[i][3]))
                bh[0] += bh[1]
                sp[0] += sp[1]

image.save(fn)
