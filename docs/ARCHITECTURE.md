# Architecture and implementation notes

[Documentation home](../README.md) · [API](API.md) · [Contributing](../CONTRIBUTING.md)

## Source map

| Path | Responsibility |
|---|---|
| `main.py`, `config.py`, `config.example.yaml` | Flask entry point, YAML loading, generic configuration |
| `api/routes.py` | HTTP routes, request guard, sessions, household/owner orchestration |
| `api/plex_auth.py`, `api/secrets_store.py` | Plex PIN sign-in, cached sharing roster, encrypted stored account access |
| `api/request_assistant.py`, `api/suggestions.py` | Title/person/genre/mood matching, structured model translation, library suggestions |
| `api/limits.py`, `api/push.py` | AI request accounting and optional notifications |
| `api/user_library.py`, `api/tmdb_lookup.py`, `api/nl_controller.py` | Per-person playlists, metadata lookup, owner text commands |
| `db/database.py` | SQLite tables and queries; opening it can initialize/adjust schema |
| `scanner/media_scanner.py`, `analyzer/media_analyzer.py` | Filesystem/Plex inventory and individual media probing |
| `scanner/quality_auditor.py`, `scanner/gap_analysis.py`, `scanner/reports.py` | Heuristic quality scoring, metadata gap inference, reports |
| `scanner/wanted_search.py`, `scanner/importer.py` | Wanted capture/availability checks and explicit media-copy workflow |
| `scanner/plex_fixer.py`, `scanner/poster_manager.py`, `scanner/export_builder.py` | File renames, poster coordination, search-term exports |
| `dashboard/index.html`, `dashboard/request.html`, `dashboard/sw.js` | Owner console, household PWA, shell/push service worker |
| `scripts/`, `tests/` | Operator tools, optional art helpers, offline regression checks |

## Data flow and design choices

The owner configuration connects to Plex and optional services. Filesystem
scans write local file paths and library keys to SQLite. Plex metadata supplies
the visible title/catalog and account-specific playlist access. Wanted rows
track requests separately from acquired media; a title listed in Plex can
still have an unavailable backing file.

Mood interpretation produces filters, not a list of invented films. The
library search executes those filters against real items. Genre conjunctions
are sent to Plex because abbreviated search objects may not carry complete
genre tags. Results are drawn across libraries rather than trusting that
ratings from different libraries are directly comparable. Structured output
and a keyword fallback make provider failure survivable; they do not establish
every model/security property.

Quality scores are configurable only through the source's present rules and
reflect codec/container/resolution/bitrate/audio heuristics. They are a
prioritization aid, not a visual-quality measurement. Gap/alternate-version
results are metadata inferences and can need human correction. The scanner
marks `4k`/`4k_tv` for manual management; do not assume every report category
has the same upgrade policy.

Posters are tracked locally and coordinated through Posteria for file import
and delivery. Curated/default poster states and locks are tracked separately
from file quality. Inspect current state before replacing artwork; exporting
or scanning tracking is different from applying a poster or re-locking it.

The poster filename builder includes the Plex rating key and library title so
Posteria can associate a stored image with its Plex item. Preserve those
conventions when moving or curating the local poster store. PlexOps supplies
image-only posters rather than adding overlay badges. The Compose setting
`PLEX_REMOVE_OVERLAY_LABEL=false` leaves Posteria's overlay-label removal
disabled; it is not a promise about existing artwork in Plex.

The household service worker caches only its shell and artwork, with
network-first shell refresh and a cache fallback for a slow/offline request.
Person-specific API responses and the per-install handoff manifest are
deliberately outside that shell cache. An offline-looking page does not mean
search/playlists can operate without the server. For shell changes, review the
cache version and test an existing installation as well as a fresh browser.

## Customization and portability

Keep tokens, real paths, optional photographs, and generated state in ignored
local files. Theme names Rose/Graphite use legacy `rae`/`athena` keys for
compatibility; their optional images have generic CSS fallbacks. Character
assets and API behavior are separate from these optional themes.

Library mappings appear in multiple places: the importer, poster manager, and
owner command aliases. Changing a library name in YAML alone does not update
all Plex section mappings. The quality auditor also has a macOS-specific
Sonarr ffprobe path. These are explicit adaptation points, not evidence of
support for arbitrary NAS layouts or operating systems.

Keep the owner console and the household page independently usable. Check CSS
specificity around theme backdrops/dialogs, escaping in text and attribute
contexts, and that navigation/API responses are not confused with cached
shell HTML. Desktop rendering alone does not establish iPhone Safari,
home-screen installation, push delivery, or actual device acceptance.
