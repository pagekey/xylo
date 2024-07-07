#!/usr/bin/env python3
import subprocess


def get_git_tags():
    try:
        result = subprocess.run(
            ['git', 'tag'],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        # Split the output into lines (each tag is on a new line)
        tags = result.stdout.strip().split('\n')
        return tags
    except subprocess.CalledProcessError as e:
        print(f"Error getting git tags: {e.stderr}")
        return []

if __name__ == "__main__":
    tags = get_git_tags()
    if tags:
        for tag in tags:
            print("The tag:",tag)
    else:
        print("No tags")
