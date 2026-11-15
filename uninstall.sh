#!/system/bin/sh
BK=/data/adb/cyberspacevii/bootysplash-a67lg2
ok=1
for p in logo fbootlogo; do
  [ -s "$BK/$p.img" ] || continue
  dd if="$BK/$p.img" of="/dev/block/by-name/$p" bs=1M conv=fsync 2>/dev/null || ok=0
done
[ "$ok" = 1 ] && rm -rf "$BK" && rmdir /data/adb/cyberspacevii 2>/dev/null
