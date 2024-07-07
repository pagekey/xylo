from unittest.mock import patch, MagicMock

from release import (
    get_git_tags,
    get_commit_messages_since,
    ReleaseType,
    compute_release_type,
    compute_next_version,
)


@patch("subprocess.run")
def test_get_git_tags_with_no_fail_returns_list_of_tags(mock_run):
    # Arrange.
    mock_result = MagicMock()
    mock_result.stdout = "tag1\ntag2"
    mock_run.return_value = mock_result

    # Act.
    result = get_git_tags()

    # Assert.
    mock_run.assert_called_with(
        "git tag".split(),
        check=True,
        stdout=-1,
        stderr=-1,
        text=True,
    )
    assert result[0] == "tag1"
    assert result[1] == "tag2"


@patch("subprocess.run")
def test_get_commit_messages_since_with_valid_hash_returns_list_of_messages(mock_run):
    # Arrange.
    mock_result = MagicMock()
    mock_result.stdout = "Do something\nDo something else"
    mock_run.return_value = mock_result

    # Act.
    result = get_commit_messages_since("HEAD~2")

    # Assert.
    mock_run.assert_called_with(
        "git log HEAD~2..HEAD --pretty=format:%s".split(),
        check=True,
        stdout=-1,
        stderr=-1,
        text=True,
    )
    assert result[0] == "Do something"
    assert result[1] == "Do something else"


def test_compute_release_type_with_no_prefixes_returns_no_release():
    # Arrange.
    commits = ["nothing important", "another poorly formatted commit message"]
    # Act.
    result = compute_release_type(commits)
    # Assert.
    assert result == ReleaseType.NO_RELEASE


def test_compute_release_type_with_only_fix_returns_patch():
    # Arrange.
    commits = ["fix: Somewhat important", "another poorly formatted commit message"]
    # Act.
    result = compute_release_type(commits)
    # Assert.
    assert result == ReleaseType.PATCH


def test_compute_release_type_with_fix_and_feat_returns_minor():
    # Arrange.
    commits = [
        "fix: Somewhat important",
        "feat: another poorly formatted commit message",
    ]
    # Act.
    result = compute_release_type(commits)
    # Assert.
    assert result == ReleaseType.MINOR


def test_compute_release_type_with_major_returns_major():
    # Arrange.
    commits = [
        "fix: Do something somewhat important",
        "feat: Add something",
        "major: Wow this is a big deal",
    ]
    # Act.
    result = compute_release_type(commits)
    # Assert.
    assert result == ReleaseType.MAJOR


def test_compute_next_version_with_no_existing_tags_returns_default_value():
    # Arrange.
    release_type = ReleaseType.MAJOR
    tags = []
    # Act.
    result = compute_next_version(release_type, tags)
    # Assert.
    assert result == "v0.1.0"

def test_compute_next_version_with_no_release_returns_greatest_tag():
    # Arrange.
    release_type = ReleaseType.NO_RELEASE
    tags = ["v0.1.0", "v0.3.0", "v0.2.0", "unrelated-tag"]
    # Act.
    result = compute_next_version(release_type, tags)
    # Assert.
    assert result == "v0.3.0"

def test_compute_next_version_with_patch_bumps_patch_value():
    # Arrange.
    release_type = ReleaseType.PATCH
    tags = ["v0.1.0", "v0.3.2", "v0.2.0", "unrelated-tag"]
    # Act.
    result = compute_next_version(release_type, tags)
    # Assert.
    assert result == "v0.3.3"

def test_compute_next_version_with_minor_bumps_minor_value():
    # Arrange.
    release_type = ReleaseType.MINOR
    tags = ["v0.1.0", "v0.3.2", "v0.2.0", "unrelated-tag"]
    # Act.
    result = compute_next_version(release_type, tags)
    # Assert.
    assert result == "v0.4.0"

def test_compute_next_version_with_major_bumps_major_value():
    # Arrange.
    release_type = ReleaseType.MAJOR
    tags = ["v0.1.0", "v0.3.2", "v0.2.0", "unrelated-tag"]
    # Act.
    result = compute_next_version(release_type, tags)
    # Assert.
    assert result == "v1.0.0"
