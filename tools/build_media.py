#!/usr/bin/env python3
"""Package an approved 9:16 render, initial still and finished boot soundtrack.

Requires ffmpeg/ffprobe and Pillow in a Python virtual environment. Input video
is 720x1280, 24 fps, with the final music already synchronized. The finished
MP3 is installed unchanged; no audio.wav is placed inside bootanimation.zip.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path
import shutil
import struct
import subprocess
import tempfile
import zipfile

from PIL import Image

MODULE = Path(__file__).resolve().parents[1]
W, H, CONTENT_H, OFFSET_Y, FPS = 720, 1600, 1280, 160, 24


def run(*args):
    subprocess.run([str(x) for x in args], check=True)


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def probe(path):
    return json.loads(subprocess.check_output([
        'ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(path)]))


def bitmap(canvas):
    quantized = canvas.quantize(colors=255, method=Image.Quantize.MEDIANCUT,
                                dither=Image.Dither.FLOYDSTEINBERG)
    palette = quantized.getpalette()[:765]
    pixels = b''.join(quantized.crop((0, y, W, y+1)).tobytes()
                      for y in range(H-1, -1, -1)) + b'\0\0'
    offset = 14+40+255*4
    header = struct.pack('<2sIHHI', b'BM', offset+len(pixels), 0, 0, offset)
    dib = struct.pack('<IiiHHIIiiII', 40, W, H, 1, 8, 0, len(pixels), 2834, 2834, 255, 255)
    colors = b''.join(bytes((palette[i+2], palette[i+1], palette[i], 0)) for i in range(0,765,3))
    return header+dib+colors+pixels, quantized.convert('RGB')


def encoded(image, quality=None):
    stream = io.BytesIO()
    if quality is None:
        image.save(stream, 'PNG')
    else:
        image.save(stream, 'JPEG', quality=quality, subsampling=0, optimize=True)
    return stream.getvalue()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ['video', 'still', 'sound', 'out']:
        parser.add_argument('--'+name, type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    streams = probe(args.video)['streams']
    video = next(s for s in streams if s['codec_type']=='video')
    if (video['width'], video['height'], video['r_frame_rate']) != (W, CONTENT_H, '24/1'):
        raise ValueError('Expected approved 720x1280, 24 fps render')
    count = int(video['nb_frames'])
    duration = count/FPS
    if float(probe(args.sound)['format']['duration']) >= duration-.75:
        raise ValueError('Boot sound needs to finish before animation teardown')
    archive = args.out/'bootanimation.zip'
    with tempfile.TemporaryDirectory(prefix='bootysplash-media-') as tmp:
        tmp = Path(tmp)
        run('ffmpeg', '-v', 'error', '-i', args.video, '-map', '0:v:0',
            '-vf', f'pad={W}:{H}:0:{OFFSET_Y}:black', '-fps_mode', 'passthrough', tmp/'%04d.png')
        run('ffmpeg', '-v', 'error', '-i', args.still, '-frames:v', '1', '-vf',
            f'scale={W}:{CONTENT_H}:flags=lanczos:force_original_aspect_ratio=increase,'
            f'crop={W}:{CONTENT_H},setsar=1,pad={W}:{H}:0:{OFFSET_Y}:black', tmp/'initial.png')
        with Image.open(tmp/'initial.png') as canvas:
            bmp, initial = bitmap(canvas.convert('RGB'))
        (args.out/'logo.bmp').write_bytes(bmp)
        initial.save(args.out/'splash-preview.png')
        # Keep the requested initial still and blend into the reverse-motion
        # starting pose over four frames without extending the approved timeline.
        for quality in [82, 80, 78, 76]:
            with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_STORED) as z:
                z.writestr('desc.txt', f'{W} {H} {FPS}\nc 1 0 part0\np 0 0 part1\n')
                for i in range(count):
                    with Image.open(tmp/f'{i+1:04d}.png') as image:
                        canvas = image.convert('RGB')
                    if i==0:
                        canvas = initial
                    elif i<4:
                        canvas = Image.blend(initial, canvas, i/4)
                    data = encoded(canvas, None if i==0 else quality)
                    z.writestr(f'part0/{i:04d}.'+('png' if i==0 else 'jpg'), data)
                if canvas.getbbox() is not None:
                    raise ValueError('Approved render must end at full black')
                z.writestr('part1/0000.jpg', data)
            if archive.stat().st_size < 95_000_000:
                break
        else:
            raise ValueError('Animation exceeds the source asset size budget')

    shutil.copyfile(args.sound, args.out/'bootsound.mp3')
    media = MODULE/'system/product/media'
    for name, destination in [('logo.bmp',MODULE/'logo.bmp'),
                              ('bootanimation.zip',media/'bootanimation.zip'),
                              ('bootsound.mp3',media/'bootsound.mp3')]:
        shutil.copyfile(args.out/name, destination)

    # Preview the actual packaged frames, retaining the approved audio packets.
    preview = args.out/'bootysplash-preview.mp4'
    process = subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24',
        '-s',f'{W}x{CONTENT_H}','-r',str(FPS),'-i','-','-i',str(args.video),
        '-map','0:v:0','-map','1:a:0','-c:v','libx264','-preset','fast','-crf','18',
        '-pix_fmt','yuv420p','-c:a','copy','-t',str(duration),'-map_metadata','-1',
        '-movflags','+faststart',str(preview)],stdin=subprocess.PIPE)
    try:
        with zipfile.ZipFile(archive) as z:
            for name in sorted(n for n in z.namelist() if n.startswith('part0/')):
                with Image.open(io.BytesIO(z.read(name))) as image:
                    process.stdin.write(image.convert('RGB').crop((0,OFFSET_Y,W,OFFSET_Y+CONTENT_H)).tobytes())
    finally:
        process.stdin.close()
    if process.wait():
        raise RuntimeError('Preview encoding failed')
    manifest = {'version':'v0.6','canvas':[W,H],'content':[W,CONTENT_H],
                'offset':[0,OFFSET_Y],'fps':FPS,'frames':count,'duration_seconds':duration,
                'jpeg_quality':quality,'initial_handoff_frames':4,
                'inputs':{name:{'file':getattr(args,name).name,'sha256':sha(getattr(args,name))}
                          for name in ['video','still','sound']},
                'outputs':{name:sha(args.out/name) for name in ['logo.bmp','bootanimation.zip','bootsound.mp3','bootysplash-preview.mp4']}}
    (args.out/'media-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(manifest,indent=2))


if __name__=='__main__':
    main()
