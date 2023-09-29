from PIL import Image
import sys
import numpy as np
import math

def dda(a, b, i):
    if a[i] == b[i]:
        return np.array([])
    
    elif a[i] > b[i]:
        a, b = b, a

    d = (b - a)
    s = d / np.absolute(b[i] - a[i])
    e = math.ceil(a[i]) - a[i]
    o = e * s
    p = a + o  

    return np.array([p, s])

def convert_sRGB(colors):
    colors = np.array(colors)
    new_colors = np.select([colors <= 0.0031308, colors > 0.0031308], [12.92 * colors, 1.055 * (colors ** (1/2.4)) - 0.055])
    return new_colors
    

# Flags
sRGB = 0

# png
text = open(sys.argv[1], "r")
l = text.readline().split()
w = int(l[1])
h = int(l[2])
fn = l[3].strip("\n")

image = Image.new("RGBA", (w, h), (0,0,0,0))

for i in text:
    l = np.array(i.split())

    # Skip empty lines
    if l.size == 0:
        continue

    # Color
    if l[0] == "color":
        c = int(l[1])
        num = (len(l) - 2) // c
        if c == 3:
            cs = [[float(l[3*i+2]), float(l[3*i+3]), float(l[3*i+4])] for i in range(num)]
            if sRGB:
                cs = convert_sRGB(cs)
        else:
            cs = [[float(l[4*i+2]), float(l[4*i+3]), float(l[4*i+4]), float(l[4*i+5])] for i in range(num)]
            if sRGB:
                cs = convert_sRGB(cs)

    # Position
    if l[0] == "position":
        n = int(l[1])
        num = (len(l) - 2) // n
        if n == 2:
            pos = [[float(l[2*i+2]), float(l[2*i+3])] for i in range(num)]  
        elif n == 3:
            pos = [[float(l[3*i+2]), float(l[3*i+3])] for i in range(num)]  
        else:
            pos = [[float(l[4*i+2]), float(l[4*i+3]), float(l[4*i+4]), float(l[4*i+5])] for i in range(num)]

    # sRGB
    if l[0] == "sRGB":
        sRGB = 1

    # drawArraysTriangles
    if l[0] == "drawArraysTriangles":
        s, count = int(l[1]), int(l[2])

        for i in range(count // 3):
            # Get top, middle, bottom y values
            vals = np.array([pos[(i*3) + s],pos[(i*3) + s+1],pos[(i*3) + s+2]])
            cols = np.array([cs[(i*3) + s],cs[(i*3) + s+1],cs[(i*3) + s+2]])
            tot = np.concatenate((vals, cols),axis=1)
            tot = tot[np.argsort(tot[:,1])]
            print(tot)
            
            # Divide by w, viewport
            wc = tot[:, 3].copy()
            tot[:,:] /= tot[:, 3, None]
            
            tot[:, 0] = (tot[:, 0] + 1) * w / 2
            tot[:, 1] = (tot[:, 1] + 1) * h / 2
            tot[:, 3] = 1 / wc
            tot[:, 4:] /= tot[:, 3, None]
            
            # Assign top, middle, bottom vectors and setup
            t = tot[0]
            m = tot[1]
            b = tot[2]
            setup = dda(t, b, 1)
            if setup.size != 0:

                # Top half 
                th = dda(t, m, 1)
                if th.size != 0:
                    while th[0][1] < m[1]:
                        xp1 = dda(setup[0], th[0], 0)
                        if xp1.size != 0:
                            while (xp1[0][0] < th[0][0] or xp1[0][0] < setup[0][0]):
                                if (xp1[0][0] < w and xp1[0][0] >=0 and xp1[0][1] < h and xp1[0][1] >= 0):
                                    print("One")
                                    print(xp1)
                                    xp1[:,4:] = convert_sRGB(xp1[:,4:])
                                    print("Two")
                                    print(xp1)
                                    image.im.putpixel((int(xp1[0][0]), int(xp1[0][1])), (int(xp1[0][4] * 255), int(xp1[0][5] * 255), int(xp1[0][6] * 255)))
                                xp1[0] += xp1[1]
                        
                        th[0] += th[1]
                        setup[0] += setup[1]
                    
                
                # Bottom half
                bh = dda(m, b, 1)
                if bh.size != 0:
                    while bh[0][1] < b[1]:
                        xp2 = dda(setup[0], bh[0], 0)
                        if xp2.size != 0:
                            while (xp2[0][0] < bh[0][0] or xp2[0][0] < setup[0][0]):
                                if (xp2[0][0] < w and xp2[0][0] >= 0 and xp2[0][1] < h and xp2[0][1] >= 0):
                                    image.im.putpixel((int(xp2[0][0]), int(xp2[0][1])), (int(xp2[0][4] * 255), int(xp2[0][5] * 255), int(xp2[0][6] * 255)))
                                xp2[0] += xp2[1]
                        bh[0] += bh[1]
                        setup[0] += setup[1]
    
    # Elements
    if l[0] == "elements":
        elems = l[1:].astype(np.uint8)
        print(elems)

    # drawElementsTriangles
    if l[0] == "drawElementsTriangles":
        count, offset = int(l[1]), int(l[2])

        for i in range(count // 3):
            # Get top, middle, bottom y values
            vals = np.array([pos[elems[(i*3) + offset]], pos[elems[(i*3) + offset +1]], pos[elems[(i*3) + offset + 2]]])
            cols = np.array([cs[elems[(i*3) + offset]], cs[elems[(i*3) + offset +1]], cs[elems[(i*3) + offset + 2]]])
            tot = np.concatenate((vals, cols),axis=1)
            tot = tot[np.argsort(tot[:,1])]
            
            # Divide by w, viewport
            wc = tot[:, 3].copy()
            tot[:,:] /= tot[:, 3, None]
            
            tot[:, 0] = (tot[:, 0] + 1) * w / 2
            tot[:, 1] = (tot[:, 1] + 1) * h / 2
            tot[:, 3] = 1 / wc
            tot[:, 4:] /= tot[:, 3, None]
            
            # Assign top, middle, bottom vectors and setup
            t = tot[0]
            m = tot[1]
            b = tot[2]
            setup = dda(t, b, 1)
            if setup.size != 0:

                # Top half 
                th = dda(t, m, 1)
                if th.size != 0:
                    while th[0][1] < m[1]:
                        xp1 = dda(setup[0], th[0], 0)
                        if xp1.size != 0:
                            while (xp1[0][0] < th[0][0] or xp1[0][0] < setup[0][0]):
                                if (xp1[0][0] < w and xp1[0][0] >=0 and xp1[0][1] < h and xp1[0][1] >= 0):
                                    image.im.putpixel((int(xp1[0][0]), int(xp1[0][1])), (int(xp1[0][4] * 255), int(xp1[0][5] * 255), int(xp1[0][6] * 255)))
                                xp1[0] += xp1[1]
                        
                        th[0] += th[1]
                        setup[0] += setup[1]
                    
                
                # Bottom half
                bh = dda(m, b, 1)
                if bh.size != 0:
                    while bh[0][1] < b[1]:
                        xp2 = dda(setup[0], bh[0], 0)
                        if xp2.size != 0:
                            while (xp2[0][0] < bh[0][0] or xp2[0][0] < setup[0][0]):
                                if (xp2[0][0] < w and xp2[0][0] >= 0 and xp2[0][1] < h and xp2[0][1] >= 0):
                                    image.im.putpixel((int(xp2[0][0]), int(xp2[0][1])), (int(xp2[0][4] * 255), int(xp2[0][5] * 255), int(xp2[0][6] * 255)))
                                xp2[0] += xp2[1]
                        bh[0] += bh[1]
                        setup[0] += setup[1]

image.save(fn)
