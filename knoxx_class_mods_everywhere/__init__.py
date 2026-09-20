"""Make the class mods from The Secret Armory of General Knoxx drop from enemies everywhere."""

from __future__ import annotations

assert __import__("mods_base").__version_info__ >= (1, 12), "Please update the SDK"

from typing import TYPE_CHECKING

from mods_base import Game, ObjectFlags, build_mod
from unrealsdk import find_object, load_package, logging

if TYPE_CHECKING:
    from unrealsdk.unreal import UObject

if Game.get_current() not in (Game.BL1, Game.BL1E):
    import webbrowser

    webbrowser.open(f"https://bl-sdk.github.io/willow1-mod-db/requirements?mod={__name__}")
    raise AssertionError("Only works in BL1/BL1E")

CLASSES = ("Brick", "Lilith", "Mordecai", "Roland")

COMMAND_ITEMS = {
    "Brick": "dlc3_gd_CommandDecks.Body_Command.Brick_Torgue_Ogre",
    "Lilith": "dlc3_gd_CommandDecks.Body_Command.Lilith_Hyperion_Specter",
    "Mordecai": "dlc3_gd_CommandDecks.Body_Command.Mordecai_SandS_Truxican",
    "Roland": "dlc3_gd_CommandDecks.Body_Command.Roland_Dahl_Marine",
}

PACKAGES = ("dlc3_gd_itempools", "gd_itempools", "gd_CommandDecks", "dlc3_gd_CommandDecks")

KNOXX_WEIGHT = "gd_Balance.Weighting.Weight_Awesome_5_VeryRare"

_saved_lengths: dict[str, int] | None = None
_saved_weights: dict[str, list[UObject]] | None = None
_applied = False


def keep_alive(obj: UObject) -> None:
    """Prevent the engine from garbage collecting an object this mod mutated."""
    obj.ObjectFlags |= ObjectFlags.KEEP_ALIVE


def _main_list(class_name: str) -> UObject:
    """The class's main class-mod drop list (the one enemies roll from)."""
    return find_object(
        "ItemPartListDefinition", f"gd_CommandDecks.Body_{class_name}.BodyParts_{class_name}"
    )


def _loyalty_list(class_name: str) -> UObject:
    """The class's Knoxx (Secret Armory DLC) part list."""
    return find_object(
        "ItemPartListDefinition", f"dlc3_gd_CommandDecks.Body_Loyalty.BodyParts_{class_name}"
    )


def _apply() -> None:
    """Append the Knoxx parts to every class's drop list, weighted as KNOXX_WEIGHT."""
    global _saved_lengths, _saved_weights

    for package in PACKAGES:
        load_package(package)

    weight_def = find_object("AttributeInitializationDefinition", KNOXX_WEIGHT)
    lengths: dict[str, int] = {}
    weights: dict[str, list[UObject]] = {}
    for class_name in CLASSES:
        main = _main_list(class_name)
        loyalty = _loyalty_list(class_name)
        keep_alive(main)
        keep_alive(loyalty)

        lengths[class_name] = len(main.WeightedParts)
        weights[class_name] = [
            part.Manufacturers[0].DefaultWeight.InitializationDefinition
            for part in loyalty.WeightedParts
        ]

        for part in loyalty.WeightedParts:
            main.WeightedParts.append(part)
        main.WeightedParts.append(main.WeightedParts[-1])
        main.WeightedParts[-1].Part = find_object("ItemPartDefinition", COMMAND_ITEMS[class_name])
        main.WeightedParts[-1].Manufacturers[0].Manufacturer = None

        for part in main.WeightedParts:
            if str(part.Part).startswith("dlc3_"):
                part.Manufacturers[0].DefaultWeight.InitializationDefinition = weight_def

    _saved_lengths = lengths
    _saved_weights = weights


def _restore() -> None:
    """Truncate the drop lists back to their original lengths and restore weights."""
    assert _saved_lengths is not None and _saved_weights is not None
    for class_name in CLASSES:
        main = _main_list(class_name)
        del main.WeightedParts[_saved_lengths[class_name] :]
        loyalty = _loyalty_list(class_name)
        for part, weight in zip(loyalty.WeightedParts, _saved_weights[class_name], strict=True):
            part.Manufacturers[0].DefaultWeight.InitializationDefinition = weight


def on_enable() -> None:
    """Apply the patch whenever the mod is enabled."""
    global _applied

    if _applied:
        return

    try:
        _apply()
    except ValueError as exc:
        logging.dev_warning(f"Knoxx class mods not applied (Secret Armory DLC missing?): {exc}")
        return

    _applied = True


def on_disable() -> None:
    """Restore the original drop lists whenever the mod is disabled."""
    global _applied, _saved_lengths, _saved_weights

    if not _applied:
        return

    _restore()
    _applied = False
    _saved_lengths = None
    _saved_weights = None


build_mod()
