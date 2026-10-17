# Optional integrations

[Documentation home](../README.md) · [Setup](SETUP.md) · [Security](../SECURITY.md)

Configure services you actually use. Keep the example section structure in
`config.yaml`, leave unused credentials empty, and expect unavailable features
to degrade or return an error. There is no automatic service provisioning.

## Anthropic

The core title/keyword path works without a key. For free-form interpretation,
set `anthropic.api_key` in your private `config.yaml`, or provide
`ANTHROPIC_API_KEY` to the Python process. The environment value takes
precedence. Python does not load `.env` automatically. Never put a key into a
committed file or pass one in a support request.

The model translates requests into structured library filters. Searches select
from Plex rather than using model-invented titles. Optional taste nudges send
up to 20 recently watched title names and a pool of unwatched candidate title
names to Anthropic; ordinary interpretation sends the request text and library
genre vocabulary. Do not enable it without accepting that data flow and
telling household members.

`app.limits` provides per-user hourly/daily request ceilings, an overall daily
request ceiling, and a query-length cap. These are rolling usage counts, not
an exact currency budget. Configure provider-side spending controls as well.
The model identifier is currently a source constant in
`api/request_assistant.py`; availability depends on your provider account.
Provider errors, timeouts, or schema failures may fall back to keywords, so a
successful search does not prove the model was called.

## TMDb

Set `tmdb.api_key` for metadata lookup, gap analysis, external title discovery,
and poster features. Retain the example API base URL unless you deliberately
review a change. TMDb results are catalog information, not proof that media is
present or playable in your Plex library. API errors and request limits should
be investigated before rerunning large gap jobs.

## Sonarr and Radarr

The analyzer can query configured Sonarr/Radarr servers through their local
URLs and API keys. This app does not configure them or automatically download
wanted titles. Do not publish their management ports or keys. They are optional
for the request page; the quality auditor separately has a current
Sonarr-bundled ffprobe path assumption described in [Setup](SETUP.md).

## Posteria

Posteria is an optional poster-management service. Poster changes can replace
and lock Plex artwork, so back up your preferred posters and test a single item
before a bulk operation. The main request/search flow does not require it.

From the repository root:

```sh
cp -n .env.example .env
chmod 600 .env
```

Edit `.env` locally with a strong `POSTERIA_PASSWORD`, a chosen
`POSTERIA_USER`, and the Plex server token. Compose requires the password and
Plex token; it does not ship usable credentials. Put the **same Posteria
username and password** in the `posteria` section of `config.yaml`, with URL
`http://127.0.0.1:1818`. The Python poster client reads `config.yaml`, while
Compose reads `.env`; changing one does not update the other.

```sh
docker compose up -d posteria
docker compose ps
```

The Compose service binds Posteria to host loopback port 1818. Open
<http://127.0.0.1:1818> on the host and verify sign-in. Confirm the container
can reach your Plex URL (`host.docker.internal` is used in the supplied
configuration), volume permissions, and timezone. Do not expose port 1818 or
disable authentication to work around a connection/login error.

The Python poster client requires configured credentials and a successful
login before sending/importing posters. It has no default-password fallback.
If the two configurations differ, correct them and restart the relevant
services. Do not change your strong password to a public example value.

Poster files live under `posteria/posters/`, with configuration under
`posteria/config/`. Both are ignored by Git. The supplied image tag is
`latest`; review and pin an upstream image version/digest for an installation
where repeatable upgrades matter. No Posteria image or runtime compatibility
test is claimed by the repository documentation.

Use `/posters/status` and `/posters/scan` to inspect tracking. Applying TMDb
artwork, importing a local Mediux YAML set, and enforcing locks are explicit
owner actions. Local YAML and its referenced images must be trusted. Auto
import is disabled in Compose; PlexOps invokes the integration when requested.

## Notifications

Web push is optional. It requires a browser that supports it, notification
permission, a stable secure origin reachable by the phone, and access to the
browser's push provider. On iPhone, install through Safari's **Add to Home
Screen** and open that icon before enabling notifications.

VAPID keys are created in ignored `data/vapid.json`; keep this with the private
backup. An optional `app.contact` value can set the VAPID contact identifier.
Use a deliberate operator contact value, not somebody else's private address.

The `notifications` configuration controls available events and wording:

- `arrived`: a requested title is playable and its wanted entry is settled.
- `requested`: a household request is recorded; intended for the owner.
- `file_missing`: a lookup detects a missing file; intended for the owner.
- `test`: the signed-in person explicitly requests a test.

Announcements are owner-triggered broadcasts. `/wanted/recheck` only reports;
`/wanted/settle` changes statuses and can notify. An optional Plex webhook
handler reacts to `library.new`; configure it only after reviewing local access
and authentication assumptions. There is no background scheduler installed by
this checkout, so arrival notification is not a guaranteed automatic service.

The current push subscription implementation needs further destination
validation before untrusted users are admitted. Keep remote use confined to
trusted accounts/network access and read [Security](../SECURITY.md). A test
response is not proof of physical delivery; check the target device.
