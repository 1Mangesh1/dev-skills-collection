---
name: ffmpeg
description: FFmpeg commands for video/audio conversion, trimming, compression, and processing. Use when user mentions "ffmpeg", "convert video", "compress video", "extract audio", "trim video", "gif from video", "video codec", "transcode", "screen recording", "merge videos", "video to mp4", "reduce file size", or any media processing task.
---

# FFmpeg

## Probe and Inspect

```bash
# Show all stream info (codec, resolution, bitrate, duration)
ffprobe -v error -show_format -show_streams input.mp4

# One-line summary: duration, size, bitrate
ffprobe -v error -show_entries format=duration,size,bit_rate -of default=noprint_wrappers=1 input.mp4

# Show video resolution and frame rate
ffprobe -v error -select_streams v:0 -show_entries stream=width,height,r_frame_rate,codec_name -of csv=p=0 input.mp4

# List all supported codecs
ffmpeg -codecs

# List all supported formats
ffmpeg -formats

# List available encoders
ffmpeg -encoders
```

## Convert Between Formats

```bash
# MP4 to MKV (copy streams, no re-encode -- fast)
ffmpeg -i input.mp4 -c copy output.mkv

# MKV to MP4 (re-encode if codecs are incompatible with MP4 container)
ffmpeg -i input.mkv -c:v libx264 -c:a aac output.mp4

# AVI to MP4
ffmpeg -i input.avi -c:v libx264 -c:a aac output.mp4

# MOV to MP4 (common for iPhone footage)
ffmpeg -i input.mov -c:v libx264 -c:a aac -movflags +faststart output.mp4

# MP4 to WebM (VP9 + Opus for web)
ffmpeg -i input.mp4 -c:v libvpx-vp9 -crf 30 -b:v 0 -c:a libopus output.webm

# Any format, let FFmpeg pick codecs for the target container
ffmpeg -i input.avi output.mp4
```

## Compress Video

```bash
# CRF mode (constant quality). Lower CRF = better quality, bigger file.
# CRF 18 = visually lossless, 23 = default, 28 = smaller but visible loss.
ffmpeg -i input.mp4 -c:v libx264 -crf 23 -preset medium -c:a aac -b:a 128k output.mp4

# Faster encoding, larger file
ffmpeg -i input.mp4 -c:v libx264 -crf 23 -preset fast -c:a copy output.mp4

# Slower encoding, smaller file (use for archival)
ffmpeg -i input.mp4 -c:v libx264 -crf 23 -preset slow -c:a aac output.mp4

# H.265 for ~50% smaller files at same quality (slower to encode)
ffmpeg -i input.mp4 -c:v libx265 -crf 28 -preset medium -c:a aac output.mp4

# Target a specific file size (e.g., 25 MB for a 60s video)
# Calculate bitrate: (25 * 8192) / 60 = ~3413 kbps total. Subtract ~128 for audio.
ffmpeg -i input.mp4 -c:v libx264 -b:v 3285k -pass 1 -an -f null /dev/null && \
ffmpeg -i input.mp4 -c:v libx264 -b:v 3285k -pass 2 -c:a aac -b:a 128k output.mp4
```

## Extract Audio

```bash
# Extract audio as MP3
ffmpeg -i input.mp4 -vn -c:a libmp3lame -q:a 2 output.mp3

# Extract audio as AAC (copy if already AAC)
ffmpeg -i input.mp4 -vn -c:a copy output.aac

# Extract audio as WAV (uncompressed)
ffmpeg -i input.mp4 -vn -c:a pcm_s16le output.wav

# Extract audio as FLAC (lossless)
ffmpeg -i input.mp4 -vn -c:a flac output.flac
```

## Convert Audio Formats

```bash
# WAV to MP3 (VBR quality 2, roughly 190 kbps)
ffmpeg -i input.wav -c:a libmp3lame -q:a 2 output.mp3

# MP3 to AAC
ffmpeg -i input.mp3 -c:a aac -b:a 192k output.m4a

# FLAC to MP3
ffmpeg -i input.flac -c:a libmp3lame -q:a 0 output.mp3

# WAV to OGG Vorbis
ffmpeg -i input.wav -c:a libvorbis -q:a 5 output.ogg

# WAV to Opus (best quality-to-size ratio)
ffmpeg -i input.wav -c:a libopus -b:a 128k output.opus

# Any audio to WAV (for editing or compatibility)
ffmpeg -i input.mp3 -c:a pcm_s16le -ar 44100 output.wav
```

## Trim and Cut

```bash
# Cut from 00:01:30 to 00:03:00 without re-encoding (fast, may have keyframe issues)
ffmpeg -ss 00:01:30 -to 00:03:00 -i input.mp4 -c copy output.mp4

# Cut with re-encoding (frame-accurate)
ffmpeg -ss 00:01:30 -to 00:03:00 -i input.mp4 -c:v libx264 -c:a aac output.mp4

# Cut first 30 seconds
ffmpeg -ss 0 -t 30 -i input.mp4 -c copy output.mp4

# Cut last 30 seconds (requires knowing duration, or use negative start)
ffmpeg -sseof -30 -i input.mp4 -c copy output.mp4

# Remove first 10 seconds
ffmpeg -ss 10 -i input.mp4 -c copy output.mp4
```

## Create GIF

```bash
# Basic GIF (low quality, simple)
ffmpeg -i input.mp4 -vf "fps=10,scale=480:-1" output.gif

# High-quality GIF with palette generation (two-pass)
ffmpeg -i input.mp4 -vf "fps=15,scale=480:-1:flags=lanczos,palettegen" palette.png && \
ffmpeg -i input.mp4 -i palette.png -lavfi "fps=15,scale=480:-1:flags=lanczos [x]; [x][1:v] paletteuse" output.gif

# GIF from a specific segment (5 seconds starting at 00:00:30)
ffmpeg -ss 00:00:30 -t 5 -i input.mp4 -vf "fps=15,scale=480:-1:flags=lanczos,palettegen" palette.png && \
ffmpeg -ss 00:00:30 -t 5 -i input.mp4 -i palette.png -lavfi "fps=15,scale=480:-1:flags=lanczos [x]; [x][1:v] paletteuse" output.gif
```

## Scale and Resize

```bash
# Scale to 1280x720
ffmpeg -i input.mp4 -vf "scale=1280:720" -c:a copy output.mp4

# Scale width to 1280, keep aspect ratio (-1 auto-calculates, -2 ensures even number)
ffmpeg -i input.mp4 -vf "scale=1280:-2" -c:a copy output.mp4

# Scale to 50% of original size
ffmpeg -i input.mp4 -vf "scale=iw/2:ih/2" -c:a copy output.mp4

# Scale to fit within 1920x1080, preserving aspect ratio (no upscale)
ffmpeg -i input.mp4 -vf "scale='min(1920,iw)':'min(1080,ih)':force_original_aspect_ratio=decrease" -c:a copy output.mp4
```

## Subtitles

```bash
# Hardcode subtitles (burn into video, always visible)
ffmpeg -i input.mp4 -vf "subtitles=subs.srt" output.mp4

# Hardcode with custom style
ffmpeg -i input.mp4 -vf "subtitles=subs.srt:force_style='FontSize=24,PrimaryColour=&HFFFFFF'" output.mp4

# Soft subtitles (user can toggle on/off, MP4)
ffmpeg -i input.mp4 -i subs.srt -c copy -c:s mov_text output.mp4

# Soft subtitles (MKV, supports more formats including ASS)
ffmpeg -i input.mp4 -i subs.srt -c copy -c:s srt output.mkv

# Extract subtitles from video
ffmpeg -i input.mkv -map 0:s:0 output.srt
```

## Merge and Concatenate

```bash
# Concatenate videos (same codec, resolution, framerate)
# First create a file list:
# file 'part1.mp4'
# file 'part2.mp4'
# file 'part3.mp4'
ffmpeg -f concat -safe 0 -i filelist.txt -c copy output.mp4

# Generate the file list from shell
for f in part*.mp4; do echo "file '$f'"; done > filelist.txt
ffmpeg -f concat -safe 0 -i filelist.txt -c copy output.mp4

# Concatenate with re-encoding (when formats differ)
ffmpeg -f concat -safe 0 -i filelist.txt -c:v libx264 -c:a aac output.mp4

# Combine video and audio from separate files
ffmpeg -i video.mp4 -i audio.mp3 -c:v copy -c:a aac -shortest output.mp4

# Replace audio track in a video
ffmpeg -i video.mp4 -i newaudio.mp3 -c:v copy -c:a aac -map 0:v:0 -map 1:a:0 output.mp4
```

## Extract Frames

```bash
# Extract one frame at a specific timestamp
ffmpeg -ss 00:01:30 -i input.mp4 -frames:v 1 frame.png

# Extract one frame every second
ffmpeg -i input.mp4 -vf "fps=1" frames_%04d.png

# Extract one frame every 10 seconds
ffmpeg -i input.mp4 -vf "fps=1/10" frames_%04d.png

# Extract all frames (warning: generates many files)
ffmpeg -i input.mp4 frames_%06d.png

# Create a thumbnail sheet (4x4 grid)
ffmpeg -i input.mp4 -vf "select='not(mod(n\,100))',scale=320:180,tile=4x4" -frames:v 1 thumbnails.png
```

## Screen Recording

```bash
# macOS -- record full screen
ffmpeg -f avfoundation -framerate 30 -i "1:0" -c:v libx264 -preset ultrafast -crf 18 output.mp4

# macOS -- list available devices
ffmpeg -f avfoundation -list_devices true -i ""

# macOS -- record screen with audio
ffmpeg -f avfoundation -framerate 30 -i "1:0" -c:v libx264 -preset ultrafast -c:a aac output.mp4

# Linux (X11) -- record full screen
ffmpeg -f x11grab -framerate 30 -video_size 1920x1080 -i :0.0 -c:v libx264 -preset ultrafast -crf 18 output.mp4

# Linux (X11) -- record a region (offset x=100,y=200, size 1280x720)
ffmpeg -f x11grab -framerate 30 -video_size 1280x720 -i :0.0+100,200 -c:v libx264 -preset ultrafast output.mp4

# Linux (PipeWire/Wayland) -- use pipewire screen capture
# Wayland does not support x11grab. Use pw-record or OBS with pipewire.
```

## Speed Up and Slow Down

```bash
# Speed up video 2x (drop audio)
ffmpeg -i input.mp4 -vf "setpts=0.5*PTS" -an output.mp4

# Speed up video 2x and audio 2x
ffmpeg -i input.mp4 -vf "setpts=0.5*PTS" -af "atempo=2.0" output.mp4

# Slow down video 2x with audio
ffmpeg -i input.mp4 -vf "setpts=2.0*PTS" -af "atempo=0.5" output.mp4

# Speed up 4x (chain atempo filters; each atempo supports 0.5-2.0 range)
ffmpeg -i input.mp4 -vf "setpts=0.25*PTS" -af "atempo=2.0,atempo=2.0" output.mp4
```

## Remove Audio

```bash
# Strip audio track, keep video as-is
ffmpeg -i input.mp4 -an -c:v copy output.mp4
```

## Codec Reference

| Codec   | Use Case                                   | Encode Flag      | Notes                                    |
|---------|--------------------------------------------|------------------|------------------------------------------|
| H.264   | General purpose, widest compatibility      | `-c:v libx264`   | Default choice. Works everywhere.        |
| H.265   | Archival, streaming, 4K content            | `-c:v libx265`   | ~50% smaller than H.264. Slower encode.  |
| VP9     | Web delivery, YouTube-style hosting        | `-c:v libvpx-vp9` | Royalty-free. Good browser support.      |
| AV1     | Next-gen web/streaming (emerging)          | `-c:v libaom-av1` | Best compression. Very slow to encode.   |
| AAC     | Audio in MP4 containers                    | `-c:a aac`       | Good quality, universal support.         |
| Opus    | Voice, music, streaming at low bitrates    | `-c:a libopus`   | Best quality-per-bit. WebM/OGG container.|
| MP3     | Legacy audio compatibility                 | `-c:a libmp3lame` | Use when AAC/Opus not accepted.         |

**Quick decision guide:**
- Sharing on the web or need broad playback? H.264 + AAC in MP4.
- Need smaller files and can wait longer to encode? H.265.
- Targeting browsers specifically? VP9 + Opus in WebM.
- Archiving and storage is a concern? H.265 or AV1.

## Useful Flags

```
-y                  Overwrite output without asking
-n                  Never overwrite output
-hide_banner        Suppress FFmpeg build info
-v error            Only show errors (quieter output)
-movflags +faststart  Move MP4 metadata to beginning (better for streaming)
-map 0              Copy all streams from input
-shortest           Stop encoding when the shortest stream ends
-threads 0          Use all available CPU threads
```
