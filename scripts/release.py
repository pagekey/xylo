#!/usr/bin/env python3
import subprocess


PREFIXES = ["fix", "feat", "major"]


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
