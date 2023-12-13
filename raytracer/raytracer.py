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

# Default
color = np.array([1,1,1])
eye = np.array([0,0,0])
forward = np.array([0,0,-1])
right = np.array([1,0,0])
up = np.array([0,1,0])
light_color = color
sun_direction = np.array([1,1,1])

# Store objects
spheres = []
sphere_colors = []
ray_directions = []
suns = []
sun_colors = []
planes = []

# Flags
sun = 0
expose = 1
fisheye = 0
panorama = 0

def convert_to_sRGB(colors):
    new_colors = np.select([colors <= 0.0031308, colors > 0.0031308], [12.92 * colors, 1.055 * (np.sign(colors) * np.abs(colors) ** (1/2.4)) - 0.055])
    return new_colors

def convert_to_linear(colors):
    new_colors = np.select([colors <= 0.04045, colors > 0.04045], [colors / 12.92, np.sign(colors) * np.abs((colors + 0.055) / 1.055) ** (2.4)])
    return new_colors


for i in text:
    l = np.array(i.split())

    # Skip empty lines
    if l.size == 0:
        continue

    # Color
    if l[0] == "color":
        color = np.array([float(l[1]), float(l[2]), float(l[3])])

    # Sphere
    if l[0] == "sphere":
        spheres.append([float(l[1]), float(l[2]), float(l[3]), float(l[4])])
        sphere_colors.append(color)

    # Sun
    if l[0] == "sun":
        sun_direction = np.array([float(l[1]), float(l[2]), float(l[3])])
        suns.append(sun_direction)
        light_color = color
        sun_colors.append(light_color)
        sun = 1

    # up
    if l[0] == "up":
        up = np.array([float(l[1]), float(l[2]), float(l[3])])
    # eye
    if l[0] == "eye":
        eye = np.array([float(l[1]), float(l[2]), float(l[3])])

    # forward
    if l[0] == "forward":
        forward = np.array([float(l[1]), float(l[2]), float(l[3])])
        up = np.cross(right, forward)
        up = up / np.linalg.norm(up)
        right = np.cross(forward, up)
        right = right / np.linalg.norm(right)
        

    # expose
    if l[0] == "expose":
        expose = float(l[1])

    # fisheye
    if l[0] == "fisheye":
        fisheye = 1

    # panorama
    if l[0] == "panorama":
        panorama = 1
    
    # plane
    if l[0] == "plane":
        plane = np.array([float(l[1]), float(l[2]), float(l[3]), float(l[4])])


m_val = max(w, h)

for x in range(w):
    for y in range(h):
        
        sx = (2 * x - w) / m_val
        sy = (h - 2 * y) / m_val

        if fisheye:
            if sx ** 2 + sy ** 2 > 1:
                continue
            r_d = np.sqrt(1 - sx ** 2 - sy ** 2) * forward + sx * right + sy * up
        else:
            r_d = forward + sx * right + sy * up
        r_d = r_d / np.linalg.norm(r_d)
                
        t_closest = np.inf
        s_idx = -1
        for s in range(len(spheres)):
            center = np.array(spheres[s][0:3])
            r = spheres[s][3]
            ray = center - eye
            inside = np.linalg.norm(ray) < r ** 2
            
            r_d_mag = np.linalg.norm(r_d)
            t_c = np.dot(ray, r_d) / r_d_mag
            
            if not inside and t_c < 0:
                continue
            
            d_squared = np.linalg.norm(eye + t_c * r_d - center) ** 2

            if not inside and r ** 2 < d_squared:
                continue
            
            t_offset = np.sqrt(r ** 2 - d_squared) / r_d_mag
                
            if inside:
                t = t_c + t_offset
            else:
                t = t_c - t_offset
            
            # Finds closest sphere
            if t >= 0 and t < t_closest:
                t_closest = t
                s_idx = s
                

        if t_closest != np.inf:
            
            point = eye + t_closest * r_d
            s_t_close = np.inf
            s_idxs = -1
            for sp in range(len(spheres)):
                if sp != s_idx:
                    centers = np.array(spheres[sp][0:3])
                    rs = spheres[sp][3]
                    rays = centers - point
                    inside = np.linalg.norm(rays) < rs ** 2
                    r_ds = sun_direction
                    r_ds = r_ds / np.linalg.norm(r_ds)
                    t_cs = np.dot(rays, r_ds) / np.linalg.norm(r_ds)
                    
                    if not inside and t_cs < 0:
                        continue
                    
                    d_squareds = np.linalg.norm(point + t_cs * r_ds - centers) ** 2

                    if not inside and rs ** 2 < d_squareds:
                        continue
                    
                    t_offsets = np.sqrt(rs ** 2 - d_squareds) / np.linalg.norm(r_ds)
                    if inside:
                        ts = t_cs + t_offsets
                    else:
                        ts = t_cs - t_offsets
                    # Finds closest sphere
                    
                    if ts > 1e-10 and ts < s_t_close:

                        s_t_close = ts
                        s_idxs = sp
            
            # Light the pixel at (x,y)
            ccenter = np.array(spheres[s_idx][0:3])
            normal = (point - ccenter) / spheres[s_idx][3]
            normal = normal / np.linalg.norm(normal)

            if np.dot(r_d, normal) > 0:
                normal *= -1
            
            
            sun_dir = sun_direction / np.linalg.norm(sun_direction)
            if s_t_close != np.inf:
                image.im.putpixel((x, y), (0,0,0))
            else:
                if sun: 
                    colors = light_color * sphere_colors[s_idx] * np.dot(normal, sun_dir)
                else:
                    colors = np.array([0,0,0])
                if expose != 1:
                    colors = 1 - np.exp(-expose * colors)
                
                colors = convert_to_sRGB(colors)
                colors = np.clip(colors, 0, 1)

                image.im.putpixel((x, y), (int(colors[0] * 255), int(colors[1] * 255), int(colors[2] * 255)))


image.save(fn)