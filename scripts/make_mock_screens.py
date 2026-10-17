#!/usr/bin/env python3
"""Render the walkthrough's system screens, so they need not be photographed.

The shots that show a phone rather than the app - the invite arriving, the VPN
prompt, the share sheet - would otherwise carry real names, numbers and
addresses. These are drawn instead, with placeholder details, at phone
resolution and ready to drop into the edit.

    venv/bin/python scripts/make_mock_screens.py            # placeholders
    venv/bin/python scripts/make_mock_screens.py --host movies.tail1234.ts.net
"""

import argparse
import subprocess
import sys
from pathlib import Path

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
OUT = Path(__file__).resolve().parent.parent / "docs/walkthrough-shots"
W, H = 390, 844
ICON = Path(__file__).resolve().parent.parent / "dashboard/icons/apple-touch-icon.png"


def icon_uri():
    """The app's own icon, inlined - Chrome renders these from file:// pages."""
    import base64
    raw = base64.b64encode(ICON.read_bytes()).decode()
    return f"data:image/png;base64,{raw}"

SHELL = """<!doctype html><meta charset="utf-8">
<style>
  * {{ box-sizing: border-box; margin: 0; }}
  body {{
    width: {w}px; height: {h}px; overflow: hidden;
    font: 16px/1.4 -apple-system, "SF Pro Text", "Helvetica Neue", sans-serif;
    background: {bg}; color: {fg}; -webkit-font-smoothing: antialiased;
  }}
  .status {{
    height: 54px; display: flex; align-items: flex-end; justify-content: space-between;
    padding: 0 22px 6px; font-size: 15px; font-weight: 600; color: {fg};
  }}
  .status .right {{ display: flex; gap: 5px; align-items: center; font-size: 13px; }}
  .bars {{ display: flex; align-items: flex-end; gap: 2px; height: 11px; }}
  .bars i {{ width: 3px; background: {fg}; border-radius: 1px; }}
  {extra}
</style>
<div class="status"><span>9:41</span>
  <span class="right"><span class="bars"><i style="height:4px"></i><i style="height:7px"></i><i style="height:11px"></i></span><span>WiFi</span><span>100%</span></span>
</div>
{body}"""


def frame(name, body, extra="", bg="#000", fg="#fff"):
    path = OUT / f"{name}.html"
    path.write_text(SHELL.format(w=W, h=H, bg=bg, fg=fg, extra=extra, body=body), encoding="utf-8")
    png = OUT / f"{name}.png"
    subprocess.run([
        CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
        f"--screenshot={png}", f"--window-size={W},{H}",
        "--force-device-scale-factor=3", f"file://{path}",
    ], capture_output=True, timeout=90)
    path.unlink(missing_ok=True)
    return png


def build(host, sender, app, tailscale=False):
    made = []
    icon = icon_uri()
    shelf = "".join(
        '<div style="aspect-ratio:2/3;border-radius:8px;background:#1c1c1e"></div>'
        for _ in range(6))

    # The Tailscale onboarding, from before the app was published over
    # Funnel. Kept against the day it goes back to being tailnet-only.
    if tailscale:
        made.append(frame("01-invite", f"""
          <div style="padding:14px 18px;border-bottom:.5px solid #2a2a2c;display:flex;
                      align-items:center;gap:12px">
            <div style="width:34px;height:34px;border-radius:50%;background:#3a3a3c;
                        display:grid;place-items:center;font-size:14px">{sender[0]}</div>
            <b style="font-size:17px">{sender}</b>
          </div>
          <div style="padding:22px 18px;display:flex;flex-direction:column;gap:10px">
            <div style="align-self:flex-start;max-width:80%;background:#26262a;
                        border-radius:20px;padding:11px 15px;font-size:16px">
              Right, here's the film thing I mentioned
            </div>
            <div style="align-self:flex-start;max-width:82%;background:#26262a;
                        border-radius:20px;padding:11px 15px;font-size:16px">
              <span style="color:#4a9eff;text-decoration:underline">
                login.tailscale.com/invite/f2a91c</span><br>
              <span style="color:#9a9a9e;font-size:14px">Tap this first — it lets your phone
              reach my machine</span>
            </div>
            <div style="align-self:flex-start;max-width:80%;background:#26262a;
                        border-radius:20px;padding:11px 15px;font-size:16px">
              Then: <span style="color:#4a9eff;text-decoration:underline">{host}</span>
            </div>
          </div>"""))

        # 02 - install Tailscale (an instruction card, not a store clone)
        made.append(frame("02-install", f"""
          <div style="padding:70px 32px;text-align:center">
            <div style="width:104px;height:104px;border-radius:24px;background:#1b1b1f;
                        border:1px solid #333;margin:0 auto 24px;display:grid;place-items:center;
                        font-size:44px">🔗</div>
            <div style="font-size:26px;font-weight:700;margin-bottom:10px">Tailscale</div>
            <div style="color:#9a9a9e;font-size:16px;line-height:1.5;margin-bottom:30px">
              Free. It's what lets your phone<br>reach the machine at home.
            </div>
            <div style="background:#0a84ff;color:#fff;font-weight:700;font-size:17px;
                        padding:15px;border-radius:14px">Get it from the App Store</div>
          </div>"""))

        # 03 - the Tailscale app on first open
        made.append(frame("03-open-tailscale", """
          <div style="padding:90px 34px 0;text-align:center">
            <div style="width:88px;height:88px;border-radius:20px;background:#1b1b1f;
                        border:1px solid #333;margin:0 auto 26px;display:grid;
                        place-items:center;font-size:38px">\U0001F517</div>
            <div style="font-size:28px;font-weight:700;margin-bottom:12px">Tailscale</div>
            <div style="color:#9a9a9e;font-size:16px;line-height:1.5;margin-bottom:36px">
              Open it once it's installed.<br>You won't need to come back here.
            </div>
            <div style="background:#0a84ff;color:#fff;font-weight:700;font-size:17px;
                        padding:15px;border-radius:14px;margin-bottom:14px">Get Started</div>
            <div style="color:#8e8e93;font-size:15px">Log in</div>
          </div>"""))

        # 04 - accepting the invitation
        made.append(frame("04-accept", f"""
          <div style="padding:20px 0 0">
            <div style="text-align:center;color:#8e8e93;font-size:13px;padding-bottom:14px;
                        border-bottom:.5px solid #2a2a2c">login.tailscale.com</div>
            <div style="padding:56px 30px 0;text-align:center">
              <div style="width:70px;height:70px;border-radius:50%;background:#1b1b1f;
                          border:1px solid #333;margin:0 auto 24px;display:grid;
                          place-items:center;font-size:30px">\u2709\uFE0F</div>
              <div style="font-size:24px;font-weight:700;line-height:1.3;margin-bottom:12px">
                {sender} invited you<br>to their network</div>
              <div style="color:#9a9a9e;font-size:15px;line-height:1.55;margin-bottom:34px">
                Accepting lets this phone reach the machine at home. Nothing else on
                it is shared.</div>
              <div style="background:#fff;color:#000;font-weight:700;font-size:17px;
                          padding:15px;border-radius:12px">Accept invitation</div>
            </div>
          </div>"""))

        # 05 - the VPN permission iOS asks for
        made.append(frame("05-vpn", """
          <div style="height:790px;display:grid;place-items:center;padding:0 34px">
            <div style="background:#2c2c2eee;border-radius:16px;overflow:hidden;width:100%;
                        backdrop-filter:blur(20px)">
              <div style="padding:22px 20px 18px;text-align:center">
                <div style="font-size:17px;font-weight:600;margin-bottom:6px">
                  "Tailscale" Would Like to Add VPN Configurations</div>
                <div style="font-size:13px;color:#c7c7cc;line-height:1.45">
                  All network activity on this iPhone may be filtered or monitored when
                  using VPN.</div>
              </div>
              <div style="display:flex;border-top:.5px solid #48484a">
                <div style="flex:1;padding:14px;text-align:center;color:#0a84ff;font-size:17px;
                            border-right:.5px solid #48484a">Don't Allow</div>
                <div style="flex:1;padding:14px;text-align:center;color:#0a84ff;font-size:17px;
                            font-weight:600">Allow</div>
              </div>
            </div>
          </div>"""))

        # 06 - connected
        made.append(frame("06-connected", """
          <div style="padding:26px 20px">
            <div style="font-size:30px;font-weight:700;margin-bottom:22px">Tailscale</div>
            <div style="background:#1c1c1e;border-radius:14px;padding:18px;display:flex;
                        align-items:center;justify-content:space-between;margin-bottom:14px">
              <div><div style="font-size:17px;font-weight:600">Connected</div>
                <div style="color:#8e8e93;font-size:14px;margin-top:2px">Your phone can reach it now</div></div>
              <div style="width:51px;height:31px;border-radius:16px;background:#30d158;
                          position:relative"><div style="position:absolute;right:2px;top:2px;
                          width:27px;height:27px;border-radius:50%;background:#fff"></div></div>
            </div>
            <div style="background:#1c1c1e;border-radius:14px;padding:16px 18px">
              <div style="color:#8e8e93;font-size:12px;letter-spacing:.5px;margin-bottom:10px">
                MACHINES</div>
              <div style="display:flex;align-items:center;gap:10px;font-size:16px">
                <span style="width:8px;height:8px;border-radius:50%;background:#30d158"></span>
                the-film-machine</div>
            </div>
          </div>"""))

    # 13 - Safari's own bar, where the share icon lives
    made.append(frame("07-sharebutton", f"""
      <div style="height:790px;display:flex;flex-direction:column">
        <div style="flex:1;padding:22px 18px">
          <div style="font-size:22px;font-weight:700;margin-bottom:16px">{app}</div>
          <div style="height:44px;border-radius:12px;background:#1c1c1e;margin-bottom:18px"></div>
          <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:10px">{shelf}</div>
        </div>
        <div style="padding:10px 16px 24px;display:flex;align-items:center;gap:12px;
                    border-top:.5px solid #2a2a2c">
          <div style="color:#8e8e93;font-size:20px">&lsaquo;</div>
          <div style="flex:1;background:#1c1c1e;border-radius:12px;padding:9px 14px;
                      text-align:center;font-size:14px;color:#c7c7cc">{host}</div>
          <div style="width:34px;height:34px;border-radius:50%;
                      box-shadow:0 0 0 3px #ff453a;display:grid;place-items:center">
            <svg viewBox="0 0 24 24" width="19" height="19" fill="none"
                 stroke="#0a84ff" stroke-width="1.9" stroke-linecap="round"
                 stroke-linejoin="round">
              <path d="M12 15V3"/><path d="M8.5 6.5L12 3l3.5 3.5"/>
              <path d="M6 12H4.8A1.8 1.8 0 0 0 3 13.8v5.4A1.8 1.8 0 0 0 4.8 21h14.4a1.8
                       1.8 0 0 0 1.8-1.8v-5.4A1.8 1.8 0 0 0 19.2 12H18"/>
            </svg></div>
          <div style="color:#8e8e93;font-size:20px">&hellip;</div>
        </div>
      </div>"""))

    # 14 - the share sheet, scrolled to the row that matters
    made.append(frame("08-sharesheet", f"""
      <div style="height:790px;display:flex;align-items:flex-end;position:relative">
        <div style="position:absolute;inset:0;padding:22px 18px;opacity:.32">
          <div style="font-size:22px;font-weight:700;margin-bottom:16px">{app}</div>
          <div style="height:44px;border-radius:12px;background:#1c1c1e;margin-bottom:18px"></div>
          <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:10px">
            {shelf}
          </div>
        </div>
        <div style="background:#1c1c1eF2;border-radius:14px 14px 0 0;width:100%;
                    padding:14px 0 30px">
          <div style="width:36px;height:5px;border-radius:3px;background:#48484a;
                      margin:0 auto 16px"></div>
          <div style="padding:0 18px 14px;display:flex;align-items:center;gap:12px;
                      border-bottom:.5px solid #2c2c2e">
            <div style="width:42px;height:42px;border-radius:9px;background:#17191c;
                        display:grid;place-items:center">
              <img src="{icon}" style="width:42px;height:42px;border-radius:9px"></div>
            <div><div style="font-size:16px;font-weight:600">{app}</div>
              <div style="color:#8e8e93;font-size:13px">{host}</div></div>
          </div>
          <div style="padding:6px 18px">
            <div style="display:flex;justify-content:space-between;padding:14px 0;
                        font-size:17px;border-bottom:.5px solid #2c2c2e">
              <span>Add to Reading List</span><span style="color:#8e8e93">📖</span></div>
            <div style="display:flex;justify-content:space-between;padding:14px 0;
                        font-size:17px;border-bottom:.5px solid #2c2c2e">
              <span>Add Bookmark</span><span style="color:#8e8e93">🔖</span></div>
            <div style="display:flex;justify-content:space-between;padding:14px 0;
                        font-size:17px;font-weight:600">
              <span>Add to Home Screen</span><span>➕</span></div>
          </div>
        </div>
      </div>"""))

    # 15 - the confirm dialog
    made.append(frame("09-add", f"""
      <div style="padding:8px 0">
        <div style="display:flex;justify-content:space-between;align-items:center;
                    padding:14px 18px;font-size:17px">
          <span style="color:#0a84ff">Cancel</span>
          <b>Add to Home Screen</b>
          <span style="color:#0a84ff;font-weight:600">Add</span>
        </div>
        <div style="margin:26px 18px;background:#1c1c1e;border-radius:12px;padding:16px;
                    display:flex;align-items:center;gap:14px">
          <img src="{icon}" style="width:60px;height:60px;border-radius:14px;flex:none">
          <div><div style="font-size:17px;font-weight:600">{app}</div>
            <div style="color:#8e8e93;font-size:13px;margin-top:2px">{host}</div></div>
        </div>
        <div style="color:#8e8e93;font-size:13px;padding:0 20px;line-height:1.5">
          An icon will be added to your Home Screen so you can quickly access this website.
        </div>
      </div>"""))

    # 16 - the icon on the home screen
    made.append(frame("10-homescreen", f"""
      <div style="padding:40px 26px">
        <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:26px 18px">
          {"".join(
            '<div style="text-align:center"><div style="width:62px;height:62px;'
            'border-radius:15px;background:#1c1c1e;margin:0 auto 6px"></div>'
            '<div style="font-size:11px;color:#d0d0d2">&nbsp;</div></div>' for _ in range(4))}
          <div style="text-align:center">
            <img src="{icon}" style="width:62px;height:62px;border-radius:15px;
                        margin:0 auto 6px;display:block">
            <div style="font-size:11px;color:#fff">{app}</div>
          </div>
        </div>
      </div>""", bg="#0b0b10"))
    return made


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="the-film-machine.tailnet.ts.net")
    parser.add_argument("--sender", default="Alex")
    parser.add_argument("--app", default="PlexGet")
    parser.add_argument("--with-tailscale", action="store_true",
                        help="also draw the six Tailscale onboarding screens")
    args = parser.parse_args()

    if not Path(CHROME).exists():
        print("Chrome is needed to render these.", file=sys.stderr)
        return 2
    OUT.mkdir(parents=True, exist_ok=True)

    for png in build(args.host, args.sender, args.app, args.with_tailscale):
        size = png.stat().st_size if png.exists() else 0
        print(f"  {png.name:20s} {size:>8,d} bytes")
    print(f"\nWritten to {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
