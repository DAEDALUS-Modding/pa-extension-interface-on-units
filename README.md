# Planetary Annihilation Extension Interface On Units (PAEIOU)

This is a Python library that allows one to generate Planetary Annihilation mods that modify units and add units to the game. It also allows one to simulate modding other server mods in order to modify units that are touched by those mods. It is currently in a very early state, and is neither complete nor well-documented.

## Current State
PAEIOU currently does not yet allow one to generate split server/client companion mods, but this is a planned capability in the future.

## Format

By default, PAEIOU expects the following files in each unit folder:
- `unit.json`
- `si.png`
- `img.png`
- `build.json`

`unit.json` is a templated version of the unit's json file.

`si.png` is the unit's strategic icon as a png file.

`img.png` is the unit's buildbar icon as a png file.

`build.json` is a custom PAEIOU file that indicates where the unit appears on the build bar.

If the unit has a weapon or custom effect files, PAEIOU expects that all weapon, ammo, and effect files will have the ".json" or ".pfx" extension.

If the unit has a custom model, it is expected, by default, that the model is named `model.papa` and that its textures are `model_diffuse.papa`, `model_mask.papa`, `model_material.papa`.

In addition, you may change these defaults by including an optional  file, `meta.json`, which can have the following fields, in any order:
```
{
    "unit": "(filename)" | false,
    "si": "(filename)" | false,
    "img": "(filename)" | false,
    "build": "(filename)" | false,
    "models": ["(filenames)"]
}
```

If `"unit"` is set to `false`, the unit will not be added to the unit list. If it is set to a string, it instead specifies an alternative filename for the unit. This filename does **NOT** need to have extension `.json`, but this is **NOT** true for additional `.json` or `.pfx` files.

If `"si"` is set to `false`, the unit will not have a custom strategic icon. If it is set to a string, it instead specifies an alternative filename for the strategic icon.

If `"img"` is set to `false`, the unit will not have a custom buildbar image. If it is set to a string, it instead specifies an alternative filename for the buildbar image.

If `"build"` is set to `false`, the unit will not be buildable. If it is set to a string, it instead specifies an alternative filename for PAEIOU's `build.json`.

`"models"` allows one to specify additional models that may be required by auxilliary units like units spawned via attack.


For an example where some of these settings may be useful, consider the situation of adding an additional strategic icon through PAEIOU without adding a whole unit, one can use:
```
{
    "unit": false,
    "img": false,
    "build": false
}
```


## Future Goals
Allow one to merge multiple PAEIOU projects to generate composite mods without additional scripting (although this is currently enabled by just moving all of the PAEIOU projects' units into the same folder and concatenating `unit_add_list.txt`.