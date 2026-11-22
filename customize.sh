#!/system/bin/sh
ui_print "Bootysplash CyberspaceVII"
ui_print " "

[ "$(getprop ro.product.device)" = A67L_Gen2 ] || abort "Fail! This module is for the Foxxd A67L Gen 2."
[ "$KSU" = true ] || abort "Fail! KernelSU Next is required."


grep -q 'lcd_size=1600x720' /proc/cmdline || abort "Fail! Unsupported display."

current=$(sha256sum /system_ext/lib64/libunisocbootanimation.so | cut -d' ' -f1)
case "$current" in
  39322942066577aa56d7119dbd7bfbd0f07e0e5c7965b42be33b8c23905f6a5b|7dc2c9f55fb466b05a50b6c4c098052a4a8187379699be577f6dc3606c28a47f) ;;
  *) abort "Fail! Boot audio fix requires supported stock firmware (1790133188)." ;;
esac
set_perm "$MODPATH/system/system_ext/lib64/libunisocbootanimation.so" 0 0 0644
set_perm "$MODPATH/boot-audio-volume.jar" 0 0 0644
set_perm "$MODPATH/post-fs-data.sh" 0 0 0755

ui_print "Installing matching boot logo, animation and faded music..."
ui_print "The complete animation plays before leaving the boot screen."

BMP="$MODPATH/logo.bmp"
BK=/data/adb/cyberspacevii/bootysplash-a67lg2
[ -f "$BMP" ] || abort "Fail! logo.bmp missing."
SZ=$(stat -c %s "$BMP")
want=$(sha256sum "$BMP" | cut -d' ' -f1)
mkdir -p "$BK"

ok=1
for p in logo fbootlogo; do
  dev=/dev/block/by-name/$p
  [ -b "$dev" ] || { ok=0; continue; }
  [ "$(blockdev --getsize64 "$dev")" -ge "$SZ" ] || { ok=0; continue; }
  if [ ! -s "$BK/$p.img" ]; then
    dd if="$dev" of="$BK/$p.img" bs=1M 2>/dev/null || abort "Fail! Could not back up $p."
  fi
  dd if="$BMP" of="$dev" bs=4096 conv=fsync,notrunc 2>/dev/null
  [ "$(head -c "$SZ" "$dev" | sha256sum | cut -d' ' -f1)" = "$want" ] || ok=0
done
rm -f "$BMP"

[ "$ok" = 1 ] && ui_print "Success!" || ui_print "Fail!"
