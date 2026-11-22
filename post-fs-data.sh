#!/system/bin/sh
MODDIR=${0%/*}
umask 077
logdir=/data/adb/cyberspacevii/bootysplash-a67lg2
mkdir -p "$logdir"
CLASSPATH="$MODDIR/boot-audio-volume.jar" /system/bin/app_process /system/bin BootMusicVolume >"$logdir/boot-audio-volume.log" 2>&1 &
