# Using PlexOps

[Documentation home](../README.md) · [Setup](SETUP.md) · [API](API.md)

## Who can do what

| Role/surface | Intended access |
|---|---|
| Visitor | Welcome page, app artwork/manifest, health response, Plex sign-in |
| Shared Plex account | Request/search, their own playlists, household wanted list, their own notifications |
| Server owner | Household features plus dashboard, scans, reports, file changes, posters, announcements, playlists for signed-in members |
| Direct local caller | Operations shortcut for loopback requests without a forwarded-for header; this is a deployment constraint, not an additional authentication factor |

PlexOps derives the owner/shared role from Plex. It does not have a separate
account registration or password database. A share invitation must be accepted
in Plex first. The roster is cached, and availability failures can preserve
previously known roles; do not rely on instant revocation. Read the
[security limits](../SECURITY.md) before remote access.

## Household request page

1. Open `/request` and choose **Sign in with Plex**, or enter its temporary code at Plex's link page.
2. Use an existing account with access to the configured server. Creating a new Plex account does not automatically grant a share.
3. Search for a title, person, genre, or mood. Title matching and keyword fallback need no AI key. Mood interpretation depends on the optional provider and can fall back to keywords.
4. Select results and choose a playlist. The list is created with your own Plex access and should appear in your Plex client after it refreshes.
5. If a title is absent, use its request action. A wanted entry records interest; it does not download or buy the title.

The page can browse and trim your playlists, build a playlist from a
description, show owner announcements, and offer library suggestions. The
owner can build a list for another household member only after that member has
signed in once and left a usable token. The owner feature can consult viewing
history for suggestions; tell household members how you intend to use it.

Age phrases narrow results through metadata filters. This is a convenience,
not a parental-control boundary or a guarantee that every result is suitable.
Plex restrictions and an adult's review remain necessary.

## Wanted list: report versus action

- Dashboard title search can **insert** a wanted entry even though its endpoint uses GET. Household searches can also capture missing files or titles.
- **Recheck** searches Plex and reports playable arrivals. It does not mark entries acquired.
- **Settle** marks playable arrivals acquired and may send configured notifications.
- Manual status choices are `wanted`, `acquired`, and `dismissed`. Entries remain for history.
- Export produces plain-text titles for your own workflow. PlexOps does not acquire files for you.

To preview a personal list of titles, create a local text file with one title
per line, then run:

```sh
venv/bin/python scripts/seed_wanted.py --file /path/to/titles.txt --dry-run
```

Remove `--dry-run` only when you intend to save misses. Omitting `--file` uses a
bundled sample film list, not your own list.

## Owner catalog and reports

Open `/dashboard` on the host. Start with one configured category, then expand:

```sh
curl -X POST http://127.0.0.1:5050/scan/movies
curl http://127.0.0.1:5050/summary
curl 'http://127.0.0.1:5050/media?library=movies'
```

The scan walks readable paths into SQLite. It does not replace a Plex library
scan or verify every file's playback. Quality audit runs ffprobe; gap analysis
contacts TMDb and writes findings. Both can take substantial time on a large
library; there is no universal completion estimate.

```sh
venv/bin/python scripts/full_rescan.py
venv/bin/python scripts/run_gap_analysis.py --movies --limit 5
```

Use the full-rescan command only after verifying the ffprobe path described in
[Setup](SETUP.md). Gap results are recommendations inferred from metadata;
review them before acting. The `4k` and `4k_tv` keys are treated as manually
managed by the scanner's current policy.

## File imports and renames

Back up the database and media affected by an operation. Library mappings and
permissions must match your installation. Preview import with an explicit
staging folder:

```sh
venv/bin/python scripts/import_media.py --staging /path/to/staging --only 'Example Film'
```

The preview contacts Plex and may initialize local database tables, but it
does not copy media. Review the title, destination, free space, and library
mapping. Add `--go` to the same command only when the plan is correct. The
importer copies a selected video, checks size, asks Plex to scan the destination,
and may mark a matching wanted entry acquired and send a notification. It
leaves source media in staging. A successful copy is not proof of Plex playback.

For filename correction, run `/fixer/audit`, inspect `/fixer/suggestions`, and
apply only chosen IDs. `/fixer/apply` and `/fixer/apply-all` rename real files;
they are not previews. The `/command` endpoint also dispatches actions from
text, including scans, playlist creation, and posters. Prefer explicit actions
until you have reviewed the fixed library aliases.

## Appearance and phone installation

The default JPT character images and app icons are bundled. Rose and Graphite
use generic CSS backgrounds. You can supply your own ignored
`dashboard/icons/rae.png` or `dashboard/icons/athena.jpg`; legacy filenames/theme
keys preserve existing preferences. Use images you intend to expose to anyone
who can reach the app; strip metadata first.

Optional helpers require Pillow:

```sh
venv/bin/python scripts/set_rae_image.py /path/to/pet.png
venv/bin/python scripts/make_rae_tile.py /path/to/pet-cutout.png
```

Those commands write local artwork. They are not needed for the normal app.
On iPhone, use Safari's **Share → Add to Home Screen** after signing in.
Notification capability needs a secure, reachable origin, browser support, and
permission; the ordinary loopback setup is a first-use check, not a working
remote phone deployment. See [notifications](INTEGRATIONS.md#notifications).
