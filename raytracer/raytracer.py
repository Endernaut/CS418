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

# Image check
#im = Image.open("raytracer-files/ray-plane.png")
#print(im.getpixel((90, 90)))

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
bulbs = []
vertices = [[]]
triangles = []
triangle_colors = []

# Flags
sun = 0
expose = 1
fisheye = 0
panorama = 0
bounces = 4

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

    # bulb
    if l[0] == "bulb":
        bulbs.append(np.array([float(l[1]), float(l[2]), float(l[3])]))

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
        right = np.cross(forward, up)
        up = up / np.linalg.norm(up)
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
        planes.append(np.array([float(l[1]), float(l[2]), float(l[3]), float(l[4])]))
    # aa
    if l[0] == "aa":
        aa = float(l[1])
    
    # xyz
    if l[0] == "xyz":
        vertices.append(np.array([float(l[1]), float(l[2]), float(l[3])]))
    
    # tri
    if l[0] == "tri":
        tri = np.array([vertices[int(l[1])], vertices[int(l[2])], vertices[int(l[3])]])
        triangles.append(tri)
        triangle_colors.append(color)
    
    # shininess
    if l[0] == "shininess":
        if len(l) == 2:
            shininess = np.array([float(l[1]), float(l[1]), float(l[1])])

m_val = max(w, h)

for x in range(w):
    for y in range(h):
        
        sx = (2 * x - w) / m_val
        sy = (h - 2 * y) / m_val

        r_d = forward + sx * right + sy * up
        if fisheye:
            
            if sx ** 2 + sy ** 2 > 1:
                continue
            print(sx ** 2 + sy ** 2)
            r_d = np.sqrt(1 - sx ** 2 - sy ** 2) * forward + sx * right + sy * up
        if panorama:
            r_d = np.cos(sx) * forward + np.sin(sx) * right + sy * up
            

        r_d = r_d / np.linalg.norm(r_d)
                
        t_closest = np.inf
        s_idx = -1
        p_idx = -1

        # Spheres
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
                
        # Planes
        for p in range(len(planes)):
            p_norm = np.array([planes[p][0], planes[p][1], planes[p][2]])
            p_norm = p_norm / np.linalg.norm(p_norm)
            p_point = -planes[p][3] * p_norm / np.linalg.norm(p_norm)
            ray_p = p_point - eye
            t = np.dot(ray_p, p_norm) / np.dot(r_d, p_norm)
            if t > 0 and t < t_closest:
                t_closest = t
                p_idx = p

        if t_closest != np.inf:
            
            point = eye + t_closest * r_d
            # Shadows
            shadow_closests = []
            sh_sun_close = []
            for shad_sun in suns:
                s_t_close = np.inf
                for sp in range(len(spheres)):
                    if sp != s_idx:
                        centers = np.array(spheres[sp][0:3])
                        rs = spheres[sp][3]
                        rays = centers - point
                        inside = np.linalg.norm(rays) < rs ** 2
                        r_ds = shad_sun
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

                
                            
                shadow_closests.append(s_t_close)
                sh_sun_close.append(shad_sun)

            # Reflections
            for b in range(bounces):
                pass
            
            # Light the pixel at (x,y)
            ccenter = np.array(spheres[s_idx][0:3])
            if (s_idx != -1):
                normal = (point - ccenter) / spheres[s_idx][3]
                long = np.arctan2(normal[0], normal[2])
                lat = np.arctan2(normal[1], np.sqrt(normal[0] ** 2 + normal[2] ** 2))
                if (x == 3 and y == 3):
                    print(long, lat)
            elif (p_idx != -1):
                normal = planes[p_idx][0:3]
            normal = normal / np.linalg.norm(normal)

            if np.dot(r_d, normal) > 0:
                normal *= -1
            
            pix_color = np.array([0,0,0]).astype(np.float64)
            light_combo = np.array([0,0,0]).astype(np.float64)
            colors = sphere_colors[s_idx]
            for sun_idx in range(len(shadow_closests)):
                # Add sun colors if not occluded
                if shadow_closests[sun_idx] == np.inf:
                    sun_d = sh_sun_close[sun_idx] + eye
                    sun_d = sun_d / np.linalg.norm(sun_d)
                    light_combo += sun_colors[sun_idx] * np.dot(normal, sun_d)
                    
            pix_color += np.array(colors) * light_combo
                        
            if expose != 1:
                pix_color = 1 - np.exp(-expose * pix_color)
                    
            pix_color = convert_to_sRGB(pix_color)
            pix_color = np.clip(pix_color, 0, 1)
      
            image.im.putpixel((x, y), (int(pix_color[0] * 255), int(pix_color[1] * 255), int(pix_color[2] * 255)))
# Check pixel
#print(image.getpixel((90, 90)))
#image.im.putpixel((90, 90), (128,128,128,255))

image.save(fn)