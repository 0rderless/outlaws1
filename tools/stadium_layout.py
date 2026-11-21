"""Stamford Bridge in the layout: the pitch green, the colliders (walls you can't walk/drive through) and the map label.
Exec'd by tools/layout.py inside its loop over blocks with _b = the stadium block; col(x0, x1, z0, z1, h) adds a collider box,
greens.append([x0, z0, x1, z1]) a grass area, lm(name, x, z) a landmark label. Keep gaps in the colliders wherever the
model has entrances/gates you can walk through."""
x0, x1, z0, z1 = _b['x0'] + 3, _b['x1'] - 3, _b['z0'] + 3, _b['z1'] - 3; D = 12
greens.append([x0 + D, z0 + D, x1 - D, z1 - D])
col(x0, x0 + D, z0 + D, z1 - D, 15); col(x1 - D, x1, z0 + D, z1 - D, 15); col(x0 + D, x1 - D, z0, z0 + D, 15); col(x0 + D, x1 - D, z1 - D, z1, 15)
col(x1 - D, x1, z0, z0 + D, 12); col(x0, x0 + D, z1 - D, z1, 12)
lm('STAMFORD BRIDGE', (x0 + x1) / 2, (z0 + z1) / 2)
