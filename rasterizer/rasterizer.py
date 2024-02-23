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
    new_colors = np.select([colors <= 0.0031308, colors > 0.0031308], [12.92 * colors, 1.055 * (np.sign(colors) * np.abs(colors) ** (1/2.4)) - 0.055])
    return new_colors
    
def convert_to_linear(colors):
    colors = np.array(colors)
    new_colors = np.select([colors <= 0.04045, colors > 0.04045], [colors / 12.92, np.sign(colors) * np.abs((colors + 0.055) / 1.055) ** (2.4)])
    return new_colors

# Flags
sRGB = 0
depth = 0
hyp = 0
frustum = 0
texcoords = 0
fsaa = 0
cull = 0
color_n = 0
uMatrix = 0


# png
text = open(sys.argv[1], "r")
l = text.readline().split()
w = int(l[1])
h = int(l[2])
fn = l[3].strip("\n")

# Image
image = Image.new("RGBA", (w, h), (0,0,0,0))

# Image testing
#im = Image.open("rasterizer-files/rast-alpha.png")
#print(im.getpixel((50,50)))

# Check for depth
depth_vals = np.ones((w, h))
alpha_vals = np.zeros((w, h))

for i in text:
    l = np.array(i.split())

    # Skip empty lines
    if l.size == 0:
        continue

    # Color (r, g, b, a)
    if l[0] == "color":
        c = int(l[1])
        num = (len(l) - 2) // c
        
        if c == 3:
            color_n = 3
            cs = [[float(l[3*i+2]), float(l[3*i+3]), float(l[3*i+4]), 1] for i in range(num)]
        else:
            color_n = 4
            cs = [[float(l[4*i+2]), float(l[4*i+3]), float(l[4*i+4]), float(l[4*i+5])] for i in range(num)]

    # Position (x, y, z, w)
    if l[0] == "position":
        n = int(l[1])
        num = (len(l) - 2) // n
        if n == 2:
            pos = [[float(l[2*i+2]), float(l[2*i+3]), 0, 1] for i in range(num)]  
        elif n == 3:
            pos = [[float(l[3*i+2]), float(l[3*i+3]), float(l[3*i+4]), 1] for i in range(num)]  
        else:
            pos = [[float(l[4*i+2]), float(l[4*i+3]), float(l[4*i+4]), float(l[4*i+5])] for i in range(num)]

    # texture
    if l[0] == "texture":
        texture = Image.open(l[1])
    
    # texcoord (s, t)
    if l[0] == "texcoord":
        num = (len(l) - 2) // 2
        tc = [[float(l[2*i+2]), float(l[2*i+3])] for i in range(num)]  
        texcoords = 1

    # sRGB
    if l[0] == "sRGB":
        sRGB = 1

    # depth
    if l[0] == "depth":
        depth = 1

    # hyp
    if l[0] == "hyp":
        hyp = 1

    # frustum
    if l[0] == "frustum":
        frustum = 1

    # fsaa
    if l[0] == "fsaa":
        fsaa = float(l[1])

    # cull
    if l[0] == "cull":
        cull = 1

    # uniformMatrix:
    if l[0] == "uniformMatrix":
        uMatrix = 1
        num = (len(l) - 1) // 4
        uniformMatrix = np.array([[float(l[4*i+1]), float(l[4*i+2]), float(l[4*i+3]), float(l[4*i+4])] for i in range(num)]).T

    # drawArraysTriangles
    if l[0] == "drawArraysTriangles":
        s, count = int(l[1]), int(l[2])
        
        for i in range(count // 3):
            # Get top, middle, bottom y values
            vals = np.array([pos[(i*3) + s], pos[(i*3) + s+1], pos[(i*3) + s+2]])
            if uMatrix:
                for l_val in range(len(vals)):
                    vals[l_val] = np.matmul(uniformMatrix, vals[l_val])
            if color_n != 0:
                cols = np.array([cs[(i*3) + s], cs[(i*3) + s+1], cs[(i*3) + s+2]])
                vals = np.concatenate((vals, cols),axis=1)
            if texcoords:
                tcs = np.array([tc[(i*3) + s], tc[(i*3) + s+1], tc[(i*3) + s+2]])
                vals = np.concatenate((vals, tcs),axis=1)

            # Divide by w, viewport
            wc = vals[:, 3].copy()
            if hyp:
                vals[:,:] /= vals[:, 3, None]
            else:
                vals[:,:4] /= vals[:, 3, None]
            
            vals[:, 0] = ((vals[:, 0] + 1) / 2) * w
            vals[:, 1] = ((vals[:, 1] + 1) / 2) * h
            vals[:, 3] = 1 / wc

            vals = vals[np.argsort(vals[:,1])]
            # Assign top, middle, bottom vectors and setup
            t = vals[0]
            m = vals[1]
            b = vals[2]
            setup = dda(t, b, 1)
            if setup.size != 0:
                
                # Top half 
                th = dda(t, m, 1)
                if th.size != 0:
                    while th[0][1] < m[1]:
                        xp1 = dda(setup[0], th[0], 0)
                        if xp1.size != 0:
                            while (xp1[0][0] < th[0][0] or xp1[0][0] < setup[0][0]):

                                # Check if in bounds
                                if (xp1[0][0] < w and xp1[0][0] >= 0 and xp1[0][1] < h and xp1[0][1] >= 0):

                                    position = np.array([int(xp1[0][0]), int(xp1[0][1]), int(xp1[0][2]), int(xp1[0][3])])

                                    if hyp:
                                        w_val = xp1[0][3]
                                    else:
                                        w_val = 1

                                    color = [xp1[0][4] / w_val, xp1[0][5] / w_val, xp1[0][6] / w_val]
                                    alpha = 1
                                    if color_n == 4:
                                        r_d, g_d, b_d, _ = image.getpixel((position[0], position[1]))
                                        r_d, g_d, b_d = convert_to_linear([r_d / 255.0, g_d / 255.0, b_d / 255.0])
                                        a_s = xp1[0][7]
                                        a_d = alpha_vals[position[0], position[1]]
                                        a_p = a_s + (1 - a_s) * a_d
                                        
                                        color = (a_s / a_p) * np.array([color[0], color[1], color[2]]) + ((1 - a_s) * a_d / a_p) * np.array([r_d, g_d, b_d])
                                        alpha_vals[position[0], position[1]] = a_p
                                        alpha = a_p

                                    if sRGB:
                                        color = convert_sRGB(color)
                                    new_pos = (position[0], position[1])
                                    new_color = (int(color[0] * 255), int(color[1] * 255), int(color[2] * 255), int(alpha * 255))
                                    if (depth): 
                                        if (xp1[0][2] < depth_vals[int(xp1[0][0]), int(xp1[0][1])]):
                                            image.im.putpixel(new_pos, new_color)
                                            depth_vals[int(xp1[0][0]), int(xp1[0][1])] = xp1[0][2]
                                    else:
                                        image.im.putpixel(new_pos, new_color)
                                    
                                    
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
                                    position = np.array([int(xp2[0][0]), int(xp2[0][1]), int(xp2[0][2]), int(xp2[0][3])])
                                    
                                        
                                    if hyp:
                                        w_val = xp2[0][3]
                                    else:
                                        w_val = 1
                                    color = [xp2[0][4] / w_val, xp2[0][5] / w_val, xp2[0][6] / w_val]
                                    alpha = 1
                                    if color_n == 4:
                                        r_d, g_d, b_d, _ = image.getpixel((position[0], position[1]))
                                        r_d, g_d, b_d = convert_to_linear([r_d / 255.0, g_d / 255.0, b_d / 255.0])
                                        a_s = xp2[0][7]
                                        a_d = alpha_vals[position[0], position[1]]
                                        a_p = a_s + (1 - a_s) * (a_d)
                                        
                                        color = (a_s / a_p) * np.array([color[0], color[1], color[2]]) + ((1 - a_s) * a_d / a_p) * np.array([r_d, g_d, b_d])
                                        alpha_vals[position[0], position[1]] = a_p
                                        alpha = a_p
                                    
                                    if sRGB:
                                        color = convert_sRGB(color)

                                    new_pos = (int(position[0]), int(position[1]))
                                    new_color = (int(color[0] * 255), int(color[1] * 255), int(color[2] * 255), int(alpha * 255))
                                    if (depth): 
                                        if (xp2[0][2] < depth_vals[int(xp2[0][0]), int(xp2[0][1])]):
                                            image.im.putpixel(new_pos, new_color)
                                            depth_vals[int(xp2[0][0]), int(xp2[0][1])] = xp2[0][2]
                                    else:
                                        image.im.putpixel(new_pos, new_color)
                                    

                                xp2[0] += xp2[1]

                        bh[0] += bh[1]
                        setup[0] += setup[1]
        

    # Elements
    if l[0] == "elements":
        elems = l[1:].astype(np.uint8)

    # drawElementsTriangles
    if l[0] == "drawElementsTriangles":
        count, offset = int(l[1]), int(l[2])
        coun = 0
        for i in range(count // 3):
            # Get top, middle, bottom y values
            vals = np.array([pos[elems[(i*3) + offset]], pos[elems[(i*3) + offset +1]], pos[elems[(i*3) + offset + 2]]])
            if uMatrix:
                for l_val in range(len(vals)):
                    vals[l_val] = np.matmul(uniformMatrix, vals[l_val])
            if frustum:
                clip = np.array([[1,0,0,1],[-1,0,0,1],[0,1,0,1],[0,-1,0,1],[0,0,1,1],[0,0,-1,1]])
                dists = np.matmul(clip, vals.T)
                dists = dists >= 0
            if color_n != 0:
                cols = np.array([cs[elems[(i*3) + offset]], cs[elems[(i*3) + offset + 1]], cs[elems[(i*3) + offset + 2]]])
                vals = np.concatenate((vals, cols),axis=1)
            if texcoords:
                tcs = np.array([tc[elems[(i*3) + offset]], tc[elems[(i*3) + offset  + 1]], tc[elems[(i*3) + offset + 2]]])
                vals = np.concatenate((vals, tcs),axis=1)
            # Divide by w, viewport
            wc = vals[:, 3].copy()
            if hyp:
                vals[:,:] /= vals[:, 3, None]
            else:
                vals[:,:4] /= vals[:, 3, None]
            
            vals[:, 0] = ((vals[:, 0] + 1) / 2) * w
            vals[:, 1] = ((vals[:, 1] + 1) / 2) * h
            vals[:, 3] = 1 / wc

            vals = vals[np.argsort(vals[:,1])]
            
            # Assign top, middle, bottom vectors and setup
            t = vals[0]
            m = vals[1]
            b = vals[2]
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
                                    
                                    position = np.array([int(xp1[0][0]), int(xp1[0][1]), int(xp1[0][2]), int(xp1[0][3])])
                                    if hyp:
                                        w_val = xp1[0][3]
                                    else:
                                        w_val = 1
                                    if texcoords:
                                        if color_n == 0:
                                            r, g, b, _ = texture.getpixel((xp1[0][4] % 1, xp1[0][5] % 1))
                                            color = [r, g, b]
                                    else:
                                        color = [xp1[0][4] / w_val, xp1[0][5] / w_val, xp1[0][6] / w_val]
                                    alpha = 1
                                    if color_n == 4:
                                        r_d, g_d, b_d, _ = image.getpixel((position[0], position[1]))
                                        r_d, g_d, b_d = convert_to_linear([r_d / 255.0, g_d / 255.0, b_d / 255.0])
                                        a_s = xp1[0][7]
                                        a_d = alpha_vals[position[0], position[1]]
                                        a_p = a_s + (1 - a_s) * a_d
                                        
                                        color = (a_s / a_p) * np.array([color[0], color[1], color[2]]) + ((1 - a_s) * a_d / a_p) * np.array([r_d, g_d, b_d])
                                        alpha_vals[position[0], position[1]] = a_p
                                        alpha = a_p

                                    if sRGB:
                                        color = convert_sRGB(color)
                                    new_pos = (position[0], position[1])
                                    new_color = (int(color[0] * 255), int(color[1] * 255), int(color[2] * 255), int(alpha * 255))
                                    if (depth): 
                                        if (xp1[0][2] < depth_vals[int(xp1[0][0]), int(xp1[0][1])]):
                                            image.im.putpixel(new_pos, new_color)
                                            depth_vals[int(xp1[0][0]), int(xp1[0][1])] = xp1[0][2]
                                    else:
                                        image.im.putpixel(new_pos, new_color)
                                    
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
                                    #clip = np.array([[1,0,0,1],[-1,0,0,1],[0,1,0,1],[0,-1,0,1],[0,0,1,1],[0,0,-1,1]])
                                    position = np.array([int(xp2[0][0]), int(xp2[0][1]), int(xp2[0][2]), int(xp2[0][3])])
                                    
                                        
                                    if hyp:
                                        w_val = xp2[0][3]
                                    else:
                                        w_val = 1

                                    if texcoords:
                                        if color_n == 0:
                                            r, g, b, _ = texture.getpixel((xp2[0][4] % 1, xp2[0][5] % 1))
                                            color = [r, g, b]
                                    else:
                                        color = [xp2[0][4] / w_val, xp2[0][5] / w_val, xp2[0][6] / w_val]
                                    alpha = 1
                                    if color_n == 4:
                                        r_d, g_d, b_d, _ = image.getpixel((position[0], position[1]))
                                        r_d, g_d, b_d = convert_to_linear([r_d / 255.0, g_d / 255.0, b_d / 255.0])
                                        a_s = xp2[0][7]
                                        a_d = alpha_vals[position[0], position[1]]
                                        a_p = a_s + (1 - a_s) * (a_d)
                                        
                                        color = (a_s / a_p) * np.array([color[0], color[1], color[2]]) + ((1 - a_s) * a_d / a_p) * np.array([r_d, g_d, b_d])
                                        alpha_vals[position[0], position[1]] = a_p
                                        alpha = a_p
                                    
                                    if sRGB:
                                        color = convert_sRGB(color)

                                    new_pos = (int(position[0]), int(position[1]))
                                    new_color = (int(color[0] * 255), int(color[1] * 255), int(color[2] * 255), int(alpha * 255))
                                    if (depth): 
                                        if (xp2[0][2] < depth_vals[int(xp2[0][0]), int(xp2[0][1])]):
                                            image.im.putpixel(new_pos, new_color)
                                            depth_vals[int(xp2[0][0]), int(xp2[0][1])] = xp2[0][2]
                                    else:
                                        image.im.putpixel(new_pos, new_color)
                                    

                                xp2[0] += xp2[1]
                        bh[0] += bh[1]
                        setup[0] += setup[1]

# Check pixel
#print(image.getpixel((50,50)))
#image.im.putpixel((50,50), (128,128,128,255))


image.save(fn)