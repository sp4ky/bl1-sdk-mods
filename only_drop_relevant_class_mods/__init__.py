"""Stop class mods that none of the players can use from spawning in loot."""

from __future__ import annotations

assert __import__("mods_base").__version_info__ >= (1, 12), "Please update the SDK"

from typing import TYPE_CHECKING

from mods_base import Game, RestartToDisable, build_mod, get_pc, hook
from unrealsdk import find_all
from unrealsdk.hooks import Type

if TYPE_CHECKING:
    from typing import Any

    from unrealsdk.unreal import BoundFunction, UObject, WrappedStruct

if Game.get_current() not in (Game.BL1, Game.BL1E):
    import webbrowser

    webbrowser.open(f"https://bl-sdk.github.io/willow1-mod-db/requirements?mod={__name__}")
    raise AssertionError("Only works in BL1/BL1E")

INVENTORY_CLASS = "WillowEquipAbleItem"
IMPOSSIBLE_GAME_STAGE = 100
SKIPPED_MAPS = ("Loader", "FakeEntry")


def _player_class_numbers() -> set[int]:
    """The 1-based class numbers of all players in the current game."""
    numbers: set[int] = set()
    for player in get_pc().WorldInfo.GRI.PRIArray:
        numbers.add(int(player.Owner.PlayerClass.CharacterName) + 1)
    return numbers


def _can_players_use(inv_def: UObject) -> bool:
    """Whether any player in the game can use the given inventory definition."""
    required = int(inv_def.RequiredCharacter)
    if required == 0:
        return True
    return required in _player_class_numbers()


def _clean_balances() -> None:
    """Mark balances of unusable items so the loot system can never roll them."""
    for balance in find_all("InventoryBalanceDefinition"):
        inv_def = balance.InventoryDefinition
        if inv_def is None:
            continue
        if str(inv_def.InventoryClass.Name) != INVENTORY_CLASS:
            continue
        if _can_players_use(inv_def):
            continue
        for manufacturer in balance.Manufacturers:
            for grade in manufacturer.Grades:
                grade.GameStageRequirement.MinGameStage = IMPOSSIBLE_GAME_STAGE


@hook("WillowGame.WillowGameInfo:PreCommitMapChange", Type.POST)
def _on_map_change(_obj: UObject, args: WrappedStruct, _ret: Any, _func: BoundFunction) -> None:
    if args.NextMapName in SKIPPED_MAPS:
        return
    if not get_pc().PlayerClass:
        return
    _clean_balances()


build_mod(cls=RestartToDisable)
