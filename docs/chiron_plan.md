# Chiron rebuild plan (for the next session)

Blueprint: `docs/chiron_blueprint.png`, traced from the user's side and front photos.

What is wrong with the current model (measured against the side photo, scaled by the 2.711 m wheelbase):
- **Front overhang is 0.98 m; the real car's is about 0.71 m.** The nose sticks out 27 cm too far. This is the "bonnet too big" problem.
- The rear overhang should be about 1.12 m, so the long tail grows by the same amount.

Targets (x = metres from the nose, z = height):
- Front axle at x 0.71, rear axle at x 3.42.
- Nose top z 0.68 and wing peak z 0.82 over the front wheel.
- Windscreen base **x 0.55 / z 0.79**, just behind the headlights. The user marked this on a screenshot, and it replaces the traced x 1.27.
  The glass runs in one long rake up to the roof front at x 1.83 / z 1.18, so the bonnet is only a short strip in front of it.
- Windscreen top x 1.83 / z 1.18; roof peak x 2.17 / z 1.212.
- Roof falls to x 3.6 / z 0.99, then the tail top at about z 0.78, with a near-vertical tail.
- C-line:
  - starts at the A-pillar foot and runs along the roof edge;
  - its rearmost point is at x about 2.85, z 0.8;
  - it sweeps forward along the lower door at z about 0.27 to just behind the front wheel.
- Bonnet (front view): two creases from the top corners of the horseshoe out to the windscreen corners, a spine down the middle, and high wings over the headlights.

Steps:
1. In `tools/blender/chiron.py`:
   - set FO to 0.71 and keep WB;
   - re-key `zroof`, `hz`, `zsh`, `wr` and the C-line constants to the targets above. Convert x to the script's t with t = x / 4.544.
   - Do not touch `chiron_lamps.py`, `chiron_recess.py` or the horseshoe code.
2. Check from the **side view only**: render it and overlay it on the blueprint outline. Iterate until the silhouette matches.
3. Run `tyrecheck.py hyper` and confirm there are no holes or clipping; `specs.json` updates automatically from FO.
4. Build once, then push. One pass, no agents.
