# Version Release Process

> **⚠️ Automated agents: stop after step 1.** Open the release PR, then hand
> control back to the user. A human must review, approve, and merge the PR
> (step 2). Do **not** merge the PR, create the tag, or push the tag on your
> own — pushing the tag publishes to PyPI and **cannot be undone**. Only
> continue past step 1 after the user explicitly tells you to proceed.

1. Open a PR with the following changes:
    1. Bump the version in [pyproject.toml](pyproject.toml).
    1. Update the [CHANGELOG.md](CHANGELOG.md).
    1. If the change requires a newer Code Ocean server version, update `MIN_SERVER_VERSION` in [client.py](src/codeocean/client.py).
    1. Commit the updates with the message `Bump version to X.Y.Z`.
1. **Review, approve, and merge the PR.** This is a manual step performed by a
   human after CI passes — it is the approval gate for the release.
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
