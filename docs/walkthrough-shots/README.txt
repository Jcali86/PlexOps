Generic PlexGet walkthrough capture guide
========================================

Public documentation must use a demonstration installation with fictional
accounts, sample library content, and an example host such as movies.example.com.
Keep real household hosts, usernames, sign-in codes, invitation links, and
private workflow links out of captures. Remove image metadata before sharing.

Suggested sequence:

  01  Open the demonstration address in Safari.
  02  Show the PlexGet welcome screen.
  03  Show the sign-in card using an obvious sample code.
  04  Show Plex's sign-up page and identify its Sign in link; leave fields blank.
  05  Show the Plex sign-in form with all fields blank.
  06  Show a fictional shared account signed in with sample library content.
  07  Tap Safari's share button.
  08  Choose Add to Home Screen.
  09  Confirm Add.
  10  Open PlexGet from its home-screen icon.

The included 07-sharebutton.png, 08-sharesheet.png, 09-add.png, and
10-homescreen.png are synthetic instruction illustrations. Their host is a
placeholder. They contain no captured household account or device information.
Real installation captures are deliberately not bundled.

To draw your own generic instruction illustrations:
  ./venv/bin/python scripts/make_mock_screens.py --host movies.example.com --sender Alex

The optional --with-tailscale flag also draws example onboarding instructions
for a private tailnet. Any invitations in those illustrations must remain
fictional; never publish a real invitation or reusable access link.
