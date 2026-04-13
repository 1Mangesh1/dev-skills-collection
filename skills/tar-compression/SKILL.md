---
name: tar-compression
description: Archive and compression commands — tar, gzip, zip, zstd, xz, bzip2, 7z, and friends. Use when user mentions "tar", "gzip", "zip", "unzip", "compress", "extract", "archive", "bzip2", "xz", "zstd", "7z", "7zip", "rar", "pigz", "pbzip2", ".tar.gz", ".tgz", ".tar.xz", ".tar.zst", ".tar.bz2", "untar", "decompress", "incremental backup", "split archive", "parallel compression", "disk image", "dd", or working with compressed files.
---

# tar and compression

## tar basics — create, extract, list

```bash
tar -cvf archive.tar dir/              # create .tar (no compression)
tar -czvf archive.tar.gz dir/          # create .tar.gz (gzip)
tar -cjvf archive.tar.bz2 dir/        # create .tar.bz2 (bzip2)
tar -cJvf archive.tar.xz dir/         # create .tar.xz (xz)
tar --zstd -cvf archive.tar.zst dir/  # create .tar.zst (zstd)
```

```bash
tar -xvf archive.tar               # extract (auto-detects compression)
tar -xzvf archive.tar.gz           # explicit gzip
tar -xjvf archive.tar.bz2          # explicit bzip2
tar -xJvf archive.tar.xz           # explicit xz
```

Modern tar auto-detects compression on extraction, so `tar -xvf` works for all formats.

## tar flags reference

| Flag | Meaning |
|------|---------|
| `-c` | Create archive |
| `-x` | Extract archive |
| `-t` | List contents (don't extract) |
| `-r` | Append files to existing archive (uncompressed .tar only) |
| `-u` | Update — append only files newer than what's in archive |
| `-v` | Verbose (show files) |
| `-f` | Next argument is the filename — must come last before the filename |
| `-z` | gzip compression |
| `-j` | bzip2 compression |
| `-J` | xz compression |
| `--zstd` | zstd compression |
| `-C` | Change to directory before operating |
| `-p` | Preserve permissions |
| `-h` | Follow symlinks (archive the target, not the link) |

`-f` must be the last flag before the archive name. `tar -cfv archive.tar` fails — tar looks for a file named `v`.

## Append, update, exclude

```bash
tar -rvf archive.tar newfile.txt           # append (uncompressed .tar only)
tar -uvf archive.tar dir/                  # update only newer files

tar -czvf archive.tar.gz dir/ --exclude='*.log' --exclude='.git'
tar -czvf archive.tar.gz dir/ --exclude-vcs          # skip .git, .svn, .hg
tar -czvf archive.tar.gz dir/ --exclude-vcs-ignores   # also honor .gitignore
tar -czvf archive.tar.gz dir/ -X exclude.txt          # patterns from file
```

## Archive inspection and partial extraction

```bash
# Inspect without extracting
tar -tzvf archive.tar.gz                       # list all files with sizes
tar -tzvf archive.tar.gz | grep pattern        # find specific files
tar -tzvf archive.tar.gz --wildcards '*.conf'  # list matching files (GNU tar)

# Extract specific files or directories
tar -xzvf archive.tar.gz path/to/file.txt      # extract one file
tar -xzvf archive.tar.gz dir/subdir/           # extract one directory
tar -xzvf archive.tar.gz --wildcards '*.conf'  # extract by pattern (GNU tar)
tar -xzvf archive.tar.gz -C /target/dir/       # extract to specific directory
tar -xzvf archive.tar.gz --strip-components=1  # strip top-level directory
```

## Preserving permissions, ownership, symlinks

```bash
# Full preservation (system backups, run as root)
tar -cpzvf archive.tar.gz --same-owner dir/

# Follow symlinks instead of storing links
tar -chzvf archive.tar.gz dir/

# Restore with ownership (requires root)
tar -xpzvf archive.tar.gz --same-owner -C /restore/

# Compare archive to filesystem (check what changed)
tar -dvf archive.tar dir/
```

On macOS, `--same-owner` is default for root. On GNU/Linux, specify it explicitly.

## Compression algorithms compared

| Tool  | Flag | Ext       | Speed     | Ratio  | Parallel tool |
|-------|------|-----------|-----------|--------|---------------|
| gzip  | `-z` | .tar.gz   | Fast      | Good   | pigz          |
| bzip2 | `-j` | .tar.bz2  | Slow      | Better | pbzip2        |
| xz    | `-J` | .tar.xz   | Very slow | Best   | pxz / pixz    |
| zstd  | `--zstd` | .tar.zst | Very fast | Better | built-in `-T` |
| lz4   | `--use-compress-program=lz4` | .tar.lz4 | Fastest | Lower | built-in |

Rough benchmarks (1 GB mixed data, single core):

| Tool    | Compress | Decompress | Compressed size |
|---------|----------|------------|-----------------|
| lz4     | ~2s      | ~0.5s      | ~55% of original |
| zstd -1 | ~3s      | ~1s        | ~42% |
| gzip -6 | ~12s     | ~3s        | ~36% |
| zstd -19| ~90s     | ~1s        | ~30% |
| xz -6   | ~120s    | ~8s        | ~28% |

Rule of thumb: quick backup → gzip/zstd. Source distribution → xz. General purpose → zstd. Real-time → lz4. bzip2 → legacy, skip it.

## gzip / gunzip

```bash
gzip file.txt              # compress to file.txt.gz, removes original
gzip -k file.txt           # keep original
gunzip file.txt.gz         # decompress
gzip -9 file.txt           # max compression (1=fast, 9=best)
gzip -l file.txt.gz        # show compression ratio
zcat file.txt.gz           # decompress to stdout
```

## zstd (modern compression)

```bash
zstd file.txt                  # compress -> file.txt.zst (default level 3)
zstd -d file.txt.zst           # decompress
zstd -19 file.txt              # max standard compression (1-19)
zstd --ultra -22 file.txt      # ultra mode (20-22, needs --ultra)
zstd --fast file.txt           # speed over ratio
zstd -T0 file.txt              # use all CPU cores
zstd --long file.txt           # larger window for better ratio on large files
```

### Dictionary compression (many small similar files)

```bash
zstd --train samples/* -o mydict.zst          # train from samples
zstd -D mydict.zst file.txt -o file.txt.zst   # compress with dictionary
zstd -d -D mydict.zst file.txt.zst             # decompress with dictionary
```

Improves ratio 2-5x on small, structurally similar files (logs, JSON, configs).

### Streaming

```bash
mysqldump mydb | zstd -T0 > dump.sql.zst
zstd -d < dump.sql.zst | mysql mydb
tar -cf - dir/ | pv | zstd -T0 > archive.tar.zst
```

## Parallel compression (pigz, pbzip2, pxz)

```bash
# pigz — parallel gzip (drop-in replacement)
tar -cf - dir/ | pigz -p 8 > archive.tar.gz
pigz -d archive.tar.gz

# pbzip2 — parallel bzip2
tar -cf - dir/ | pbzip2 -p8 > archive.tar.bz2

# pxz — parallel xz
tar -cf - dir/ | pxz -T 8 > archive.tar.xz

# tar integration via --use-compress-program
tar -cf archive.tar.gz --use-compress-program='pigz -9' dir/
tar -xf archive.tar.gz --use-compress-program='pigz -d' -C /target/
```

## zip / unzip

```bash
zip archive.zip file1 file2             # create
zip -r archive.zip dir/                 # recursive (directories)
zip -r archive.zip dir/ -x '*.log'     # exclude pattern

unzip archive.zip                       # extract to current dir
unzip archive.zip -d /target/dir/       # extract to specific dir
unzip archive.zip file.txt              # extract one file
unzip -o archive.zip                    # overwrite without prompting
unzip -l archive.zip                    # list files and sizes
zipinfo archive.zip                     # detailed info
zip -u archive.zip updated-file.txt    # update changed files in archive
```

### Password-protected zip

```bash
zip -e archive.zip file1 file2         # prompt for password
unzip -P 'mypass' archive.zip          # extract with password
```

zip's encryption (ZipCrypto) is weak. Use 7z with AES-256 for real security.

### Split zip archives

```bash
zip -r -s 100m archive.zip dir/        # split at 100MB chunks
zip -s 0 archive.zip --out combined.zip # merge splits before extracting
unzip combined.zip
```

## 7z operations (p7zip / 7-Zip)

```bash
7z a archive.7z dir/                        # create .7z
7z a archive.7z dir/ -mx=9                  # ultra compression
7z a archive.7z dir/ -ms=on                 # solid mode (better compression)
7z a archive.7z dir/ -p'Pass' -mhe=on       # AES-256 encrypt contents + filenames
7z a -v100m archive.7z dir/                 # split into 100MB volumes

7z x archive.7z                             # extract preserving structure
7z e archive.7z                             # extract flat (no dirs)
7z x archive.7z -o/target/dir/              # extract to directory
7z l archive.7z                             # list contents
7z t archive.7z                             # test integrity
```

7z reads/writes: .7z, .zip, .tar, .gz, .bz2, .xz. Extracts .rar.

## Piping tar over SSH

```bash
# Local to remote
tar -czvf - dir/ | ssh user@host 'tar -xzvf - -C /target/'

# Remote to local
ssh user@host 'tar -czvf - /remote/dir/' | tar -xzvf - -C /local/dir/

# With zstd for faster transfer
tar -cf - dir/ | zstd -T0 | ssh user@host 'zstd -d | tar -xf - -C /target/'

# With progress and bandwidth limit
tar -cf - dir/ | pv -L 10m | ssh user@host 'tar -xf - -C /target/'
```

## Incremental backups with tar

```bash
# Level 0: full backup (creates snapshot file)
tar -czvf backup-full.tar.gz \
    --listed-incremental=/var/backups/snapshot.snar dir/

# Level 1: incremental (only changes since last backup)
tar -czvf backup-inc-$(date +%Y%m%d).tar.gz \
    --listed-incremental=/var/backups/snapshot.snar dir/

# Restore: apply full, then each incremental in order
tar -xzvf backup-full.tar.gz -C /restore/ --listed-incremental=/dev/null
tar -xzvf backup-inc-20260410.tar.gz -C /restore/ --listed-incremental=/dev/null
```

`--listed-incremental=/dev/null` during restore tells tar to extract everything. GNU tar only.

## Split large archives

```bash
tar -czvf - dir/ | split -b 100m - archive.tar.gz.part-
cat archive.tar.gz.part-* | tar -xzvf -
```

## Cross-platform: macOS vs GNU tar

| Feature | GNU tar (Linux) | BSD tar (macOS) |
|---------|----------------|-----------------|
| `--wildcards` | Required for patterns | Default behavior |
| `--exclude-vcs-ignores` | Supported | Not supported |
| `--zstd` | Supported | Use `--use-compress-program` |
| `--listed-incremental` | Supported | Not supported |
| Extended attributes | `--xattrs` | Stored by default |

```bash
# macOS: install GNU tar for full feature set
brew install gnu-tar    # use as 'gtar'

# macOS: zstd with BSD tar
tar -cf - dir/ | zstd > archive.tar.zst

# macOS: avoid resource fork ._* files
COPYFILE_DISABLE=1 tar -czvf archive.tar.gz dir/
```

## Compression for specific use cases

```bash
# Logs (repetitive text, compresses 90%+)
gzip -9 app.log
find /var/log -name '*.log' -mtime +7 -exec gzip {} \;
zstd --train logs/*.log -o log-dict.zst && zstd -D log-dict.zst -19 app.log

# Database dumps
mysqldump mydb | zstd -T0 > mydb.sql.zst
pg_dump mydb | gzip -9 > mydb.sql.gz
pg_dump -Fc mydb > mydb.dump              # pg custom format (built-in compression)

# Source code distribution
tar -cJvf project.tar.xz --exclude-vcs project/
git archive --format=tar.gz HEAD > project.tar.gz

# Disk images
dd if=/dev/sda bs=4M status=progress | zstd -T0 > disk.img.zst
zstd -d < disk.img.zst | dd of=/dev/sda bs=4M status=progress
qemu-img convert -c -O qcow2 disk.raw disk.qcow2
```

## Common patterns

```bash
# Backup with timestamp
tar -czvf "backup-$(date +%Y%m%d-%H%M%S).tar.gz" /path/to/dir/

# Dry run — see what would be extracted
tar -tzvf archive.tar.gz | head -20

# Find largest files in archive
tar -tzvf archive.tar.gz | sort -k3 -n -r | head -20

# Create archive from file list
tar -czvf archive.tar.gz -T filelist.txt

# Create archive excluding large files
find dir/ -size -10M | tar -czvf small-files.tar.gz -T -

# Verify archive integrity
gzip -t archive.tar.gz && echo "OK" || echo "CORRUPT"
xz -t archive.tar.xz
zstd -t archive.tar.zst
```
