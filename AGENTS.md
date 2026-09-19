# AGENTS.md

Guidance for agents working in this repo. This repo holds [Borderlands SDK](https://bl-sdk.github.io/) mods for **Borderlands 1** (`willow1`). Read the [getting started](https://bl-sdk.github.io/developing/getting_started/) and [releasing your mod](https://bl-sdk.github.io/developing/releasing_your_mod/) docs before doing non-trivial work.

## Repo layout

- One folder per mod: `<mod_name>/`
- `__init__.py` — mod entry point (executed when the game loads the mod)
- `pyproject.toml` — mod metadata; the single source of truth for name, version, description, authors, dependencies, and release info
- Any other Python files for that mod live in the same folder

## Developing a mod

- Mod entry points run in the game's embedded Python; there is no standalone runtime. Use the in-game console (`py` for one-liners, `pyexec <file>` for whole files) to experiment before writing a full mod.
- Put dependency/version checks at the top of `__init__.py`, e.g.:

  ```python
  assert __import__("mods_base").__version_info__ >= (1, 12), "Please update the SDK"

  from mods_base import Game

  if Game.get_current() not in (Game.BL1, Game.BL1E):
      import webbrowser

      webbrowser.open(f"https://bl-sdk.github.io/willow1-mod-db/requirements?mod={__name__}")
      raise AssertionError("Only works in BL1/BL1E")
  ```

  Optionally open the requirements page on failure: `webbrowser.open("https://bl-sdk.github.io/willow1-mod-db/requirements?mod=<project.name>")`.
- For SDK version requirements, add `willow1_mod_manager >= x.y` to `project.dependencies`.
- Read bundled assets with `mods_base.open_in_mod_dir` (or `importlib.resources`); write persistent data under a folder you create in `SETTINGS_DIR`.
- Use `unrealsdk.logging.*` for console output, not `print`.
- For IDE/typing support, point extra paths at the game's `sdk_mods` folder and `sdk_mods/.stubs` (native module stubs).

## Releasing a mod

1. **Package as `.sdkmod`**: a zip (renamed `.sdkmod`) whose root contains exactly one folder named `<mod_name>`, with `__init__.py` inside. No extra files or folders at the zip root. (Use a `.zip` mod folder only when shipping a native `.pyd`; hybrid `.zip` with a game-folder layout only when shipping upk/pak files.)
2. **`pyproject.toml` is the source of truth** — keep `project` (name, version, description, authors, dependencies, urls) and `tool.sdkmod` (name, version, supported_games, coop_support, license, download) in sync with the actual mod.
3. **Mod DB page**: add a markdown file to the `willow1_mods` folder in the [bl-sdk.github.io site repo](https://github.com/bl-sdk/bl-sdk.github.io) with front matter `pyproject_url:` pointing at a raw.githubusercontent.com link to your `pyproject.toml` (auto-updating, not a pinned commit), plus a detailed description.

## Code style

- ruff is the linter and formatter. The config lives in the root `ruff.toml` (SDK house
  style: Python 3.14 target, line length 100).
- Before committing, run:

  ```sh
  ruff check --fix .
  ruff format .
  ```

  All Python code must pass `ruff check .` and `ruff format --check .` cleanly.
- Mod `__init__.py` headers deliberately run the SDK version check before importing from
  `mods_base`, so the import comes after code. That would normally be E402; `ruff.toml`
  ignores E402 for `**/__init__.py` instead of working around it (no `if True:` blocks).

## Conventions

- Mod folder name = `project.name` (snake_case), matching the inner folder in the `.sdkmod`.
- Set `supported_games` to the Willow1 games the mod supports (BL1 and/or BL1E); set `coop_support` honestly (`Unknown` / `Incompatible` / `RequiresAllPlayers` / `ClientSide` / `HostOnly`).
- When releasing a version: bump `project.version` (and `tool.sdkmod.version`) before packaging.
