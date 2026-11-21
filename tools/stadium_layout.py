"""Stamford Bridge in the layout: the pitch green, the colliders (walls you can't walk/drive through) and the map label.
Exec'd by tools/layout.py inside its loop over blocks with _b = the stadium block; col(x0, x1, z0, z1, h) adds a collider box,
greens.append([x0, z0, x1, z1]) a grass area, lm(name, x, z) a landmark label. Keep gaps in the colliders wherever the
model has entrances/gates you can walk through."""
x0, x1, z0, z1 = _b['x0'] + 3, _b['x1'] - 3, _b['z0'] + 3, _b['z1'] - 3; D = 12
FX = x1 - 14                                   # east facade line; FX..x1 is the open forecourt (same numbers as landmarks.py stadium())
px0, px1, pz0, pz1 = x0 + D, FX - D, z0 + D, z1 - D; cx, cz = (px0 + px1) / 2, (pz0 + pz1) / 2
EZ0, EZ1 = cz - 3, cz + 3                      # main entrance passage through the east stand
greens.append([px0, pz0, px1, pz1])
col(x0, px0, pz0, pz1, 15); col(px1, FX, pz0, EZ0, 15); col(px1, FX, EZ1, pz1, 15); col(px0, px1, z0, pz0, 15); col(px0, px1, pz1, z1, 15)
col(px1, FX, z0, pz0, 12); col(x0, px0, pz1, z1, 12)
lm('STAMFORD BRIDGE', (x0 + FX) / 2, (z0 + z1) / 2)
