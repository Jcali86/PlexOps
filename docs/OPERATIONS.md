# Operations and troubleshooting

[Documentation home](../README.md) · [Setup](SETUP.md) · [Security](../SECURITY.md)

## Working directory and process

Run from the project root so a relative `database.path` always identifies the
same database. Start in a foreground terminal first:

```sh
venv/bin/python main.py
```

Ctrl-C stops that foreground process. Configuration changes require a restart.
`/health` confirms only that the Flask process can answer; check Plex sign-in,
library search, and each optional integration separately.

For a background macOS installation, an optional
[Launch Agent template](launchd.plist.example) is supplied. It is not installed
automatically. Replace every `/path/to/PlexOps` in a **local copy** with your
absolute project directory, ensure its Python path exists, create the log
directory, and save it as
`~/Library/LaunchAgents/com.plex-ops.api.plist`.

```sh
mkdir -p logs
plutil -lint "$HOME/Library/LaunchAgents/com.plex-ops.api.plist"
launchctl bootstrap "gui/$(id -u)" "$HOME/Library/LaunchAgents/com.plex-ops.api.plist"
```

Check its private logs under `logs/`. To stop it, including automatic restart:

```sh
launchctl bootout "gui/$(id -u)" "$HOME/Library/LaunchAgents/com.plex-ops.api.plist"
```

Use bootstrap again to start it. Do not run a foreground copy while the
Launch Agent owns the same port/database. This example is a local convenience,
not a production web-server or remote-access configuration.

## Back up before updates and file operations

Stop the app and every scan/import job. Save a private backup outside the
checkout of:

1. `config.yaml`, and `.env` if Posteria is used.
2. The database named by `database.path`, plus any accompanying `-wal` and `-shm` files. An offline copy must be taken only after all writers stop; alternatively use SQLite's supported backup facility.
3. The entire `data/` folder, including token-encryption and VAPID keys if created. Restoring a database without its matching secret key makes stored tokens unreadable.
4. Optional `posteria/` configuration/poster data and your local theme photographs.
5. Independent backups of media you intend to rename, copy over, or change.

Do not treat the database as disposable: scans are rebuildable, but wanted
requests, user sessions, notifications, and announcements are also stored
there. Do not upload a backup as a bug-report attachment.

## Update and rollback

After making the backup and stopping jobs:

```sh
git status --short
git diff
git pull --ff-only
venv/bin/python -m pip install -r requirements.txt
venv/bin/python -m pip check
venv/bin/python -m unittest discover -s tests -v
```

If the checkout has local changes, preserve and review them before pulling.
Do not use a reset or clean command to force an update. Compare the new
`config.example.yaml` with your private configuration and add required fields
without replacing your values. Restart locally, check health/sign-in, and try
a small search or report before restarting long jobs.

Database tables/columns can be created or adjusted when the app opens SQLite;
there is no independent migration manager or guaranteed downgrade path.
Rollback means stopping jobs and restoring a known-compatible code revision,
private configuration, database, and matching keys together. Keep that backup
until the updated installation is accepted. Reverting code alone may not
revert database changes.

Posteria has its own image/configuration upgrade path. Review upstream image
changes, keep an image digest/version record, back up its volumes, and verify
login before invoking poster writes. `docker compose down` does not repair an
invalid Python-side password or make an arbitrary image upgrade safe.

## Common problems

| Symptom | Check and next action |
|---|---|
| `config.yaml` missing or YAML parse error | Create a private copy of the example, keep indentation/spelling, and run from the project root. Never paste the full file into an issue. |
| Missing Python module | Use the intended virtual environment, reinstall `requirements.txt`, run `pip check`. Pillow is separate for optional image helpers. |
| Port 5050 is busy | Stop the existing foreground/service-managed instance, or deliberately choose another port in private config. Identify the process before terminating it. |
| Health is OK, Plex/library calls fail | Check the configured Plex URL from the app host, owner-token validity, server availability, and NAS permissions. A health response does not test any of these. |
| Shared member cannot sign in | Confirm they use the existing shared account, accepted the invitation on this server, and still have access. Request a fresh code after expiry; do not publish the code or token. |
| Repeated sign-in or 401 | A session/token can expire or be revoked. Sign in again. Restoring the wrong encryption key can also make stored tokens unusable. |
| Owner route returns 403 remotely | It requires owner authorization. Do not remove forwarded headers or disable the guard to obtain access. Use the host locally while reviewing remote ingress. |
| Catalog/report is empty | Confirm paths are readable, run a small scan, then the relevant quality/gap analysis. Verify library keys and the source's fixed Plex-name mappings. |
| Quality audit returns no useful probes | Check the auditor's current Sonarr-bundled ffprobe path; general analyzer PATH support does not change it. Use scan-only until the tool path is correctly adapted. |
| TMDb/gap/poster errors | Check your own API key and provider status/limits. Start with a small limit. Do not interpret provider failure as a missing library title. |
| Mood request feels literal | No key, unsupported model, timeout, or schema error can lead to keyword fallback. Exact-title search can still work. Check private logs and provider-account settings. |
| AI limit reached | Limits use rolling hourly/daily windows, not a guaranteed reset at local midnight. Wait for older entries to age out; keep provider spending controls enabled. |
| Posteria login/import fails | Confirm strong credentials match in `.env` and `config.yaml`, restart the affected process, verify loopback URL and container-to-Plex reachability. Do not use a default password or disable auth. |
| Notification test does not arrive | Check home-screen installation on iPhone, secure origin, permission, signed-in account, browser/provider reachability, and device delivery. Keep VAPID identity stable. |
| A title is visible but marked missing/unknown | Check whether the NAS is mounted and readable under the expected name. Do not delete requests or reclassify the library to hide a storage outage. |
| SQLite is locked | Stop overlapping jobs and identify the writer. Make a private backup before repair. Do not delete database/WAL files to clear a lock. |

## Useful local diagnostics

```sh
curl http://127.0.0.1:5050/health
curl http://127.0.0.1:5050/summary
venv/bin/python -m pip check
venv/bin/python -m unittest discover -s tests -v
docker compose ps
```

Only use the Docker command if Posteria is configured. `test_connections.py`
is an **operator diagnostic**: it contacts Plex and reads configured paths,
unlike the offline unit tests. Read it before running it against real media.
Keep logs and command output private; redact usernames, titles, paths, URLs,
tokens, and configuration before sharing a minimal error report.
