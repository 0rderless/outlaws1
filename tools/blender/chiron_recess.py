"""Headlamp recesses for chiron.py (exec'd inside it, sharing its globals).
Runs after the body is subdivided and the wheel arches are cut, before the glass insets: carve the headlamp
cavities into `body` here (e.g. a BOOLEAN DIFFERENCE with a cutter mesh whose material is the dark interior colour).
Lamps are added later by chiron_lamps.py and land on whatever surface is here (they ray-cast onto the front)."""
