---
name: tar-compression
description: Archive and compression commands — tar, gzip, zip, and friends. Use when user mentions "tar", "gzip", "zip", "unzip", "compress", "extract", "archive", "bzip2", "xz", "7z", ".tar.gz", ".tgz", "untar", or working with compressed files.
---

# tar and compression

## tar basics

Create an archive:

```bash
tar -cvf archive.tar dir/          # create .tar (no compression)
tar -czvf archive.tar.gz dir/      # create .tar.gz (gzip)
tar -cjvf archive.tar.bz2 dir/     # create .tar.bz2 (bzip2)
tar -cJvf archive.tar.xz dir/      # create .tar.xz (xz)
```

Extract an archive:

```bash
tar -xvf archive.tar               # extract .tar
tar -xzvf archive.tar.gz           # extract .tar.gz
tar -xjvf archive.tar.bz2          # extract .tar.bz2
tar -xJvf archive.tar.xz           # extract .tar.xz
```

Modern tar auto-detects compression on extraction, so `tar -xvf archive.tar.gz` works without `-z`. Specifying the flag is still common for clarity.

## The flags

| Flag | Meaning |
|------|---------|
| `-c` | Create archive |
| `-x` | Extract archive |
| `-t` | List contents (don't extract) |
| `-v` | Verbose (show files) |
| `-f` | Next argument is the filename -- must come last before the filename |
| `-z` | gzip compression |
| `-j` | bzip2 compression |
| `-J` | xz compression |
| `-C` | Change to directory before operating |
| `-p` | Preserve permissions |

`-f` must be the last flag before the archive name. `tar -cvf archive.tar` works; `tar -cfv archive.tar` does not -- tar would look for a file named `v`.

## List archive contents without extracting

```bash
tar -tzvf archive.tar.gz                    # list all files
tar -tzvf archive.tar.gz | grep pattern     # find specific files
```

## Extract specific files

```bash
tar -xzvf archive.tar.gz path/to/file.txt   # extract one file
tar -xzvf archive.tar.gz --wildcards '*.conf'  # extract by pattern (GNU tar)
```

## Extract to a specific directory

```bash
tar -xzvf archive.tar.gz -C /target/dir/
```

## Exclude files when creating

```bash
tar -czvf archive.tar.gz dir/ --exclude='*.log' --exclude='.git'
tar -czvf archive.tar.gz dir/ --exclude-vcs   # skip .git, .svn, etc.
tar -czvf archive.tar.gz dir/ -X exclude.txt  # patterns from file
```

## gzip / gunzip (single files)

```bash
gzip file.txt              # compresses to file.txt.gz, removes original
gzip -k file.txt           # keep original
gunzip file.txt.gz         # decompress
gzip -d file.txt.gz        # same as gunzip
gzip -9 file.txt           # max compression (1=fast, 9=best)
gzip -l file.txt.gz        # show compression ratio
```

gzip works on single files only. For directories, use tar + gzip.

## zip / unzip

Create:

```bash
zip archive.zip file1 file2
zip -r archive.zip dir/                 # recursive (directories)
zip -r archive.zip dir/ -x '*.log'     # exclude pattern
zip -e archive.zip file1               # encrypt with password
```

Add to existing archive:

```bash
zip archive.zip newfile.txt            # appends to existing zip
zip -u archive.zip updated-file.txt   # update only changed files
```

Extract:

```bash
unzip archive.zip                      # extract to current dir
unzip archive.zip -d /target/dir/      # extract to specific dir
unzip archive.zip file.txt             # extract one file
```

List contents:

```bash
unzip -l archive.zip                   # list files and sizes
zipinfo archive.zip                    # detailed info
```

## Compression comparison

| Tool  | Flag | Ext       | Speed     | Ratio  | Notes |
|-------|------|-----------|-----------|--------|-------|
| gzip  | `-z` | .tar.gz   | Fast      | Good   | Everywhere, default choice |
| bzip2 | `-j` | .tar.bz2  | Slow      | Better | Rarely worth the time |
| xz    | `-J` | .tar.xz   | Very slow | Best   | Source tarballs, max compression |
| zstd  | `--zstd` | .tar.zst | Very fast | Better | Best speed/ratio tradeoff |

Rule of thumb:
- Quick backup or transfer: gzip or zstd
- Distributing source code: xz
- General purpose modern: zstd
- bzip2: legacy, rarely the right choice today

## zstd (modern compression)

```bash
tar --zstd -cvf archive.tar.zst dir/       # create
tar --zstd -xvf archive.tar.zst            # extract (or just tar -xvf)

zstd file.txt                              # compress single file -> file.txt.zst
zstd -d file.txt.zst                       # decompress
zstd -19 file.txt                          # max compression (1-19, default 3)
zstd --fast file.txt                       # speed over ratio
zstd -T0 file.txt                          # use all CPU cores
```

zstd is typically 3-5x faster than gzip at similar or better compression ratios.

## Split large archives

```bash
# Create a split archive (100MB chunks)
tar -czvf - dir/ | split -b 100m - archive.tar.gz.part-

# Reassemble and extract
cat archive.tar.gz.part-* | tar -xzvf -

# Or with zip
zip -r -s 100m archive.zip dir/           # split zip
```

## tar over SSH

```bash
# Copy directory to remote machine
tar -czvf - dir/ | ssh user@host 'tar -xzvf - -C /target/'

# Copy from remote to local
ssh user@host 'tar -czvf - /remote/dir/' | tar -xzvf - -C /local/dir/

# With progress (requires pv)
tar -cf - dir/ | pv | ssh user@host 'tar -xf - -C /target/'
```

## Common patterns

Backup a directory with date stamp:

```bash
tar -czvf "backup-$(date +%Y%m%d).tar.gz" /path/to/dir/
```

Compress all log files older than 7 days:

```bash
find /var/log -name '*.log' -mtime +7 -exec gzip {} \;
```

Extract and strip the top-level directory:

```bash
tar -xzvf archive.tar.gz --strip-components=1
```

Dry run -- see what would be extracted:

```bash
tar -tzvf archive.tar.gz | head -20
```

Create archive preserving permissions and symlinks:

```bash
tar -cpzvf archive.tar.gz --preserve-permissions dir/
```

Compare archive to filesystem (check what changed):

```bash
tar -dvf archive.tar dir/
```
