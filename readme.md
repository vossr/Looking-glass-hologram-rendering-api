<p float="left">
<img src="img/stealth.gif" width="500" height="auto"/>
<img src="img/flat.gif" width="300" height="auto"/>
</p>

This abstracts the device api and lenticular rendering, so user can write a quilt renderer to show the hologram on the device.
Also implemented basic rgbd to quilt renderer.

# Usage
```bash
python3 -m pip install -e .
```

Inputs are cv2 images

To render image or already projected lenticular frame
```python
hologram_rendering.render_image(image)
```
<br>

To render a quilt  
tile dimensions should match your specific device
```python
hologram_rendering.render_quilt(quilt)
```
<br>

Displacement map implementation.  
offset_scale 0 to 1  
rot_max_rad radians  
```python
hologram_rendering.render_rgb_depth(rgb, depth, offset_scale, rot_max_rad):
```

<br>

## Horizontal camera reprojection methods
##### After depth estimation
##### The main issue is of course missing color data behind nearby geometry
- Displacement map + infill:
    - Track optical flow history for infill
    - Infill [Adobe PatchMatch](https://www.youtube.com/watch?v=8KGqD8voAkI)
    - [Owl3D](https://www.owl3d.com/) unknown deep learning temporal method
    - So goal temporally stable real-time [video inpainting](https://paperswithcode.com/task/video-inpainting)
    - https://huggingface.co/stabilityai/stable-diffusion-2-inpainting
- Deep learning end to end:
    - [comma.ai has one](https://youtu.be/EqQNZXqzFSI?t=322), small offset simulator for dashcam video
    - https://github.com/HypoX64/Deep3D
- Vertex grid textured heightmap
    - Similar to [jbienz refract](https://solersoft.github.io/Refract/)
    - Stretches the pixels
- Displacement map:
    - Doesn't try to fill missing data, texture samples with offset
- Displacement map with custom sampling:
    - Camera reprojection with only fragment shader depth buf analysis
    - Fill missing data with texture sampling tricks
- Displacement map or vertex grid with multiple layers:
    - Split to layers by depth
    - Similar to rgb depth [looking glass studio](https://lookingglassfactory.com/looking-glass-studio)
    - Similar to [Facebook 3D photos](https://techcrunch.com/2018/06/07/how-facebooks-new-3d-photos-work/)
    - Facebook uses CNN to hallucinate missing data
<br>

## Some other ideas i had

### View interpolation
Render left- and rightmost cameras, and interpolate rest with camera reprojection (or sbs to hologram)

### Single Pass Multiview Rendering
maybe with mesh shaders, render to all quilts with single pass

### Lenticular quilt culling
irl facecam that object tracks tracks eyes, so can render only needed views.  
for heavy raytracing or something


<br>
<br>

LICENSE: CC0
