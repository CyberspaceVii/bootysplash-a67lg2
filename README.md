# Bootysplash

**[Download bootysplash-a67lg2.zip — v0.6](https://github.com/CyberspaceVii/bootysplash-a67lg2/releases/download/v0.6/bootysplash-a67lg2.zip)**

Custom power-on logo, boot animation and Lords of Acid boot music for the
**Foxxd A67L Gen 2**, using KernelSU Next.

Gen 1 version: [bootysplash-a67lg1](https://github.com/CyberspaceVii/bootysplash-a67lg1).

**[Watch the preview with music](https://github.com/CyberspaceVii/bootysplash-a67lg2/releases/download/v0.6/bootysplash-preview.mp4)**

The animation plays backward, forward, then drops and fades to black. Music
fades in and out at a moderate level. The full animation plays before the boot
screen closes.

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

v0.6 has not yet been boot-tested on the phone.

## License

[WTFPL](LICENSE).

---

CyberspaceVII · https://www.cyberspace7.org
