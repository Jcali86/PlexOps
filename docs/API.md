# API reference

[Documentation home](../README.md) · [Usage](USAGE.md) · [Security](../SECURITY.md)

Routes are implemented in [`api/routes.py`](../api/routes.py). This is a source
reference, not a versioned public API contract. Examples target the local owner
console at `http://127.0.0.1:5050`. Remote clients need the appropriate PlexOps
session; no owner token should be embedded in a browser URL or public command.

**Method alone does not describe side effects.** In particular,
`GET /wanted/search` can save a wanted entry. Schema initialization, session
touches, cache updates, and external calls can occur on otherwise informational
routes. File/poster/playlist/status actions are not dry runs.

## Public shell and sign-in

| Method and path | Purpose |
|---|---|
| `GET /`, `GET /request` | Household page; a private one-time install handoff can establish a session |
| `GET /health` | Process-only health response |
| `GET /manifest.webmanifest`, `GET /sw.js`, `GET /icons/<path:filename>` | App installation, service worker, and public art |
| `POST /auth/start` | Issue temporary Plex sign-in pins; rate limited |
| `GET /auth/poll/<int:pin_id>` | Poll a pin issued by this app and establish a session after authorization |
| `GET /auth/me` | Current signed-in identity and app configuration visible to that user |
| `POST /auth/logout` | End the current app session |

Do not log or share temporary codes, session cookies, or manifest handoff URLs.
The sign-in endpoints contact Plex; they are not an offline authentication mock.

## Household surface

| Method and path | Purpose / main inputs |
|---|---|
| `POST /request/search` | JSON `query`; title/person/keyword/model-assisted search, possibly capturing missing titles |
| `GET /request/showcase`, `GET /request/suggestions`, `GET /request/nudges` | Library shelves and suggestions; nudges can use the AI allowance |
| `GET /request/detail` | Item metadata; `key` identifies the Plex item |
| `GET /request/playlists`, `GET /request/playlist/items` | Person's playlists; items use `name` |
| `POST /request/playlist` | JSON `playlist`, `rating_keys`; create/add, with owner-only `for_user` override |
| `POST /request/playlist/auto` | JSON `query`, optional `count`; build a library playlist |
| `POST /request/playlist/remove` | JSON `playlist`, `rating_keys`; remove from that person's playlist |
| `POST /request/wanted` | JSON `title`, optional `kind` (`show`/film) and `season`; save a request |
| `GET /request/wanted/list` | Household wanted entries and requester labels |
| `GET /request/announcements` | Active owner notes |
| `GET /wanted/thumb` | Artwork proxy; `path` must match supported Plex metadata-art paths |
| `GET /push/key` | Public push key for a signed-in person |
| `POST /push/subscribe`, `POST /push/unsubscribe` | Store/remove that person's push subscription |
| `POST /push/test` | Send a test to that person's subscriptions |

## Owner catalog, analysis, and reports

| Method and path | Purpose / main inputs |
|---|---|
| `GET /dashboard`, `GET /summary`, `GET /libraries`, `GET /media` | Console, counts, Plex libraries, indexed files (`library` filter) |
| `POST /scan/<library>` | Walk a configured NAS library key and update the index |
| `POST /scan/test` | JSON `path`; inspect a single directory without a full scan |
| `POST /analyze` | JSON `file_path`; probe a file and update its media row |
| `POST /analyze/quality` | JSON optional `limit`; write heuristic quality scores |
| `POST /analyze/gaps` | JSON optional `type` (`tv`/`movies`), `limit`; write gap findings |
| `GET /quality`, `GET /gaps` | Filtered stored findings |
| `GET /reports/upgrades`, `GET /reports/gaps`, `GET /reports/posters` | Formatted report data; filters include `library` |
| `GET /search/tmdb` | `q`, optional `type`; external metadata search |
| `GET /sonarr/series`, `GET /radarr/movies` | Query configured optional services |
| `GET /export`, `GET /export/download` | Search-term export; optional `categories`, `library` |

Quality filters include `min_score`, `max_score`, `issue`, and `library`.
Upgrade reports default to scores at or below 70 and accept `limit`. Gap
reports accept `type=tv`, `franchise`, or `alternate`. Export category keys are
defined in [`scanner/export_builder.py`](../scanner/export_builder.py), including
quality issues, missing episodes/seasons, franchise gaps, alternate versions,
and uncurated posters. Exports do not fetch media.

## Owner writes and household management

| Method and path | Action |
|---|---|
| `POST /fixer/audit`, `GET /fixer/suggestions`, `GET /fixer/known-issues` | Produce/review rename suggestions before applying anything |
| `POST /fixer/apply` | JSON `ids`: rename the selected real files |
| `POST /fixer/apply-all` | Apply a confidence group; defaults to `high` |
| `POST /command` | JSON `command`; execute a supported text command, potentially changing Plex |
| `GET /wanted`, `GET /wanted/export` | Wanted queue (`status`) and text export |
| `GET /wanted/search` | `q`; search and save misses |
| `POST /wanted/<int:wanted_id>/status` | JSON `status`: `wanted`, `acquired`, `dismissed` |
| `GET /wanted/recheck`, `POST /wanted/recheck` | Report playable arrivals without reclassifying |
| `POST /wanted/settle` | Mark arrivals acquired and potentially notify |
| `POST /plex/webhook` | Plex `library.new` event invokes settling; local access assumptions require review |
| `GET /members`, `GET /members/<username>/picks` | Members who have signed in and suggestions for them |
| `POST /announce`, `POST /announce/<int:note_id>/retire` | Publish/broadcast or retire an owner note |
| `GET /notifications` | Configured event descriptions and device counts |

## Poster operations

| Method and path | Purpose / main inputs |
|---|---|
| `GET /posters/status` | `state`, `library`, `limit`; inspect tracking |
| `POST /posters/scan` | Optional JSON `libraries`; refresh tracking from Plex |
| `POST /posters/apply-tmdb` | JSON `rating_key` for one item, or `library` for uncurated items |
| `POST /posters/import-mediux` | JSON `yaml_path`; trusted local YAML and referenced images |
| `POST /posters/enforce-locks` | Re-lock tracked curated/TMDb posters in Plex |
| `GET /posters/orphans` | Report local poster files that no longer match Plex items |

States include `uncurated`, `curated`, and `tmdb_default`. Inspect tracking and
back up curated artwork first. The integration needs both a valid TMDb key for
TMDb actions and a configured, authenticated Posteria service where used.
See [Posteria setup](INTEGRATIONS.md#posteria).

## Representative local commands

These owner commands are intended for an installation you control. Audit/scan
commands write local findings; recheck reports arrivals. No example invokes
bulk renames, bulk artwork replacement, or a broadcast.

```sh
curl http://127.0.0.1:5050/summary
curl 'http://127.0.0.1:5050/quality?max_score=70&library=movies'
curl 'http://127.0.0.1:5050/reports/gaps?type=franchise&limit=10'
curl -X POST http://127.0.0.1:5050/fixer/audit \
  -H 'Content-Type: application/json' -d '{"limit":5}'
curl 'http://127.0.0.1:5050/fixer/suggestions?confidence=high'
curl http://127.0.0.1:5050/wanted/recheck
curl 'http://127.0.0.1:5050/posters/status?state=uncurated&limit=10'
```

Common statuses: 400 invalid input, 401 sign-in required/expired, 403 owner-only
or not shared, 409 a member's playlist access needs attention, 429 a limit, and
502/503 upstream trouble. Some optional suggestion failures return 200 with an
`error` or empty results, and action results may report `success: false`; inspect
the response body instead of treating every 2xx as success.
