#!/usr/bin/env python3
"""."""
import enum
import re
import subprocess
from typing import List


class ReleaseType(enum.Enum):
    NO_RELEASE = 0
    PATCH = 1
    MINOR = 2
    MAJOR = 3


PREFIXES = {
    "fix": ReleaseType.PATCH,
    "feat": ReleaseType.MINOR,
    "major": ReleaseType.MAJOR,
}


def get_git_tags() -> List[str]:
    """."""
    try:
        result = subprocess.run(
            ["git", "tag"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        # Split the output into lines (each tag is on a new line)
        tags = result.stdout.strip().split("\n")
        return tags
    except subprocess.CalledProcessError as e:
        print(f"Error getting git tags: {e.stderr}")
        return []


def get_commit_messages_since(commit_hash) -> List[str]:
    """."""
    try:
        result = subprocess.run(
            ["git", "log", f"{commit_hash}..HEAD", "--pretty=format:%s"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        # Split the output into lines (each line is a commit message)
        commit_messages = result.stdout.strip().split("\n")
        return commit_messages
    except subprocess.CalledProcessError as e:
        print(f"Error getting commit messages: {e.stderr}")
        return []


def compute_release_type(commits: List[str]) -> ReleaseType:
    """."""
    release_type = ReleaseType.NO_RELEASE
    for commit in commits:
        for prefix, prefix_release_type in PREFIXES.items():
            if commit.startswith(f"{prefix}: "):
                # Check whether this is greater than the existing value
                if release_type.value < prefix_release_type.value:
                    release_type = prefix_release_type
    return release_type


def compute_next_version(release_type: ReleaseType, tags: List[str]) -> str:
    """."""
    if len(tags) < 1:
        return "v0.1.0"
    pattern = r'^v\d+\.\d+\.\d+$'
    max_version = (0, 1, 0)
    for tag in tags:
        if re.match(pattern, tag):
            # This tag has valid format (vX.Y.Z)
            major, minor, patch = tag.replace("v", "").split(".")
            major = int(major)
            minor = int(minor)
            patch = int(patch)
            if major > max_version[0] \
                or (major == max_version[0] and minor > max_version[1]) \
                    or (major == max_version[0] and minor == max_version[1] and patch > max_version[2]):
                max_version = (major, minor, patch)
    if release_type == ReleaseType.MAJOR:
        max_version = (max_version[0] + 1, 0, 0)
    elif release_type == ReleaseType.MINOR:
        max_version = (max_version[0], max_version[1] + 1, 0)
    elif release_type == ReleaseType.PATCH:
        max_version = (max_version[0], max_version[1], max_version[2] + 1)
    else:
        pass # NO_RELEASE

    return f"v{max_version[0]}.{max_version[1]}.{max_version[2]}"

if __name__ == "__main__":
    tags = get_git_tags()
    if tags:
        for tag in tags:
            print("The tag:", tag)
            print("Commits since")
            commits = get_commit_messages_since(tag)
            for commit in commits:
                print("Commit:", commit)
                for prefix in PREFIXES:
                    if commit.startswith(f"{prefix}: "):
                        print("PREFIX DETECTED:", commit)
    else:
        print("No tags")
