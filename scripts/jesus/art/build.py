"""Paint the Life of Jesus pictures: SVG scenes -> PNG (headless Chromium) -> WebP in art/jesus/.

usage: python3 scripts/jesus/art/build.py [moment numbers...]   (1-based, as in ?life=N; default all)
"""
import os, subprocess, sys, tempfile
sys.path.insert(0, os.path.dirname(__file__))
from paint import Scene
from scenes import S
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
OUT = os.path.join(ROOT, 'art', 'jesus')


def main(args):
    keys = [int(a) - 1 for a in args] if args else sorted(S)
    tmp = tempfile.mkdtemp()
    svgdir, pngdir = os.path.join(tmp, 'svg'), os.path.join(tmp, 'png')
    os.makedirs(svgdir)
    for k in keys:
        sc = Scene(101 + k * 17)
        S[k](sc)
        open(os.path.join(svgdir, f'{k + 1:02d}.svg'), 'w').write(sc.svg())
    subprocess.run(['node', os.path.join(HERE, 'render.js'), svgdir, pngdir], check=True)
    os.makedirs(OUT, exist_ok=True)
    for f in sorted(os.listdir(pngdir)):
        im = Image.open(os.path.join(pngdir, f)).convert('RGB')
        dst = os.path.join(OUT, f.replace('.png', '.webp'))
        im.save(dst, 'WEBP', quality=80, method=6)
        print(dst, os.path.getsize(dst) // 1024, 'KB')


if __name__ == '__main__':
    main(sys.argv[1:])
