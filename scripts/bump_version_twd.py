# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

import json
import re
from pathlib import Path

import click
from jupyter_releaser.util import get_version


def increment_twd_version(current):
    """Increment TWD local version identifier.

    Examples:
        Python: 0.19.0a1 -> 0.19.0a1+twd1
                0.19.0a1+twd1 -> 0.19.0a1+twd2
        NPM:    0.19.0-alpha.1 -> 0.19.0-alpha.1+twd1
                0.19.0-alpha.1+twd1 -> 0.19.0-alpha.1+twd2
    """
    match = re.match(r'^(.+)\+twd(\d+)$', current)
    if match:
        base = match.group(1)
        twd_num = int(match.group(2))
        return f"{base}+twd{twd_num + 1}"
    else:
        return f"{current}+twd1"


@click.command()
@click.option("--force", default=False, is_flag=True)
@click.option("--skip-if-dirty", default=False, is_flag=True)
def bump(force, skip_if_dirty):
    from jupyter_releaser.util import run

    status = run("git status --porcelain").strip()
    if len(status) > 0:
        if skip_if_dirty:
            return
        if not force:
            raise Exception("Must be in a clean git state with no untracked files")

    current = get_version()

    # Increment Python version
    new_python_version = increment_twd_version(current)

    HERE = Path(__file__).parent.parent.resolve()

    # bump the Python packages
    for version_file in HERE.glob("python/**/_version.py"):
        content = version_file.read_text().splitlines()
        variable, current_val = content[0].split(" = ")
        if variable != "__version__":
            raise ValueError(
                f"Version file {version_file} has unexpected content;"
                f" expected __version__ assignment in the first line, found {variable}"
            )
        version_file.write_text(f'__version__ = "{new_python_version}"\n')

    # bump the JS packages - convert Python version format to NPM format
    # e.g., 0.19.0a1+twd1 -> 0.19.0-alpha.1+twd1
    js_version = new_python_version
    js_version = re.sub(r'a(\d+)', r'-alpha.\1', js_version)
    js_version = re.sub(r'b(\d+)', r'-beta.\1', js_version)
    js_version = re.sub(r'rc(\d+)', r'-rc.\1', js_version)

    # bump lerna packages
    lerna_cmd = f"jlpm run lerna version {js_version} --no-push --force-publish --no-git-tag-version"
    if force:
        lerna_cmd += " --yes"
    run(lerna_cmd)

    # bump the local package.json file
    path = HERE.joinpath("package.json")
    if path.exists():
        with path.open(mode="r") as f:
            data = json.load(f)

        data["version"] = js_version

        with path.open(mode="w") as f:
            json.dump(data, f, indent=2)
    else:
        raise FileNotFoundError(f"Could not find package.json under dir {path!s}")

    print(f"Bumped version: {current} -> {new_python_version}")


if __name__ == "__main__":
    bump()
