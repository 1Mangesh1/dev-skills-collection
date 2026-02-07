# Image Optimization Strategies

## Image Format Selection

### JPEG
- Best for: Photos, complex images
- Compression: Lossy
- Size: Medium
- Browser support: Universal

```html
<picture>
  <source type="image/webp" srcset="photo.webp">
  <source type="image/jpeg" srcset="photo.jpg">
  <img src="photo.jpg" alt="Photo">
</picture>
```

### WebP
- Best for: All images (modern format)
- Compression: Lossy + Lossless
- Size: 25-35% smaller than JPEG
- Browser support: 96% (graceful fallback needed)

### PNG
- Best for: Graphics, logos with transparency
- Compression: Lossless
- Size: Larger than JPEG
- Browser support: Universal

### SVG
- Best for: Icons, logos, simple graphics
- Compression: Vector-based
- Size: Very small
- Scalable: Perfect for all screen sizes

## Optimization Checklist

1. **Right Format**
   - Photo → WebP/JPEG
   - Icon → SVG
   - Transparent → PNG/WebP

2. **Compression**
   ```bash
   # Optimize PNG
   pngquant image.png --output image-optimized.png
   
   # Optimize JPEG
   jpegoptim --max=85 image.jpg
   
   # Convert to WebP
   cwebp image.jpg -o image.webp
   ```

3. **Responsive Images**
   ```html
   <img 
     srcset="
       small.jpg 480w,
       medium.jpg 1024w,
       large.jpg 1920w"
     sizes="(max-width: 480px) 100vw,
            (max-width: 1024px) 80vw,
            1200px"
     src="large.jpg"
     alt="Description"
   >
   ```

4. **Lazy Loading**
   ```html
   <!-- Browser-native lazy loading -->
   <img src="image.jpg" loading="lazy" alt="Description">
   ```

5. **CDN Delivery**
   - Use CDN for image distribution
   - Cloudflare, Cloudinary, AWS CloudFront
   - Automatic optimization available

## Tools

- **ImageOptim** - macOS GUI
- **Squoosh** - Online converter  
- **Sharp** - Node.js library
- **ImageMagick** - Command-line tool
- **Cloudinary** - Cloud service with optimization

## Size Targets

| Type | Size Target |
|------|-------------|
| Hero Image | < 300KB |
| Gallery Image | < 150KB |
| Thumbnail | < 50KB |
| Icon | < 20KB |
