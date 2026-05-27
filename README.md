# SpriteForge
## Simple and fast tool to render 8-directional sprites from 3D models

### About
When making retro-style games (like Daggerfall or classic Doom-era titles),    
3D characters are often represented as pre-rendered 2D sprites from multiple angles.    
Creating these by hand is tedious and inconsistent.

This script automates the process: given a .obj model and a texture,    
it renders 8 directional views (N, NE, E, SE, S, SW, W, NW) using OpenGL    
and saves each frame as a PNG sprite, ready to use in your game engine.    
Optionally, it can also produce a single sprite sheet with all 8 directions combined.

The camera elevation, sprite size, and background color are all configurable.    
Transparent backgrounds are supported for direct use in engines without chroma keying.

### Installation

#### Windows
Install Python, then:

```bash
pip install PyOpenGL PyOpenGL_accelerate pygame Pillow numpy
```

#### Linux

For Debian-based:

```bash
sudo apt install python3-pip python3-pygame
pip3 install PyOpenGL PyOpenGL_accelerate Pillow numpy
```

For Arch-based:

```bash
sudo pacman -S python-pip python-pygame
pip install PyOpenGL PyOpenGL_accelerate Pillow numpy
```

For RHEL-based:

```bash
sudo dnf install python3-pip
pip3 install PyOpenGL PyOpenGL_accelerate pygame Pillow numpy
```

#### macOS

```bash
sudo port install python3
pip3 install PyOpenGL PyOpenGL_accelerate pygame Pillow numpy
```

### Usage

```bash
python render_sprites.py --model model.obj --texture texture.png
All options
Argument	Default	Meaning
--model	(required)	Path to .obj file
--texture	(required)	Path to texture (PNG/JPG)
--size	512	Output sprite size in pixels
--bg	transparent	Background: transparent, black, white, green
--outdir	sprites	Output folder for sprites
--prefix	sprite	Filename prefix for output files
--sheet	off	Also save a combined sprite sheet
--elevation	15.0	Camera elevation angle in degrees
```

### Examples

```
python render_sprites.py --model goblin.obj --texture goblin.png --size 256 --sheet
python render_sprites.py --model chest.obj --texture chest.png --bg green --outdir chest_sprites
python render_sprites.py --model hero.obj --texture hero.png --elevation 25 --prefix hero
Output
Loading model: goblin.obj
  Vertices: 1423, Triangles: 2688
Loading texture: goblin.png
Building VBO with flat normals...

Rendering sprites 256x256px...

  S   (180 deg) -> sprites/sprite_S.png
  SW  (225 deg) -> sprites/sprite_SW.png
  W   (270 deg) -> sprites/sprite_W.png
  NW  (315 deg) -> sprites/sprite_NW.png
  N   (  0 deg) -> sprites/sprite_N.png
  NE  ( 45 deg) -> sprites/sprite_NE.png
  E   ( 90 deg) -> sprites/sprite_E.png
  SE  (135 deg) -> sprites/sprite_SE.png

Sprite sheet -> sprites/sprite_sheet.png

Done. Saved 8 sprites to 'sprites/'
```
