# Contributing

[Documentation home](README.md) · [Security reporting](SECURITY.md#reporting-a-vulnerability)

## Work on a demonstration installation

Use fictional accounts, small sample media you may share, and your own local
test services. Do not probe a maintainer's household server or publish its
network details. Set up a virtual environment following [Setup](docs/SETUP.md),
then create a focused branch and keep private configuration/data ignored.

Before a change, read the relevant source and
[architecture notes](docs/ARCHITECTURE.md). Keep the owner and household access
boundaries, account-specific tokens/playlists, wanted-versus-acquired state,
and explicit file/poster writes intact. Do not replace tests with live calls
to Plex, an AI provider, or a media library.

## Offline checks

From the repository root with dependencies installed:

```sh
venv/bin/python -m pip check
venv/bin/python -m unittest discover -s tests -v
git diff --check
```

The current offline regression suite covers a bounded part of Posteria
configuration/login behavior. Passing it does not prove all routes, remote
authorization, filesystem behavior, UI appearance, push delivery, or every
provider integration. Add focused tests for meaningful behavior changed by
your patch. No pytest installation is required by this suite.

`test_connections.py` and scripts under `scripts/` are operator utilities,
not the offline test suite. Some contact real services, catalog private paths,
copy media, or mutate records. Read their arguments and effects first. Use
explicit test paths and a private disposable database when validating them.

For UI changes, record browser/OS, viewport, theme, and whether evidence came
from a fresh browser, an existing service-worker installation, an iPhone
Simulator, or a physical device. Use the
[capture guide](docs/walkthrough-shots/README.txt); no real usernames, hosts,
codes, invitations, image metadata, or private library contents in screenshots.

## Useful issue and pull-request reports

Include:

- What you expected and what happened, with a minimal example.
- Revision, OS, Python/browser version, affected feature, and relevant optional services.
- Sanitized error text and reproduction using fictional inputs.
- What changed, why, tests/checks run, and any remaining limits.

Do not attach `config.yaml`, `.env`, databases, secret/VAPID keys, private logs,
media files, or unredacted captures. Report security flaws privately using
[Security](SECURITY.md), not as public working exploits.

Review `git status`, `git diff`, and the staged diff before submitting. Confirm
that changed documentation links/commands match the source, new configuration
has a generic example, and optional integrations remain optional. Use a GitHub
noreply commit email if you do not intend your personal email to be public.
Keep unrelated refactors and generated/private artifacts out of the change.
