# Outlaws - London

An open-world London game for the browser. It is built for an iPad (A16) with a keyboard and mouse and is served with GitHub Pages. The engine is three.js r160, and every model (people, vehicles, guns, the whole city and its street furniture) is built in Blender.

**Play:** https://0rderless.github.io/outlaws1/ (turn on Pages under Settings → Pages → Deploy from branch → `main` / root).

- **City:** a round island about 950 m across, modelled in Blender. A wide ring road runs all the way round the waterfront and every outer street joins it, so there are no dead ends or invisible walls. You just keep looping. Beyond the ring road are a seafront promenade, a sea wall and open water.
  - The Thames runs through the middle under five bridges.
  - Landmarks: Big Ben (Elizabeth Tower, with gilded clock faces, belfry and spire) and the Houses of Parliament, St Paul's Cathedral (dome, lantern and west towers), Stamford Bridge stadium (you can drive onto the pitch), Buckingham Palace and the Mall, the London Eye (it turns), Tower Bridge, the Tower of London, the Shard, the Gherkin, the Walkie-Talkie, the Cheesegrater, and the Canary Wharf towers.
  - Tower Bridge has Gothic towers on river piers, blue-and-white high-level walkways and suspension chains.
  - Streets: brick and stone terraces with real window openings, shopfronts, awnings, mansard roofs and chimneys, glass towers, kerbs and pavements, zebra crossings with Belisha beacons, Victorian lamp posts, trees, phone boxes, post boxes, bus shelters and billboards.
- **Day and night:**
  - The sun rises in the east and sets in the west, followed by a moonlit sky full of stars. After dark the office and shop windows light up, the street lamps cast pools of light, and your vehicle has headlights.
  - In Settings you can keep the full cycle (12 to 96 minutes per day) or fix the time at dawn, midday, sunset or night. T skips ahead one hour.
- **Characters:** realistic MakeHuman (CC0) bodies rigged to a Mixamo skeleton and animated with motion-captured idle, walk and run clips. The hero wears a black tank top, black shorts and a backwards cap.
- **Vehicles (Blender):**
  - The cars have recessed tinted glass, door shut lines, projector lamps, interiors seen through the glass and ten-spoke alloys.
  - Models: saloon, hatchback, SUV, sports car, the London black cab, a Met police estate, and a classic Routemaster bus.
  - A **Chiron-style hypercar** that does 170 mph.
  - A sport **motorbike** that leans into corners.
  - A flyable **helicopter**.
  - A **tank**: a machine gun on a left click, and a cannon whose shells blow up cars, buses and police helicopters on R or a right click.
  - Wheel positions are read straight from the Blender models, so every wheel sits in its arch.
- **Spawn anything:** press **V** (or tap the car button under the settings gear) to spawn any vehicle in front of you in any paint colour. Only you can spawn the tank.
- **Explosions:** cars catch fire and blow up when shot enough or hit by a tank shell, and the blast damages everything around them.
- **Car radio:** six built-in songs (Montagem Dominador, Montagem Fearless, Montagem Alquimia, Isolation, Montagem Ritmo Astral and Montagem Impacto) play as soon as you get in a vehicle.
  - Q and E or the mouse wheel change song, and the red radio button shows the full list.
  - There is also OUTLAWS FM, an original phonk station generated live, and **Add songs** to load more from your iPad.

## Controls

**On iPad with a mouse:** Safari on iPad can't capture the mouse (it has no Pointer Lock), so the game switches to a free pointer:
- The crosshair follows your mouse, and shots snap to the person nearest it.
- Push the pointer against the left or right edge of the screen to turn the camera, or use the arrow keys.
- Most iPad keyboards have no Esc key, so P pauses.
- Press / or tap the **?** button for the controls card. The Mouse setting can force either mode.
- Tip: use Share → Add to Home Screen. It installs as **Outlaws** with its own icon and runs full screen.

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
   - The vehicle scripts are separate: `python3 -I tools/blender/cars.py <type> assets/cars/<type>.glb` builds each car, and `bus.py`, `bike.py`, `tank.py`, `heli.py` and `wheel.py` build the Routemaster, the motorbike, the tank, the helicopter and the wheels. `cars.py` also writes `assets/cars/specs.json`, which holds each car's wheel positions.
  4. Compress each with `gltf-transform quantize --quantize-color 8` followed by `gltf-transform meshopt`, which gives the `*.min.glb` files the game loads.
  5. `people.py`, `guns.py` and `anims.py` build the characters, guns and the animation file. The character scripts expect the MakeHuman base mesh and the MPFB2 Mixamo rig and weights from the makehumancommunity GitHub repos.

Credits: MakeHuman base mesh and rig (CC0, makehumancommunity), and the Mixamo X Bot animations and brick texture from the three.js examples.
