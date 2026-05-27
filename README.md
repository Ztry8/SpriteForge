# SpriteForge

[![GitHub last commit](https://img.shields.io/github/last-commit/ztry8/spriteforge)](https://github.com/ztry8/spriteforge/commits)
[![License](https://img.shields.io/github/license/ztry8/spriteforge)](https://github.com/ztry8/spriteforge/blob/main/LICENSE)

## Simple and fast tool to render 8-directional sprites from 3D models

### About
When making retro-style games (like Daggerfall or classic Doom-era titles),    
3D characters are often represented as pre-rendered 2D sprites from multiple angles.    
Creating these by hand is tedious and inconsistent.

This script automates the process: given a .obj model and a texture,    
it renders 8 directional views (`BACK_LEFT`, `BACK`, `BACK_RIGHT`, `RIGHT`, `FRONT_RIGHT`, `FRONT`, `FRONT_LEFT`, `LEFT`, `BACK_LEFT`) using OpenGL    
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

#### Example of output
```
$ python render_sprites.py --model hero.obj --texture hero.png --elevation 25 --prefix hero
Loading model: hero.obj
  Vertices: 203, Triangles: 402
Loading texture: hero.png
Building VBO with smooth normals...

Rendering sprites 512x512px...

  BACK_LEFT (180 deg) -> sprites/sprite_BACK_LEFT.png
  BACK (225 deg) -> sprites/sprite_BACK.png
  BACK_RIGHT (270 deg) -> sprites/sprite_BACK_RIGHT.png
  RIGHT (315 deg) -> sprites/sprite_RIGHT.png
  FRONT_RIGHT (  0 deg) -> sprites/sprite_FRONT_RIGHT.png
  FRONT ( 45 deg) -> sprites/sprite_FRONT.png
  FRONT_LEFT ( 90 deg) -> sprites/sprite_FRONT_LEFT.png
  LEFT (135 deg) -> sprites/sprite_LEFT.png
  BACK_LEFT (180 deg) -> sprites/sprite_BACK_LEFT.png

Done. Saved 8 sprites to 'sprites/'
```

#### Example of result
 
![N](https://github.com/Ztry8/SpriteForge/blob/main/sprites/sprite_FRONT.png)
![NE](https://github.com/Ztry8/SpriteForge/blob/main/sprites/sprite_FRONT_RIGHT.png)
![E](https://github.com/Ztry8/SpriteForge/blob/main/sprites/sprite_FRONT_LEFT.png)
