# London Streets

A small open-world London game for the browser, built for an iPad (A16) with a keyboard and mouse, and served with GitHub Pages. Three.js r160 engine, models built in Blender.

- **Characters:** realistic MakeHuman (CC0) bodies rigged to a Mixamo skeleton and driven by motion-captured idle, walk and run animations, retargeted at load time. The hero wears a black tank top, black shorts, white trainers, a gold chain and a backwards cap. Pedestrians come in varied outfits, skin tones and hair; Met police wear hi-vis and custodian helmets.
- **Vehicles:** modelled in Blender with subdivision surfaces: saloon, hatchback, SUV, sports car, black cab, Met police car with Battenburg livery, and a double-decker bus. Reflective paint and glass, spinning, steering wheels.
- **Guns:** modelled pistol, SMG and pump shotgun.
- **London:** Big Ben, the Houses of Parliament, Buckingham Palace and the Mall, Tower Bridge, the Tower of London, the Shard, the Gherkin, the Walkie-Talkie, the Cheesegrater and the London Eye, plus brick and stone terraces with reflective windows, shopfronts, lamp posts, zebra crossings, phone boxes and billboards.
- **Lighting:** HDR sky lighting (golden hour), sun shadows, ACES tone mapping.
- **Police:** wanted level of 1 to 5 stars, pursuing cars, officers who arrest or shoot, and a helicopter at 4 stars.

## Controls

WASD move or drive · mouse look (click to lock the cursor) · left click shoot · right click lock on to the nearest person · Shift sprint / handbrake · C walk · Space jump / handbrake · F get in or out · 1 2 3 or wheel switch weapon · H horn · Esc pause and settings. On-screen touch buttons can be switched on in Settings.

## Files

- `index.html` runs the game. It is served by GitHub Pages; locally it needs any static web server because it loads `assets/` and `lib/`.
- `lib/` a pinned copy of three.js r160 and the loaders it uses (MIT licence in `lib/LICENSE-three`).
- `assets/` models, animations, HDR sky and textures.
- `tools/blender/` the Blender (bpy) scripts that build the characters, cars, wheel, guns and animation file. They expect the MakeHuman base mesh and the MPFB2 Mixamo rig/weights files, downloaded from the makehumancommunity GitHub repos.

Credits: MakeHuman base mesh and rig (CC0, makehumancommunity), Mixamo X Bot animations and HDR/brick textures from the three.js examples.
