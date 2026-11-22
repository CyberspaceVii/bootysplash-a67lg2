#!/usr/bin/env bash
set -euo pipefail
module_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
sdk_dir="${ANDROID_HOME:?Set ANDROID_HOME to an Android SDK with platform36 and build-tools36.0.0}"
classes_dir="$(mktemp -d)"
trap 'rm -rf -- "$classes_dir"' EXIT
"${JAVA_HOME:+$JAVA_HOME/bin/}javac" --release 17 \
  -classpath "$sdk_dir/platforms/android-36/android.jar" \
  -d "$classes_dir" "$module_dir/tools/BootMusicVolume.java"
"$sdk_dir/build-tools/36.0.0/d8" \
  --lib "$sdk_dir/platforms/android-36/android.jar" \
  --output "$module_dir/boot-audio-volume.jar" "$classes_dir/BootMusicVolume.class"
