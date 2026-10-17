# Security and deployment limits

[Documentation home](README.md) · [Operations](docs/OPERATIONS.md)

## Intended deployment boundary

Start on the host with Flask bound to `127.0.0.1` and debug disabled. This is a
self-hosted toolkit with powerful file and Plex operations. It has not been
established safe as an untrusted public internet service. Public source
availability is separate from granting strangers access to your installation.

Before any remote use, review and test the full ingress, proxy, authentication,
authorization, abuse controls, and network reachability with a demonstration
installation. A private network/tailnet can reduce reachability, but does not
replace correct application access controls. No Funnel, router forwarding,
public reverse proxy, certificate service, or firewall configuration is
installed by this project. The Flask development server is not a production
hosting configuration.

Known constraints that require further review before public hosting:

- The owner-operations shortcut accepts loopback requests without a forwarded-for header. A local proxy that omits that header can expose privileged operations. Network origin is not proof of an owner's identity.
- Forwarded host/protocol handling trusts a proxy hop. The source does not establish a complete trusted-host, proxy allowlist, or browser-origin defense for arbitrary public deployment.
- Sessions rely on cached Plex sharing information. Provider failures can leave previous roster information in use; immediate revocation is not guaranteed.
- Push subscription destinations are not yet sufficiently constrained for untrusted users.
- Artwork proxying uses the server owner's Plex token, so its library visibility deserves review when shares have different restrictions.
- Rate ceilings and structured model output reduce some abuse; they are not proof against cost overruns, denial of service, injection, or every privacy failure.

These are operator limitations, not a claim that a particular running server
was attacked or that a remote bypass was demonstrated. Do not expose an
installation to untrusted public traffic until these boundaries have been
addressed and independently verified.

## Private data

Keep these out of Git, public artifacts, and support attachments:

- `config.yaml` and `.env`: server tokens, API keys, login credentials, and local paths.
- SQLite data: library paths/titles, requested titles and requesters, Plex IDs/usernames, session identifiers, encrypted Plex tokens, usage records, push subscriptions, and owner notes.
- `data/secret.key`: encryption key for stored Plex tokens. Back up the key and database together, privately. Encryption does not protect against someone who obtains both.
- `data/vapid.json`: push signing identity.
- Logs, exports, backups, private artwork, invitation links, temporary sign-in codes, and real-device screenshots.

Plex passwords are entered at Plex. PlexOps still holds access tokens in order
to act on accounts for playlists. Application sessions currently have a
90-day lifetime. Revoking a Plex token/share and signing out are different
actions; follow Plex's account/server controls when withdrawing access.

Optional AI sends request text, genre vocabulary, and for taste nudges watched
and candidate title names to Anthropic. Plex, TMDb, configured Sonarr/Radarr,
Posteria, and browser push providers receive the requests needed for their
features. Disable optional integrations you do not want to use. Do not place
sensitive personal information into mood requests or announcements.

The app does not provide a complete self-service account/data deletion tool.
An operator handling retention or removal should make a private backup and
review the schema/token implications before changing local data. Do not
delete a database as routine troubleshooting: it contains wanted/history and
session information, not only a rebuildable scan cache.

## Credentials and publishing

Use individual private credentials and restrict host/filesystem access.
Gitignore is a convenience, not a secret-management guarantee. Check staged
files, commit metadata, historical refs, image pixels/metadata, release assets,
and issue attachments before publishing. Removing a secret from the latest
file does not remove history or cached copies. Revoke/rotate exposed secrets
through their provider and verify the replacement; do not test suspect tokens
against a live service to determine ownership.

The repository intentionally excludes personal photographs and original
household captures. Generic art and the synthetic walkthrough illustrations
do not constitute a live installation or device-delivery test.

## Reporting a vulnerability

Use GitHub's private **Security → Report a vulnerability** option if enabled.
If it is unavailable, use a maintainer's published private contact route to
arrange disclosure. Do not open a public issue containing credentials,
personal hosts, private files, or an exploit against a real household server.

Provide the affected revision, route/component, sanitized reproduction using
fictional accounts/test data, impact, and any proposed fix. Do not probe
somebody else's deployment or include working tokens. Ordinary installation
problems can use a public issue following [Contributing](CONTRIBUTING.md).
