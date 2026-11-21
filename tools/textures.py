"""Generates the city texture layers (512px each) -> assets/city/layers.jpg + layers.json."""
import json, math, os, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, '..', 'assets', 'city')
N = 512; rng = np.random.default_rng(7); R = random.Random(7)
def noise(scale, octaves=4, seed=0):
    g = np.random.default_rng(seed); out = np.zeros((N, N))
    for o in range(octaves):
        s = max(2, int(N / scale * 2 ** o)); a = g.random((s, s))
        img = Image.fromarray((a * 255).astype(np.uint8)).resize((N, N), Image.BICUBIC)
        # make it tile: blend with shifted copy
        arr = np.asarray(img, dtype=float) / 255; out += arr / 2 ** o
    out = (out - out.min()) / (out.max() - out.min() + 1e-9); return out
def tileable(arr):
    a = arr; b = np.roll(np.roll(a, N // 2, 0), N // 2, 1)
    y, x = np.mgrid[0:N, 0:N] / N; w = (np.minimum(np.minimum(x, 1 - x), np.minimum(y, 1 - y)) * 2).clip(0, 1)[..., None] if a.ndim == 3 else (np.minimum(np.minimum(x, 1 - x), np.minimum(y, 1 - y)) * 2).clip(0, 1)
    w = np.clip(w * 3, 0, 1); return a * w + b * (1 - w)
def rgb(base, n=None, amt=0.1):
    img = np.ones((N, N, 3)) * np.array(base, dtype=float) / 255
    if n is not None: img *= (1 - amt + n[..., None] * amt * 2)
    return img
def to_img(a): return Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))
layers = {}
# brick: desaturated photo so vertex colours pick the brick colour
src = Image.open(os.path.join(HERE, '..', 'assets', 'brick_diffuse.jpg')).convert('RGB').resize((N, N))
b = np.asarray(src, dtype=float) / 255; grey = b.mean(2, keepdims=True); b = grey * .8 + b * .2; b = b / b.mean() * .62
layers['brick'] = b
n1 = tileable(noise(40, 5, 1))
st = rgb((224, 220, 210), n1, .08); im = to_img(st); d = ImageDraw.Draw(im)
for row in range(6):
    y = int(row * N / 6); d.line([(0, y), (N, y)], fill=(150, 145, 135), width=3); off = (row % 2) * 85
    for x in range(-85 + off, N, 170): d.line([(x, y), (x, y + N // 6)], fill=(160, 155, 145), width=3)
layers['stone'] = np.asarray(im.filter(ImageFilter.GaussianBlur(.6)), dtype=float) / 255
layers['paint'] = rgb((236, 233, 226), tileable(noise(60, 4, 2)), .03)
sl = rgb((78, 82, 88), tileable(noise(30, 4, 3)), .12); im = to_img(sl); d = ImageDraw.Draw(im)
for row in range(12):
    y = row * N // 12; d.line([(0, y), (N, y)], fill=(40, 42, 46), width=3)
    for x in range((row % 2) * 32, N, 64): d.line([(x, y), (x, y + N // 12)], fill=(48, 50, 55), width=2)
layers['slate'] = np.asarray(im, dtype=float) / 255
asph_n = tileable(noise(12, 5, 4)); asph = rgb((62, 64, 68), asph_n, .14)
spk = rng.random((N, N)) < .02; asph[spk] *= 1.35; layers['asphalt'] = asph
def road(width_m, lines):
    im = to_img(asph.copy()); d = ImageDraw.Draw(im); px = N / width_m
    d.rectangle([0, 0, int(.35 * px), N], fill=(46, 47, 50)); d.rectangle([N - int(.35 * px), 0, N, N], fill=(46, 47, 50))
    for kind, u, w in lines:
        x = int(u * px); ww = max(2, int(w * px))
        if kind == 'solid': d.rectangle([x - ww // 2, 0, x + ww // 2, N], fill=(236, 236, 228))
        if kind == 'yellow': d.rectangle([x - ww // 2, 0, x + ww // 2, N], fill=(232, 195, 58))
        if kind == 'dash':
            for y in range(0, N, N // 2): d.rectangle([x - ww // 2, y, x + ww // 2, y + N // 4], fill=(236, 236, 228))
    return np.asarray(im, dtype=float) / 255
layers['road'] = road(14, [('yellow', .55, .1), ('yellow', .75, .1), ('yellow', 13.25, .1), ('yellow', 13.45, .1), ('dash', 7, .15)])
layers['roadring'] = road(18, [('yellow', .55, .1), ('yellow', .75, .1), ('yellow', 17.25, .1), ('yellow', 17.45, .1), ('solid', 8.85, .12), ('solid', 9.15, .12), ('dash', 4.6, .12), ('dash', 13.4, .12)])
pv = rgb((190, 186, 178), tileable(noise(50, 4, 5)), .06); im = to_img(pv); d = ImageDraw.Draw(im)
for k in range(5):
    p = k * N // 4; d.line([(p, 0), (p, N)], fill=(130, 126, 120), width=3); d.line([(0, p), (N, p)], fill=(130, 126, 120), width=3)
arr = np.asarray(im, dtype=float) / 255
for i in range(4):
    for j in range(4): arr[j * 128 + 2:(j + 1) * 128 - 2, i * 128 + 2:(i + 1) * 128 - 2] *= R.uniform(.93, 1.06)
layers['pavement'] = arr
kb = rgb((170, 168, 164), tileable(noise(8, 4, 6)), .2); kb[:, ::170] *= .6; layers['kerb'] = kb
gr = tileable(noise(10, 6, 7)); g = np.stack([.25 + gr * .15, .42 + gr * .2, .18 + gr * .08], 2); blades = rng.random((N, N)) < .08; g[blades] *= rng.uniform(.75, 1.25, (blades.sum(), 1)); layers['grass'] = g
layers['gravel'] = rgb((205, 190, 160), tileable(noise(6, 4, 8)), .2)
bk = tileable(noise(20, 4, 9)); bark = np.stack([.33 + bk * .1, .27 + bk * .08, .21 + bk * .06], 2); bark *= (0.85 + .15 * np.sin(np.arange(N) / 6.0)[None, :, None]); layers['bark'] = bark
lv = tileable(noise(14, 6, 10)); lv2 = tileable(noise(40, 3, 11)); layers['leaves'] = np.stack([.18 + lv * .16 + lv2 * .05, .32 + lv * .24 + lv2 * .06, .12 + lv * .1], 2)
layers['metal'] = rgb((40, 44, 42), tileable(noise(30, 3, 12)), .1)
cc = rgb((178, 176, 170), tileable(noise(25, 5, 13)), .1); cc[::128, :] *= .8; layers['concrete'] = cc
wd = tileable(noise(30, 3, 14)); wood = np.stack([.45 + wd * .1, .3 + wd * .07, .18 + wd * .05], 2); wood[::64, :] *= .55; layers['wood'] = wood
zb = asph.copy(); u = np.arange(N) // (N // 8); zb[:, (u % 2 == 0)] = .92; layers['zebra'] = zb
layers['gold'] = rgb((212, 170, 70), tileable(noise(20, 3, 15)), .12)
layers['steel'] = rgb((170, 175, 182), tileable(noise(60, 3, 16)), .06)
layers['redasphalt'] = rgb((150, 72, 58), asph_n, .14)
im = Image.new('RGB', (N, N), (201, 164, 63)); d = ImageDraw.Draw(im); c = N / 2
d.ellipse([c - 226, c - 226, c + 226, c + 226], fill=(246, 241, 223), outline=(28, 28, 28), width=12); d.ellipse([c - 168, c - 168, c + 168, c + 168], outline=(28, 28, 28), width=4)
try: font = ImageFont.truetype('DejaVuSerif-Bold.ttf', 38)
except Exception: font = ImageFont.load_default()
for i, t in enumerate(['XII', 'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI']):
    a = i / 12 * math.tau - math.pi / 2; x = c + math.cos(a) * 198; y = c + math.sin(a) * 198; d.text((x, y), t, fill=(28, 28, 28), font=font, anchor='mm')
for k in range(60):
    a = k / 60 * math.tau; d.ellipse([c + math.cos(a) * 160 - 3, c + math.sin(a) * 160 - 3, c + math.cos(a) * 160 + 3, c + math.sin(a) * 160 + 3], fill=(28, 28, 28))
for a, l, w in ((10 / 12 * math.tau + .09 - math.pi / 2, 112, 14), (2 / 12 * math.tau - math.pi / 2, 164, 8)):
    d.line([(c, c), (c + math.cos(a) * l, c + math.sin(a) * l)], fill=(28, 28, 28), width=w)
layers['clock'] = np.asarray(im, dtype=float) / 255
ADS = [('KEBAB KING', 'OPEN TILL 4AM', (255, 204, 0), (192, 20, 27)), ('BROLLY & CO.', 'RAINING AGAIN?', (29, 53, 87), (241, 250, 238)), ('THAMES FM 97.3', 'THE SOUND OF THE CITY', (106, 27, 154), (255, 230, 109)),
       ('BRUV ENERGY', 'PROPER TEA. PROPER BUZZ.', (0, 168, 107), (255, 255, 255)), ("CHIPPY'S", 'FISH & CHIPS £5', (244, 239, 230), (13, 59, 102)), ('MIND THE GAP', 'SHOES THAT FIT', (230, 57, 70), (255, 255, 255))]
im = Image.new('RGB', (N, N)); d = ImageDraw.Draw(im)
try: f1 = ImageFont.truetype('DejaVuSans-Bold.ttf', 28); f2 = ImageFont.truetype('DejaVuSans-Bold.ttf', 15)
except Exception: f1 = f2 = ImageFont.load_default()
for i, (t1, t2, bg, fg) in enumerate(ADS):
    x0, y0 = (i % 2) * 256, (i // 2) * 170; d.rectangle([x0, y0, x0 + 256, y0 + 170], fill=bg); d.text((x0 + 128, y0 + 70), t1, fill=fg, font=f1, anchor='mm'); d.text((x0 + 128, y0 + 125), t2, fill=fg, font=f2, anchor='mm')
layers['ads'] = np.asarray(im, dtype=float) / 255
ss = rgb((210, 186, 130), tileable(noise(30, 5, 17)), .1); im = to_img(ss); d = ImageDraw.Draw(im)
for x in range(0, N, 64): d.line([(x, 0), (x, N)], fill=(150, 128, 82), width=4)
for y in range(0, N, 128): d.line([(0, y), (N, y)], fill=(160, 138, 92), width=6)
layers['sandstone'] = np.asarray(im, dtype=float) / 255
layers['lampglass'] = rgb((250, 236, 200)); layers['signal'] = rgb((255, 170, 30))
layers['leather'] = rgb((30, 30, 32), tileable(noise(20, 3, 18)), .1)
PROPS = {'brick': (.9, 0, 0), 'stone': (.85, 0, 0), 'paint': (.55, 0, 0), 'slate': (.7, 0, 0), 'asphalt': (.95, 0, 0), 'road': (.93, 0, 0), 'roadring': (.93, 0, 0), 'pavement': (.9, 0, 0),
         'kerb': (.8, 0, 0), 'grass': (1, 0, 0), 'gravel': (1, 0, 0), 'bark': (.95, 0, 0), 'leaves': (.75, 0, 0), 'metal': (.4, .65, 0), 'concrete': (.9, 0, 0), 'wood': (.8, 0, 0), 'zebra': (.93, 0, 0),
         'gold': (.3, 1, 0), 'steel': (.25, .9, 0), 'redasphalt': (.93, 0, 0), 'clock': (.45, 0, .6), 'ads': (.5, 0, .8), 'sandstone': (.85, 0, 0), 'lampglass': (.2, 0, 3.0), 'signal': (.3, 0, 2.0), 'leather': (.6, 0, 0)}
names = list(PROPS)
strip = np.concatenate([np.clip(layers[n], 0, 1) for n in names], 0)
Image.fromarray((strip * 255).astype(np.uint8)).save(os.path.join(OUT, 'layers.jpg'), quality=86)
json.dump(dict(size=N, layers=[dict(name=n, rough=PROPS[n][0], metal=PROPS[n][1], night=PROPS[n][2]) for n in names]), open(os.path.join(OUT, 'layers.json'), 'w'), indent=1)
print(len(names), 'layers', os.path.getsize(os.path.join(OUT, 'layers.jpg')) // 1024, 'KB')
