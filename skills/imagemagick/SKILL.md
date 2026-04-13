---
name: imagemagick
description: ImageMagick commands for image conversion, resizing, cropping, and batch processing. Use when user mentions "imagemagick", "convert image", "resize image", "crop image", "image format", "batch resize", "thumbnail", "watermark", "image manipulation", "magick", "mogrify", or processing images from the command line.
---

# ImageMagick Commands

ImageMagick v7 uses `magick` as the main command. On older systems (v6), use `convert`, `mogrify`, `identify`, `montage` directly.

## Image Info

```bash
# Dimensions, format, colorspace, filesize
magick identify image.png
magick identify -verbose image.png

# Just dimensions
magick identify -format "%wx%h" image.png

# Format, dimensions, filesize, colorspace in one line
magick identify -format "Format: %m, Size: %wx%h, Filesize: %b, Colorspace: %[colorspace]\n" image.png

# List all images in a directory
magick identify *.jpg
```

## Convert Between Formats

```bash
magick input.png output.jpg
magick input.jpg output.webp
magick input.png output.gif
magick input.svg output.png
magick input.png output.pdf
magick input.webp output.png

# Explicit format override (when extension is ambiguous)
magick PNG:input output.jpg
```

## Resize

```bash
# Resize to exact width x height (may distort)
magick input.png -resize 800x600! output.png

# Resize to fit within bounds (preserves aspect ratio)
magick input.png -resize 800x600 output.png

# Resize by width only (height scales proportionally)
magick input.png -resize 800x output.png

# Resize by height only
magick input.png -resize x600 output.png

# Resize by percentage
magick input.png -resize 50% output.png

# Resize only if larger (shrink-only flag >)
magick input.png -resize 800x600\> output.png

# Resize only if smaller (enlarge-only flag <)
magick input.png -resize 800x600\< output.png

# Fill area, cropping overflow (cover behavior)
magick input.png -resize 800x600^ -gravity center -extent 800x600 output.png
```

## Crop

```bash
# Crop WxH+X+Y (width x height from top-left offset)
magick input.png -crop 400x300+100+50 +repage output.png

# Crop from center
magick input.png -gravity center -crop 400x300+0+0 +repage output.png

# Auto-trim whitespace/uniform borders
magick input.png -trim +repage output.png

# Trim with fuzz tolerance (handles near-white borders)
magick input.png -fuzz 10% -trim +repage output.png

# Crop into tiles (e.g., 3x3 grid)
magick input.png -crop 33.33%x33.33% +repage tile_%d.png
```

## Quality and Compression

```bash
# JPEG quality (1-100, default ~92)
magick input.png -quality 85 output.jpg

# WebP quality (1-100)
magick input.png -quality 80 output.webp

# PNG compression level (0-9 mapped to quality 0-90, where lower = more compression)
magick input.png -quality 90 output.png

# Lossless WebP
magick input.png -define webp:lossless=true output.webp

# JPEG with specific sampling factor
magick input.png -sampling-factor 4:2:0 -quality 85 output.jpg
```

## Batch Processing with Mogrify

Mogrify modifies files in place. Use `-path` to write to a different directory.

```bash
# Convert all PNGs to JPG in a new directory
mkdir -p converted
magick mogrify -path converted -format jpg *.png

# Resize all images in place
magick mogrify -resize 800x600 *.jpg

# Resize and output to directory
mkdir -p resized
magick mogrify -path resized -resize 50% *.png

# Batch quality reduction
mkdir -p compressed
magick mogrify -path compressed -quality 80 *.jpg

# Batch format conversion with resize
mkdir -p thumbnails
magick mogrify -path thumbnails -resize 200x200 -format webp *.png
```

## Create Thumbnails

```bash
# Simple thumbnail (preserves aspect ratio)
magick input.png -thumbnail 150x150 thumb.png

# Square thumbnail with crop (cover + center crop)
magick input.png -thumbnail 150x150^ -gravity center -extent 150x150 thumb.png

# Thumbnail strip metadata
magick input.png -thumbnail 150x150 -strip thumb.png

# Batch thumbnails
mkdir -p thumbs
magick mogrify -path thumbs -thumbnail 200x200^ -gravity center -extent 200x200 *.jpg
```

## Watermark

```bash
# Text watermark
magick input.png \
  -gravity southeast \
  -fill "rgba(255,255,255,0.5)" \
  -pointsize 24 \
  -annotate +10+10 "Copyright 2026" \
  output.png

# Text watermark with background
magick input.png \
  -gravity south \
  -fill white -undercolor "rgba(0,0,0,0.5)" \
  -pointsize 20 \
  -annotate +0+10 " My Watermark " \
  output.png

# Image overlay watermark (bottom-right, 20% opacity)
magick input.png \
  \( watermark.png -resize 200x -alpha set -channel A -evaluate set 20% +channel \) \
  -gravity southeast -geometry +10+10 \
  -composite output.png

# Tiled watermark across entire image
magick input.png \
  \( watermark.png -resize 100x -alpha set -channel A -evaluate set 15% +channel \
     -write mpr:wm +delete +clone -fill mpr:wm -draw "color 0,0 reset" \) \
  -composite output.png
```

## Combine Images

```bash
# Append horizontally (side by side)
magick input1.png input2.png +append combined.png

# Append vertically (stacked)
magick input1.png input2.png -append combined.png

# Montage grid (2x2) with spacing
magick montage img1.png img2.png img3.png img4.png \
  -geometry 300x300+5+5 -tile 2x2 grid.png

# Montage with labels
magick montage img1.png img2.png img3.png img4.png \
  -label "%f" -geometry 300x300+5+5 -tile 2x grid.png

# Montage with background color
magick montage *.jpg \
  -geometry 200x200+4+4 -tile 3x -background "#f0f0f0" grid.png
```

## Color Adjustments

```bash
# Convert to grayscale
magick input.png -colorspace Gray output.png

# Adjust brightness-contrast (-100 to +100 each)
magick input.png -brightness-contrast 10x20 output.png

# Negate (invert colors)
magick input.png -negate output.png

# Sepia tone
magick input.png -sepia-tone 80% output.png

# Adjust saturation (via modulate: brightness, saturation, hue)
magick input.png -modulate 100,130,100 output.png

# Desaturate partially
magick input.png -modulate 100,50,100 output.png

# Convert colorspace (sRGB, CMYK, etc.)
magick input.png -colorspace CMYK output.tiff
magick input.tiff -colorspace sRGB output.png

# Auto-level (stretch contrast)
magick input.png -auto-level output.png

# Normalize (full range stretch)
magick input.png -normalize output.png
```

## Borders and Padding

```bash
# Add solid border
magick input.png -bordercolor "#333333" -border 10 output.png

# Add padding (extend canvas with background color)
magick input.png -gravity center -background white -extent 900x700 output.png

# Rounded corners (create mask, composite)
magick input.png \
  \( +clone -alpha extract \
     -draw "fill black polygon 0,0 0,15 15,0 fill white circle 15,15 15,0" \
     \( +clone -flip \) -compose Multiply -composite \
     \( +clone -flop \) -compose Multiply -composite \
  \) -alpha off -compose CopyOpacity -composite output.png

# Add shadow
magick input.png \
  \( +clone -background black -shadow 60x5+4+4 \) \
  +swap -background none -layers merge +repage output.png
```

## Optimize for Web

```bash
# Strip all metadata (EXIF, profiles, comments)
magick input.jpg -strip output.jpg

# Progressive JPEG
magick input.png -interlace Plane -quality 85 -strip output.jpg

# Optimized WebP from any format
magick input.png -quality 80 -define webp:method=6 -strip output.webp

# Resize + optimize in one pass
magick input.png -resize 1200x -quality 82 -strip -interlace Plane output.jpg

# Batch optimize for web
mkdir -p web
magick mogrify -path web -resize "1920x1920>" -quality 82 -strip -interlace Plane -format jpg *.png
```

## Favicon from PNG

```bash
# Create multi-size ICO favicon
magick input.png -define icon:auto-resize=256,128,64,48,32,16 favicon.ico

# Create specific size favicons
magick input.png -resize 32x32 favicon-32.png
magick input.png -resize 16x16 favicon-16.png
magick input.png -resize 180x180 apple-touch-icon.png
magick input.png -resize 192x192 android-chrome-192.png
magick input.png -resize 512x512 android-chrome-512.png
```

## PDF Operations

```bash
# PDF to images (one image per page)
magick -density 300 input.pdf output_%03d.png

# Specific page from PDF (0-indexed)
magick -density 300 "input.pdf[0]" first_page.png

# Page range
magick -density 300 "input.pdf[0-4]" page_%03d.png

# Images to PDF
magick *.jpg output.pdf

# Images to PDF with specific page size
magick *.png -resize 595x842 -gravity center -extent 595x842 output.pdf

# Compress PDF images
magick -density 150 input.pdf -quality 80 compressed.pdf
```

## Transparent Background

```bash
# Remove white background (make transparent)
magick input.png -fuzz 10% -transparent white output.png

# Remove any specific color background
magick input.png -fuzz 15% -transparent "#00ff00" output.png

# Replace transparent with a color
magick input.png -background white -alpha remove -alpha off output.png

# Flatten transparency to white
magick input.png -flatten output.jpg

# Set specific pixels transparent via flood fill from top-left corner
magick input.png -fill none -fuzz 10% -draw "alpha 0,0 floodfill" output.png

# Add transparency channel
magick input.jpg -alpha set output.png
```

## Useful Flags Reference

| Flag | Purpose |
|------|---------|
| `-strip` | Remove metadata |
| `-auto-orient` | Fix rotation from EXIF |
| `+repage` | Reset virtual canvas after crop |
| `-fuzz N%` | Color matching tolerance |
| `-gravity` | Anchor point: center, north, southeast, etc. |
| `-density N` | DPI for rasterizing vector/PDF (use before input) |
| `-depth 8` | Set bit depth |
| `-alpha set` | Enable alpha channel |
| `-alpha remove` | Flatten alpha to background |
| `-verbose` | Show processing details |
