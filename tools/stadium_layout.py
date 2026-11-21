"""Stamford Bridge in the layout: the pitch green, the colliders (walls you can't walk/drive through) and the map label.
Exec'd by tools/layout.py inside its loop over blocks with _b = the stadium block; col(x0, x1, z0, z1, h) adds a collider box,
greens.append([x0, z0, x1, z1]) a grass area, lm(name, x, z) a landmark label. Keep gaps in the colliders wherever the
model has entrances/gates you can walk through."""
x0, x1, z0, z1 = _b['x0'] + 3, _b['x1'] - 3, _b['z0'] + 3, _b['z1'] - 3; D = 12
FX = x1 - 14                                   # east facade line; FX..x1 is the open forecourt (same numbers as landmarks.py stadium())
px0, px1, pz0, pz1 = x0 + D, FX - D, z0 + D, z1 - D; cx, cz = (px0 + px1) / 2, (pz0 + pz1) / 2
EZ0, EZ1 = cz - 3, cz + 3                      # main entrance passage: open from the forecourt, through the east stand, onto the pitch
greens.append([px0, pz0, px1, pz1])
# the four stands round the pitch (the east one split by the passage) and the four corners: a closed bowl x0..FX
col(x0, px0, pz0, pz1, 15); col(px0, px1, z0, pz0, 15); col(px0, px1, pz1, z1, 15)
col(px1, FX, pz0, pz1, 15)   # east stand solid until the entrance passage is modelled
for a0, a1 in ((x0, px0), (px1, FX)):
    for c0, c1 in ((z0, pz0), (pz1, z1)): col(a0, a1, c0, c1, 15)
# main entrance block projecting into the forecourt (stadium_entrance.py), split by the passage
# statue plinth on the round plaza in front of the entrance (stadium_plaza.py)
PX, PZ = FX + 9.6, EZ1 + 3.4; col(PX - 1, PX + 1, PZ - 1, PZ + 1, 1.5)
ZA = _b['z0'] + .02; col(FX + 5, FX + 10, ZA + 9, ZA + 16, 3)   # club shop kiosk
lm('STAMFORD BRIDGE', (x0 + FX) / 2, (z0 + z1) / 2)
