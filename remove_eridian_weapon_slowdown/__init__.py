"""Remove the movement speed penalty applied by Eridian weapons."""

assert __import__("mods_base").__version_info__ >= (1, 12), "Please update the SDK"


from mods_base import Game, build_mod
from unrealsdk import find_object

if Game.get_current() not in (Game.BL1, Game.BL1E):
    import webbrowser

    webbrowser.open(f"https://bl-sdk.github.io/willow1-mod-db/requirements?mod={__name__}")
    raise AssertionError("Only works in BL1/BL1E")

ENCUMBRANCE_PATH = "d_attributes.Encumbrance.TotalEncumbrance"

_original_property_name: str | None = None


def _apply_patch(enabled: bool) -> None:
    global _original_property_name

    resolver = find_object("AttributeDefinition", ENCUMBRANCE_PATH).ValueResolverChain[0]
    if enabled:
        if _original_property_name is None:
            _original_property_name = str(resolver.PropertyName)
        resolver.PropertyName = ""
    elif _original_property_name is not None:
        resolver.PropertyName = _original_property_name


def on_enable() -> None:
    """Apply the patch whenever the mod is enabled."""
    _apply_patch(True)


def on_disable() -> None:
    """Restore the original encumbrance behavior whenever the mod is disabled."""
    _apply_patch(False)


build_mod()
