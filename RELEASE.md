# Version Release Process

1. Open a PR with the following changes:
    1. Bump the version in [pyproject.toml](pyproject.toml).
    1. Update the [CHANGELOG.md](CHANGELOG.md).
    1. Commit the updates with the message `Bump version to X.Y.Z`.
1. Merge the PR.
1. Locally, sync your clone with GitHub:
    ```
    git fetch origin
    git checkout main
    git reset --hard origin/main
    ```
1. Tag the release:
    ```
    git tag vX.Y.Z -m "vX.Y.Z"
    ```
1. Push changes:
    ```
    git push origin vX.Y.Z
    ```

    This will trigger a workflow on CircleCI that will generate a GitHub release
    and publish the new version to PyPI.
