# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

import json
from pathlib import Path

from jupyter_releaser.util import run

LERNA_CMD = "jlpm run lerna version --no-push --force-publish --no-git-tag-version"

# match these with main branch on github
VERSION_MAJOR = 0
VERSION_MINOR = 19
VERSION_PATCH = 0
VERSION_ALPHA = 1

# increment this from 0 for our changes
VERSION_TWD = 5


def bump(force=False, skip_if_dirty=False):
    status = run("git status --porcelain").strip()
    if len(status) > 0:
        if skip_if_dirty:
            return
        # raise Exception("Must be in a clean git state with no untracked files")

    js_version = f"{VERSION_MAJOR}.{VERSION_MINOR}.{VERSION_PATCH}-alpha.{VERSION_ALPHA}-twd.{VERSION_TWD}"
    python_version = f"{VERSION_MAJOR}.{VERSION_MINOR}.{VERSION_PATCH}a{VERSION_ALPHA}+twd{VERSION_TWD}"

    # bump the JS packages
    lerna_cmd = f"{LERNA_CMD} {js_version}"
    if force:
        lerna_cmd += " --yes"
    run(lerna_cmd)

    run(f"jlpm")  # update yank.lock

    HERE = Path(__file__).parent.parent.resolve()

    # bump the Python packages
    for version_file in HERE.glob("python/**/_version.py"):
        content = version_file.read_text().splitlines()
        variable, current = content[0].split(" = ")
        if variable != "__version__":
            raise ValueError(
                f"Version file {version_file} has unexpected content;"
                f" expected __version__ assignment in the first line, found {variable}"
            )
        version_file.write_text(f'__version__ = "{python_version}"\n')

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


if __name__ == "__main__":
    bump()
