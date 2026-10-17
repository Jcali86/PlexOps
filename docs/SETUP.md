# Setup

[Documentation home](../README.md) · [Security](../SECURITY.md)

## Prerequisites

- A Plex Media Server you administer, a working owner token, and at least one library. Shared users need their own Plex accounts and an accepted share on this server.
- Python 3.10 or newer for the source syntax, `venv`, and pip. The pinned dependencies must also support your chosen interpreter and platform; there is no complete compatibility matrix.
- Read access to the media paths from the machine running PlexOps. NAS mounts must already be mounted. Write permission is needed only for operations that copy or rename media.
- Git for obtaining and updating source. Start with a local macOS installation; other platforms need review of media-tool paths and library mappings.
- `ffprobe` for file analysis. The quality auditor currently uses the Sonarr-bundled path `/Applications/Sonarr.app/Contents/MacOS/ffprobe`, while the general analyzer uses the `ffprobe-python` wrapper. Installing FFmpeg on PATH alone does not change that hardcoded auditor path. Start with scan-only mode if it is unavailable.
- Optional: Docker with Compose for Posteria; Pillow for local artwork helper scripts; Chrome for the synthetic screenshot helper. Core web pages do not require these helpers.

## Install into a virtual environment

```sh
git clone https://github.com/Jcali86/PlexOps.git
cd PlexOps
python3 --version
python3 -m venv venv
venv/bin/python -m pip install -r requirements.txt
venv/bin/python -m pip check
cp -n config.example.yaml config.yaml
chmod 600 config.yaml
```

`cp -n` preserves an existing configuration. Edit `config.yaml` locally; do not
paste credentials into an issue, screenshot, shell transcript, or commit.
Install Pillow separately only if you use the image helpers:
`venv/bin/python -m pip install Pillow`.

## Configure the app

The Python app reads **`config.yaml` from the project root**. It does not load
`.env`; that file is used by Docker Compose for optional Posteria. Restart the
Python process after configuration changes.

| Section | What to enter |
|---|---|
| `plex.url` | URL reachable from the app host, usually `http://127.0.0.1:32400` on the same machine |
| `plex.token` | Owner token for the configured Plex server; it grants powerful server access |
| `nas` | Local paths for each library key; each value may be a path or list of paths |
| `tmdb` | Keep the base URL; supply your own API key for discovery, gaps, and poster features |
| `sonarr`, `radarr` | Keep the example structure; add your own local URL/key only if using those integrations |
| `anthropic.api_key` | Leave empty or retain the `YOUR_...` placeholder to use keyword mode; add a key only after reading the data-flow notes |
| `posteria` | Optional Posteria URL and login; see [integrations](INTEGRATIONS.md#posteria) |
| `app` | App name and AI usage ceilings; these are request-count limits, not a monetary budget guarantee |
| `notifications` | Which events may be sent and their wording |
| `flask` | Keep `host: "127.0.0.1"`, port `5050`, and `debug: false` for initial use |
| `database.path` | SQLite path; a relative path is resolved from the process working directory |

Replace every `/path/to/media/...` example with your own readable path. For
categories you do not have, use an empty list such as `concerts: []`. Keep the
section keys used by the source. The importer and command controller have
fixed Plex section-name maps in `scanner/importer.py` and
`api/nl_controller.py`; inspect those before using import, commands, or bulk
operations on differently named libraries.

There is no bundled credential, populated database, private media, or server
connection. A placeholder token/key is not a working setup. TMDb features fail
or degrade when its key is missing; Plex title/library features are the best
first check.

## First local launch

From the repository root:

```sh
venv/bin/python main.py
```

Leave that terminal running, then open:

- <http://127.0.0.1:5050/health> — process response only; `{"status":"ok"}` does not prove Plex or optional providers work.
- <http://127.0.0.1:5050/request> — Plex sign-in and household request page.
- <http://127.0.0.1:5050/dashboard> — owner console. Direct loopback requests have an owner-operations shortcut; use the host account carefully.

Sign in through Plex using the same account you use to watch your shared
library. Your Plex password is entered at Plex, not into PlexOps. The app does
store an encrypted Plex access token for playlists and an application session;
see [private data and backups](../SECURITY.md#private-data).

Stop the foreground app with Ctrl-C. This checkout does not install a macOS
Launch Agent or otherwise register a background service. Follow
[operations](OPERATIONS.md) only after the local foreground setup works.

## Populate a small catalog first

Check the configured paths and make a private backup before large scans.
This owner-only local request indexes files and writes the catalog:

```sh
curl -X POST http://127.0.0.1:5050/scan/movies
```

For all configured paths without ffprobe quality scoring:

```sh
venv/bin/python scripts/full_rescan.py --scan-only
```

These commands contact Plex and read your configured media paths. They are
operator actions, not offline tests. Their output can include private paths and
titles; do not publish it unredacted. Continue with [Using PlexOps](USAGE.md).
