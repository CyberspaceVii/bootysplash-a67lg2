# Bootysplash

**[Download bootysplash-a67lg2.zip — v0.6](https://github.com/CyberspaceVii/bootysplash-a67lg2/releases/download/v0.6/bootysplash-a67lg2.zip)**

Matching power-on logo, boot animation and faded Lords of Acid music for the Foxxd A67L Gen 2.

A KernelSU Next module for the **Foxxd A67L Gen 2**. Gen 1 version: [bootysplash-a67lg1](https://github.com/CyberspaceVii/bootysplash-a67lg1).

**[Watch the preview with music](https://github.com/CyberspaceVii/bootysplash-a67lg2/releases/download/v0.6/bootysplash-preview.mp4)**

The animation plays **backward → forward → drop**, with the drop at 85% speed,
a 1.5-second fade to black and a short black hold. Total: **21.67 seconds at
24 fps**. The reversal has no repeated endpoint, and four overlay frames smooth
the matched transition into the drop at 13.25 seconds.

The picture fills a 720×1280 **9:16** crop, centered on the phone's 720×1600
display with 160 black pixels above and below. The supplied initial still uses
the same crop and position. Its stock-format 255-color BMP matches the first
animation frame exactly, followed by a short blend into the reverse-motion pose.

The full animation plays before the boot screen closes, even when Android is
ready early. Black holds for slower boots. This uses Android's
[play-to-completion animation format](https://android.googlesource.com/platform/frameworks/base/+/refs/heads/main/cmds/bootanimation/FORMAT.md);
it does not delay Android's internal boot-completed property.

The Lords of Acid excerpt runs from source 37.50–56.54 seconds, placing the
50–51-second vocal cue at the drop. It is reduced by 6 dB, with a half-second
fade-in and two-second fade-out. Music ends before the animation does. Original
clip audio is excluded, and no persistent volume setting is changed.

## Requirements

- Foxxd A67L Gen 2
- Rooted with KernelSU Next

The installer stops without changing anything if either is missing.

## Install

1. Download [`bootysplash-a67lg2.zip`](https://github.com/CyberspaceVii/bootysplash-a67lg2/releases/latest/download/bootysplash-a67lg2.zip).
2. KernelSU Next → Modules → Install from storage → select the zip.
3. Reboot.

## Uninstall

Remove the module in KernelSU Next and reboot.

The boot animation and sound are systemless. The power-on logo isn't: the bootloader reads it straight
from the `logo` and `fbootlogo` partitions. So the installer backs up the originals to
`/data/adb/cyberspacevii/bootysplash-a67lg2/` before writing, and uninstalling writes them back.

## Rebuild the media

With ffmpeg installed, create a Python virtual environment with Pillow. Use the
approved 720×1280, 24 fps video with its synchronized audio, the original still,
and the finished MP3 soundtrack:

```sh
python tools/build_media.py --video /path/to/approved-preview.mp4 \
  --still /path/to/initialass.png --sound /path/to/finished-bootsound.mp3 \
  --out /tmp/bootysplash-build
python tools/package.py --out /tmp/bootysplash-build
```

The media builder updates the checkout's three runtime assets and creates a
preview from the actual packaged frames. The package builder creates the
installable ZIP and release SHA256SUMS. Keep the input media available for
rebuilding; the full original music source is not included in this checkout.

Host checks cover all 520 frame decodes, archive integrity, stock BMP layout,
exact still/first-frame pixels, black ending, soundtrack identity and release
hashes. **v0.6 has not been boot-tested on the phone**; actual speaker loudness
and vendor playback timing remain unverified.

## License

[WTFPL](LICENSE).

---

CyberspaceVII · https://www.cyberspace7.org
