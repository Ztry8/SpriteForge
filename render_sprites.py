import sys
import os
import math
import argparse
import ctypes
import numpy as np

parser = argparse.ArgumentParser(description="Render 8-directional sprites from OBJ model")
parser.add_argument("--model",     required=True,  help="Path to .obj file")
parser.add_argument("--texture",   required=True,  help="Path to texture (PNG/JPG)")
parser.add_argument("--size",      type=int, default=512, help="Sprite size in pixels (default 512)")
parser.add_argument("--bg",        default="transparent", choices=["transparent", "black", "white", "green"],
                    help="Sprite background")
parser.add_argument("--outdir",    default="sprites", help="Output folder for sprites")
parser.add_argument("--prefix",    default="sprite",  help="Output filename prefix")
parser.add_argument("--sheet",     action="store_true", help="Also save a sprite sheet")
parser.add_argument("--elevation", type=float, default=15.0,
                    help="Camera elevation angle in degrees (0 = horizon, 30 = top-down)")
args = parser.parse_args()

import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from PIL import Image


DIRECTIONS = [
    ("S",   180),
    ("SW",  225),
    ("W",   270),
    ("NW",  315),
    ("N",     0),
    ("NE",   45),
    ("E",    90),
    ("SE",  135),
]


def compute_flat_normals(verts, faces):
    buf = []
    for tri in faces:
        (vi0, vti0, _), (vi1, vti1, _), (vi2, vti2, _) = tri

        p0 = verts["pos"][vi0]
        p1 = verts["pos"][vi1]
        p2 = verts["pos"][vi2]

        edge1 = p1 - p0
        edge2 = p2 - p0
        n = np.cross(edge1, edge2)
        length = np.linalg.norm(n)
        if length > 1e-9:
            n /= length
        else:
            n = np.array([0.0, 1.0, 0.0], dtype=np.float32)

        for vi, vti in ((vi0, vti0), (vi1, vti1), (vi2, vti2)):
            px, py, pz = verts["pos"][vi]
            nx, ny, nz = n
            u, v = verts["uv"][vti] if verts["uv"] is not None and vti >= 0 else (0.0, 0.0)
            buf.extend([px, py, pz, nx, ny, nz, u, v])

    return np.array(buf, dtype=np.float32)


def load_obj(path):
    raw_verts, raw_uvs, faces = [], [], []

    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            if parts[0] == "v":
                raw_verts.append([float(x) for x in parts[1:4]])
            elif parts[0] == "vt":
                raw_uvs.append([float(x) for x in parts[1:3]])
            elif parts[0] == "f":
                tri = []
                for token in parts[1:]:
                    indices = token.split("/")
                    vi  = int(indices[0]) - 1
                    vti = int(indices[1]) - 1 if len(indices) > 1 and indices[1] else -1
                    tri.append((vi, vti, -1))
                for i in range(1, len(tri) - 1):
                    faces.append([tri[0], tri[i], tri[i + 1]])

    pos = np.array(raw_verts, dtype=np.float32)
    uv  = np.array(raw_uvs,   dtype=np.float32) if raw_uvs else None

    center = (pos.max(axis=0) + pos.min(axis=0)) / 2.0
    pos -= center
    scale = np.max(np.abs(pos))
    if scale > 0:
        pos /= scale

    verts = {"pos": pos, "uv": uv}
    return verts, faces


def load_texture(path):
    img = Image.open(path).convert("RGBA")
    img = img.transpose(Image.FLIP_TOP_BOTTOM)
    img_data = np.array(img, dtype=np.uint8)

    tex_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex_id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA,
                 img.width, img.height, 0,
                 GL_RGBA, GL_UNSIGNED_BYTE, img_data)
    glGenerateMipmap(GL_TEXTURE_2D)
    return tex_id


def build_vbo(verts, faces):
    buf = compute_flat_normals(verts, faces)
    vbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, buf.nbytes, buf, GL_STATIC_DRAW)
    glBindBuffer(GL_ARRAY_BUFFER, 0)
    vertex_count = len(faces) * 3
    return vbo, vertex_count


def render_frame(vbo, vertex_count, tex_id, azimuth_deg, elevation_deg, size, bg_color):
    glViewport(0, 0, size, size)
    glClearColor(*bg_color)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glShadeModel(GL_FLAT)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(30.0, 1.0, 0.01, 100.0)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    cam_dist = 4.0
    elev_rad = math.radians(elevation_deg)
    azim_rad = math.radians(azimuth_deg)

    cam_x = cam_dist * math.cos(elev_rad) * math.sin(azim_rad)
    cam_y = cam_dist * math.sin(elev_rad)
    cam_z = cam_dist * math.cos(elev_rad) * math.cos(azim_rad)

    gluLookAt(cam_x, cam_y, cam_z,
              0, 0, 0,
              0, 1, 0)

    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_LIGHT1)
    glEnable(GL_LIGHT2)

    glLightfv(GL_LIGHT0, GL_POSITION, [1.5,  2.0,  1.5, 0.0])
    glLightfv(GL_LIGHT0, GL_DIFFUSE,  [1.0,  0.95, 0.9, 1.0])
    glLightfv(GL_LIGHT0, GL_SPECULAR, [0.7,  0.7,  0.7, 1.0])

    glLightfv(GL_LIGHT1, GL_POSITION, [-2.0, 1.0, -1.0, 0.0])
    glLightfv(GL_LIGHT1, GL_DIFFUSE,  [0.4,  0.45, 0.55, 1.0])
    glLightfv(GL_LIGHT1, GL_SPECULAR, [0.0,  0.0,  0.0,  1.0])

    glLightfv(GL_LIGHT2, GL_POSITION, [0.0, -1.0, -2.0, 0.0])
    glLightfv(GL_LIGHT2, GL_DIFFUSE,  [0.2,  0.2,  0.25, 1.0])
    glLightfv(GL_LIGHT2, GL_SPECULAR, [0.0,  0.0,  0.0,  1.0])

    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, [0.15, 0.15, 0.2, 1.0])
    glLightModeli(GL_LIGHT_MODEL_TWO_SIDE, GL_TRUE)

    glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT,   [0.25, 0.25, 0.25, 1.0])
    glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE,   [1.0,  1.0,  1.0,  1.0])
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR,  [0.4,  0.4,  0.4,  1.0])
    glMaterialf (GL_FRONT_AND_BACK, GL_SHININESS, 48.0)

    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, tex_id)
    glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)

    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    stride = 8 * 4

    glEnableClientState(GL_VERTEX_ARRAY)
    glEnableClientState(GL_NORMAL_ARRAY)
    glEnableClientState(GL_TEXTURE_COORD_ARRAY)

    glVertexPointer  (3, GL_FLOAT, stride, ctypes.c_void_p(0))
    glNormalPointer  (   GL_FLOAT, stride, ctypes.c_void_p(12))
    glTexCoordPointer(2, GL_FLOAT, stride, ctypes.c_void_p(24))

    glDrawArrays(GL_TRIANGLES, 0, vertex_count)

    glDisableClientState(GL_VERTEX_ARRAY)
    glDisableClientState(GL_NORMAL_ARRAY)
    glDisableClientState(GL_TEXTURE_COORD_ARRAY)
    glBindBuffer(GL_ARRAY_BUFFER, 0)
    glDisable(GL_LIGHTING)
    glDisable(GL_TEXTURE_2D)


def grab_frame(size, bg_transparent):
    if bg_transparent:
        pixels = glReadPixels(0, 0, size, size, GL_RGBA, GL_UNSIGNED_BYTE)
        img = Image.frombytes("RGBA", (size, size), pixels)
    else:
        pixels = glReadPixels(0, 0, size, size, GL_RGB, GL_UNSIGNED_BYTE)
        img = Image.frombytes("RGB", (size, size), pixels)
    return img.transpose(Image.FLIP_TOP_BOTTOM)


def main():
    SIZE = args.size
    BG_MAP = {
        "transparent": (0.0, 0.0, 0.0, 0.0),
        "black":       (0.0, 0.0, 0.0, 1.0),
        "white":       (1.0, 1.0, 1.0, 1.0),
        "green":       (0.0, 1.0, 0.0, 1.0),
    }
    bg_color       = BG_MAP[args.bg]
    bg_transparent = args.bg == "transparent"

    os.makedirs(args.outdir, exist_ok=True)

    pygame.init()
    pygame.display.set_mode((SIZE, SIZE), DOUBLEBUF | OPENGL | NOFRAME)
    pygame.display.set_caption("Sprite Renderer")

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_MULTISAMPLE)
    if bg_transparent:
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    print(f"Loading model: {args.model}")
    verts, faces = load_obj(args.model)
    print(f"  Vertices: {len(verts['pos'])}, Triangles: {len(faces)}")

    print(f"Loading texture: {args.texture}")
    tex_id = load_texture(args.texture)

    print("Building VBO with flat normals...")
    vbo, vertex_count = build_vbo(verts, faces)

    images = []
    print(f"\nRendering sprites {SIZE}x{SIZE}px...\n")

    for name, azimuth in DIRECTIONS:
        render_frame(vbo, vertex_count, tex_id,
                     azimuth, args.elevation, SIZE, bg_color)
        pygame.display.flip()

        img = grab_frame(SIZE, bg_transparent)
        images.append((name, azimuth, img))

        out_path = os.path.join(args.outdir, f"{args.prefix}_{name}.png")
        img.save(out_path, "PNG")
        print(f"  {name:3s} ({azimuth:3d} deg) -> {out_path}")

    if args.sheet:
        cols, rows = 4, 2
        sheet = Image.new("RGBA" if bg_transparent else "RGB",
                          (SIZE * cols, SIZE * rows), (0, 0, 0, 0))
        for i, (name, azimuth, img) in enumerate(images):
            x = (i % cols) * SIZE
            y = (i // cols) * SIZE
            sheet.paste(img, (x, y))
        sheet_path = os.path.join(args.outdir, f"{args.prefix}_sheet.png")
        sheet.save(sheet_path, "PNG")
        print(f"\nSprite sheet -> {sheet_path}")

    print(f"\nDone. Saved {len(images)} sprites to '{args.outdir}/'")
    pygame.quit()


if __name__ == "__main__":
    main()
