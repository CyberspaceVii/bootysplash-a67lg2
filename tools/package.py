#!/usr/bin/env python3
"""Create the install ZIP and release hashes from the checkout's runtime files."""
import argparse
import hashlib
from pathlib import Path
import zipfile

MODULE = Path(__file__).resolve().parents[1]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    args.out.mkdir(parents=True,exist_ok=True)
    files=[MODULE/name for name in ['module.prop','customize.sh','uninstall.sh','logo.bmp',
                                    'README.md','CHANGELOG.md','LICENSE',
                                    'post-fs-data.sh','boot-audio-volume.jar']]
    files+=sorted(p for p in (MODULE/'system').rglob('*') if p.is_file())
    archive=args.out/'bootysplash-a67lg2.zip'
    with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED) as z:
        for file in files:
            name=str(file.relative_to(MODULE))
            info=zipfile.ZipInfo(name,date_time=(2026,11,22,0,0,0))
            info.compress_type=zipfile.ZIP_DEFLATED
            info.external_attr=(0o100755 if file.suffix=='.sh' else 0o100644)<<16
            z.writestr(info,file.read_bytes())
    release=[archive]
    preview=args.out/'bootysplash-preview.mp4'
    if preview.exists():
        release.append(preview)
    lines=[]
    for path in release:
        with path.open('rb') as stream:
            digest=hashlib.file_digest(stream,'sha256').hexdigest()
        lines.append(f'{digest}  {path.name}\n')
    (args.out/'SHA256SUMS').write_text(''.join(lines))
    print(archive)


if __name__=='__main__':
    main()
