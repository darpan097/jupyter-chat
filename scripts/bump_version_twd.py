# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

import json
import re
from pathlib import Path

import click
from jupyter_releaser.util import get_version, run


def increment_twd_version(current):
    """
    Increment TWD version:
    - Python: 0.19.0a1 -> 0.19.90a1+twd1, 0.19.90a1+twd1 -> 0.19.90a1+twd2
    - NPM: 0.19.0-alpha.1 -> 0.19.0-alpha.1+twd1, 0.19.0-alpha.1+twd1 -> 0.19.0-alpha.1+twd2
    """
    # Check if already has +twdN suffix
    twd_match = re.search(r'\+twd(\d+)$', current)

    if twd_match:
        # Increment existing twd number
        twd_num = int(twd_match.group(1))
        new_version = re.sub(r'\+twd\d+$', f'+twd{twd_num + 1}', current)
    else:
        # Add +twd1 suffix
        # For Python versions, also change micro version to 90 if it's not already
        # E.g., 0.19.0a1 -> 0.19.90a1+twd1
        py_match = re.match(r'^(\d+)\.(\d+)\.(\d+)(.*)', current)
        if py_match:
            major, minor, micro, suffix = py_match.groups()
            if micro != '90':
                new_version = f"{major}.{minor}.90{suffix}+twd1"
            else:
                new_version = f"{current}+twd1"
        else:
            # For NPM format or other formats, just append +twd1
            new_version = f"{current}+twd1"

    return new_version


def convert_python_to_js_version(py_version):
    """Convert Python version format to JavaScript/NPM format."""
    # Remove +twd suffix temporarily
    twd_match = re.search(r'(\+twd\d+)$', py_version)
    twd_suffix = twd_match.group(1) if twd_match else ''
    base_version = re.sub(r'\+twd\d+$', '', py_version)

    # Parse Python version: e.g., 0.19.90a1
    match = re.match(r'^(\d+)\.(\d+)\.(\d+)([a-z]+)?(\d+)?', base_version)
    if not match:
        raise ValueError(f"Cannot parse Python version: {py_version}")

    major, minor, micro, pre_type, pre_num = match.groups()

    js_version = f"{major}.{minor}.{micro}"

    if pre_type and pre_num:
        # Convert Python pre-release format to NPM format
        pre_type_map = {'a': 'alpha', 'b': 'beta', 'rc': 'rc'}
        pre_type_js = pre_type_map.get(pre_type, pre_type)
        js_version += f"-{pre_type_js}.{pre_num}"

    # Add twd suffix back
    if twd_suffix:
        js_version += twd_suffix

    return js_version


@click.command()
@click.option("--force", default=False, is_flag=True)
@click.option("--skip-if-dirty", default=False, is_flag=True)
def bump(force, skip_if_dirty):
    status = run("git status --porcelain").strip()
    if len(status) > 0:
        if skip_if_dirty:
            return
        raise Exception("Must be in a clean git state with no untracked files")

    current = get_version()
    new_py_version = increment_twd_version(current)
    new_js_version = convert_python_to_js_version(new_py_version)

    print(f"Bumping version from {current} to {new_py_version} (Python) / {new_js_version} (JS)")

    HERE = Path(__file__).parent.parent.resolve()

    # Bump the Python packages
    for version_file in HERE.glob("python/**/_version.py"):
        content = version_file.read_text().splitlines()
        variable, current_version = content[0].split(" = ")
        if variable != "__version__":
            raise ValueError(
                f"Version file {version_file} has unexpected content;"
                f" expected __version__ assignment in the first line, found {variable}"
            )
        version_file.write_text(f'__version__ = "{new_py_version}"\n')
        print(f"Updated {version_file}")

    # Bump JS packages using lerna
    lerna_cmd = f"jlpm run lerna version --no-push --force-publish --no-git-tag-version {new_js_version}"
    if force:
        lerna_cmd += " --yes"
    run(lerna_cmd)

    # Bump the local package.json file
    path = HERE.joinpath("package.json")
    if path.exists():
        with path.open(mode="r") as f:
            data = json.load(f)

        data["version"] = new_js_version

        with path.open(mode="w") as f:
            json.dump(data, f, indent=2)

        print(f"Updated {path}")
    else:
        raise FileNotFoundError(f"Could not find package.json under dir {path!s}")


if __name__ == "__main__":
    bump()
