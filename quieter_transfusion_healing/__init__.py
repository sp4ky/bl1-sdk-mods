"""Lower the volume of the healing sound cue played by Transfusion grenades."""

from __future__ import annotations

assert __import__("mods_base").__version_info__ >= (1, 12), "Please update the SDK"

from typing import TYPE_CHECKING

from mods_base import Game, ObjectFlags, build_mod, hook
from unrealsdk import find_object, logging
from unrealsdk.hooks import Type

if Game.get_current() not in (Game.BL1, Game.BL1E):
    import webbrowser

    webbrowser.open(f"https://bl-sdk.github.io/willow1-mod-db/requirements?mod={__name__}")
    raise AssertionError("Only works in BL1/BL1E")

if TYPE_CHECKING:
    from typing import Any

    from unrealsdk.unreal import BoundFunction, UObject, WrappedStruct

SOUND_CUE_PATH = "Wep_Elemental_Effects.Weapon_Tech.Transfusion_Receive_healthCue"
QUIET_VOLUME = 0.2

_original_volume: float | None = None
_applied = False


def keep_alive(obj: UObject) -> None:
    """Prevent the engine from garbage collecting an object this mod mutated."""
    obj.ObjectFlags |= ObjectFlags.KEEP_ALIVE


def _apply(enabled: bool) -> bool:
    """Apply (or restore) the volume patch. Returns False if the cue isn't loaded yet."""
    global _applied, _original_volume

    try:
        sound_cue = find_object("SoundCue", SOUND_CUE_PATH)
    except ValueError:
        # The package isn't loaded yet (e.g. at game startup); a map change will retry.
        return False

    keep_alive(sound_cue)
    if _original_volume is None:
        _original_volume = sound_cue.VolumeMultiplier

    sound_cue.VolumeMultiplier = QUIET_VOLUME if enabled else _original_volume
    _applied = True
    return True


def on_enable() -> None:
    """Apply the volume patch whenever the mod is enabled."""
    _apply(True)


def on_disable() -> None:
    """Restore the original volume whenever the mod is disabled."""
    if _applied:
        _apply(False)


@hook("WillowGame.WillowGameInfo:PreCommitMapChange", Type.POST)
def _on_map_change(_obj: UObject, _args: WrappedStruct, _ret: Any, _func: BoundFunction) -> None:
    # The cue's package only loads during gameplay, so re-apply until the cue is available.
    if not _applied and not _apply(True):
        logging.dev_warning("Transfusion sound cue still not found after map change; will retry")


build_mod()
