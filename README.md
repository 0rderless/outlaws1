# London Streets

A small open-world London game for the browser. It is built for an iPad (A16) with a keyboard and mouse and is served with GitHub Pages. The engine is three.js r160, and every model (people, vehicles, guns, the whole city and its street furniture) is built in Blender.

**Play:** https://0rderless.github.io/outlaws1/ (turn on Pages under Settings → Pages → Deploy from branch → `main` / root).

- **City:** a round island about 950 m across, modelled in Blender. A wide ring road runs all the way round the waterfront and every outer street joins it, so there are no dead ends or invisible walls. You just keep looping. Beyond the ring road are a seafront promenade, a sea wall and open water.
  - The Thames runs through the middle under five bridges.
  - Landmarks: Big Ben (Elizabeth Tower, with gilded clock faces, belfry and spire) and the Houses of Parliament, Buckingham Palace and the Mall, the London Eye (it turns), Tower Bridge, the Tower of London, the Shard, the Gherkin, the Walkie-Talkie, the Cheesegrater, and the Canary Wharf towers.
  - Tower Bridge has Gothic towers on river piers, blue-and-white high-level walkways and suspension chains.
  - Streets: brick and stone terraces with real window openings, shopfronts, awnings, mansard roofs and chimneys, glass towers, kerbs and pavements, zebra crossings with Belisha beacons, Victorian lamp posts, trees, phone boxes, post boxes, bus shelters and billboards.
- **Day and night:**
  - The sun rises in the east and sets in the west, followed by a moonlit sky full of stars. After dark the office and shop windows light up, the street lamps cast pools of light, and your vehicle has headlights.
  - In Settings you can keep the full cycle (12 to 96 minutes per day) or fix the time at dawn, midday, sunset or night. T skips ahead one hour.
- **Characters:** realistic MakeHuman (CC0) bodies rigged to a Mixamo skeleton and animated with motion-captured idle, walk and run clips. The hero wears a black tank top, black shorts and a backwards cap.
- **Vehicles (Blender):**
  - The cars are lofted bodies with recessed tinted glass and rubber seals, door shut lines, projector headlamps with LED strips, wrap-round tail lights, grilles, mirrors and handles. Seats, dashboards and right-hand-drive steering wheels are visible through the glass. They ride on ten-spoke alloys.
  - Models: saloon, hatchback, SUV, sports car, the London black cab (round lamps, chrome grille, TAXI sign), a Met police estate in Battenburg livery, and a classic Routemaster double-decker. The Routemaster has a cream band, both decks of windows with seats inside, a radiator grille and round lamps, and the open rear platform with its pole.
  - A sport motorbike that leans into corners and has a riding pose. Crash it hard and you go over the handlebars.
  - AI traffic drives on the left.
- **Police:**
  - Wanted levels run from 1 to 5 stars. Police cars give chase, officers try to arrest you or shoot, and a helicopter joins at 4 stars.
  - Each police car carries a crew of two. Once both officers are down the car is left empty and you can steal it, and reinforcements arrive in new cars after a delay.

## Controls

**On iPad with a mouse:** Safari on iPad can't capture the mouse (it has no Pointer Lock), so the game switches to a free pointer:
- The crosshair follows your mouse, and shots snap to the person nearest it.
- Push the pointer against the left or right edge of the screen to turn the camera, or use the arrow keys.
- Most iPad keyboards have no Esc key, so P pauses.
- Press / or tap the **?** button for the controls card. The Mouse setting can force either mode.
- Tip: use Share → Add to Home Screen to play full screen without the Safari toolbar.

| Key | Action |
| --- | --- |
| WASD | Move, or drive and ride |
| Mouse | Look and aim (on iPad: aim, and push to the screen edge to turn) |
| Arrow keys | Turn and tilt the camera |
| Left click | Shoot |
| Right click | Lock on to the nearest person |
| Shift | Sprint; handbrake in a vehicle |
| C | Walk / jog |
| Space | Jump; handbrake in a vehicle |
| F | Get on or off a bike, or in and out of a car |
| 1 2 3 or the mouse wheel | Switch weapon |
| H | Horn |
| T | Skip ahead one hour |
| P or Esc | Pause and settings |
| / | Show or hide the controls card |

## Performance (iPad)

- The city is merged into roughly one draw call per material per 120 m chunk, all textured from a single texture array.
- Street furniture is only drawn within about 150 m, and distant cars are hidden.
- Medium quality on iPad renders at 1.25× pixel density with a 400 m view distance.
- The layout is checked at 4:3 (1024×768) and at the 1180×820 iPad landscape viewport.

## Files

- `index.html` runs the game. Locally it needs a static web server, because it loads `assets/` and `lib/`.
- `lib/` is a pinned copy of three.js r160 and the loaders it uses, including the meshopt decoder (MIT licence in `lib/LICENSE-three`).
- `assets/` holds the models, animations and city data (`assets/city/`).
- `tools/` holds the build scripts:
  1. `python3 tools/layout.py` lays out the roads, blocks, building lots, props and colliders, and writes `assets/city/layout.json`.
  2. `python3 tools/textures.py` paints the 26 surface textures into `assets/city/layers.jpg`.
  3. `python3 -I tools/blender/city.py` and `python3 -I tools/blender/props.py` build the city, landmarks and props in Blender (bpy). They export `city.glb`, `eye.glb` and `props.glb`.
   - The vehicle scripts are separate: `python3 -I tools/blender/cars.py <type> assets/cars/<type>.glb` builds each car, and `bus.py`, `bike.py` and `wheel.py` build the Routemaster, the motorbike and the wheels.
  4. Compress each with `gltf-transform quantize --quantize-color 8` followed by `gltf-transform meshopt`, which gives the `*.min.glb` files the game loads.
  5. `people.py`, `guns.py` and `anims.py` build the characters, guns and the animation file. The character scripts expect the MakeHuman base mesh and the MPFB2 Mixamo rig and weights from the makehumancommunity GitHub repos.

Credits: MakeHuman base mesh and rig (CC0, makehumancommunity), and the Mixamo X Bot animations and brick texture from the three.js examples.
