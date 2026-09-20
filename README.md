# bl1-sdk-mods

Python mods for **Borderlands 1**, built with the [Borderlands SDK](https://bl-sdk.github.io/).

Each mod is a Python package (a folder with `__init__.py`) that loads through the SDK's mod manager. See [AGENTS.md](AGENTS.md) for development and release conventions used in this repo.

## Mods

| Mod | Description |
|-----|-------------|
| [Remove Eridian Weapon Slowdown](remove_eridian_weapon_slowdown/) | Removes the movement speed penalty from holding Eridian weapons. |
| [Quieter Transfusion Healing](quieter_transfusion_healing/) | Lowers the volume of the healing sound cue from Transfusion grenades. |
| [Only Drop Relevant Class Mods](only_drop_relevant_class_mods/) | Class mods that no player in the game can use stop spawning in loot. |
| [Only Drop Relevant Artifacts](only_drop_relevant_artifacts/) | Artifacts that no player in the game can use stop spawning in loot. |
| [Knoxx Class Mods Everywhere](knoxx_class_mods_everywhere/) | Makes the class mods from The Secret Armory of General Knoxx drop from enemies everywhere. |

## Links

- [Getting started developing SDK mods](https://bl-sdk.github.io/developing/getting_started/)
- [Releasing your mod](https://bl-sdk.github.io/developing/releasing_your_mod/)
- [BL1 mod DB](https://bl-sdk.github.io/willow1-mod-db/)
- [ui_utils reference (BL1)](https://bl-sdk.github.io/developing/ui_utils/willow1/)
