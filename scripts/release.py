#!/usr/bin/env python3
import enum
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


def get_git_tags():
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


def get_commit_messages_since(commit_hash):
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


def compute_release_type(commits: List[str]):
    release_type = ReleaseType.NO_RELEASE
    for commit in commits:
        for prefix, prefix_release_type in PREFIXES.items():
            if commit.startswith(f"{prefix}: "):
                # Check whether this is greater than the existing value
                if release_type.value < prefix_release_type.value:
                    release_type = prefix_release_type
    return release_type

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
