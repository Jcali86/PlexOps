# PlexOps

PlexOps is a self-hosted Plex library toolkit with a phone-friendly **PlexGet**
request page. It catalogs your media, reports quality and collection gaps,
tracks wanted titles, creates Plex playlists, and offers optional poster tools.
It works with media you supply; it is not a downloader.

**Start locally.** This is a macOS-oriented project, not a hardened public
hosting package. Keep the default `127.0.0.1` bind, and read
[Security and deployment limits](SECURITY.md) before giving anyone network
access. A public source repository does not make an installation safe to expose
to untrusted visitors.

## Get started

1. Read [Setup](docs/SETUP.md) for prerequisites, installation, and private configuration.
2. Start the app from the project root with `venv/bin/python main.py`.
3. Open <http://127.0.0.1:5050/request> for the household page or
   <http://127.0.0.1:5050/dashboard> for the owner console.
4. Follow [Using PlexOps](docs/USAGE.md) to scan a small library and try a playlist.

The checkout includes example configuration, generic artwork, and synthetic
walkthrough illustrations. You supply your Plex server, credentials, media
paths, and optional services. It does not install a Launch Agent, create Plex
shares, configure a reverse proxy, or provision an AI account.

## Documentation

| Guide | What it covers |
|---|---|
| [Setup](docs/SETUP.md) | Python, media tools, configuration, first launch, first checks |
| [Using PlexOps](docs/USAGE.md) | Owner and household roles, searches, requests, playlists, file operations |
| [Optional integrations](docs/INTEGRATIONS.md) | Anthropic, TMDb, Sonarr/Radarr, Posteria, notifications |
| [Operations and troubleshooting](docs/OPERATIONS.md) | Backups, updates, service management, recovery, common errors |
| [API reference](docs/API.md) | Route groups, side effects, representative local commands |
| [Architecture](docs/ARCHITECTURE.md) | Source map, data flow, customization, implementation limits |
| [Security](SECURITY.md) | Private data, deployment boundaries, responsible reporting |
| [Contributing](CONTRIBUTING.md) | Development workflow, safe verification, useful issue reports |
| [Walkthrough capture guide](docs/walkthrough-shots/README.txt) | Fictional accounts and privacy-safe documentation captures |

## Feature boundaries

- Plex sign-in is intended to admit the owner and accounts shared on the configured server.
- Household playlists use the signed-in person's Plex access; owner tools can change files and metadata.
- Exact-title and keyword searches work without an AI key. Free-form interpretation is optional and may fall back to keywords.
- Missing-title searches can add wanted entries. Rechecking reports arrivals; settling marks entries acquired and can notify people.
- Media import previews a copy plan by default. Applying renames, importing files, changing posters, and broadcasting notes are consequential operations.
- Sonarr/Radarr and Posteria are optional. They are not required just to open the request page.

The current implementation has fixed library-name mappings and macOS-specific
media-tool assumptions. Supported features are described from source; this
repository does not claim a complete compatibility matrix, a verified live
installation, or an independently certified public deployment. See the guides
before applying bulk changes to a real library.
