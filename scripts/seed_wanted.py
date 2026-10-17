#!/usr/bin/env python3
"""Seed the wanted list from a playlist of titles.

Each title is searched against Plex; only the misses are saved. Safe to run
more than once - titles already captured are reported, never duplicated.

    venv/bin/python scripts/seed_wanted.py --dry-run
    venv/bin/python scripts/seed_wanted.py
    venv/bin/python scripts/seed_wanted.py --file titles.txt
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from db import Database
from scanner.wanted_search import PlexUnavailable, search_and_capture

# The Sunday playlist project - films already handled elsewhere when present.
SUNDAY_PLAYLIST = [
    "The Secret Life of Walter Mitty (2013)", "Chef (2014)",
    "The Grand Budapest Hotel (2014)", "Amelie (2001)",
    "The Intouchables (2011)", "Hunt for the Wilderpeople (2016)",
    "Sing Street (2016)", "About Time (2013)", "The Martian (2015)",
    "Galaxy Quest (1999)", "Back to the Future (1985)",
    "The Princess Bride (1987)", "Stardust (2007)",
    "Pirates of the Caribbean: The Curse of the Black Pearl (2003)",
    "Raiders of the Lost Ark (1981)", "The Truman Show (1998)",
    "Big Fish (2003)", "Knives Out (2019)", "The Nice Guys (2016)",
    "Hot Fuzz (2007)", "School of Rock (2003)",
    "Little Miss Sunshine (2006)", "Crazy Rich Asians (2018)",
    "Notting Hill (1999)", "When Harry Met Sally (1989)",
    "Julie & Julia (2009)", "Everything Everywhere All at Once (2022)",
    "La La Land (2016)", "Cool Runnings (1993)", "The Full Monty (1997)",
    "Project Hail Mary (2026)", "The Lego Movie (2014)",
    "Bridesmaids (2011)", "Anchorman: The Legend of Ron Burgundy (2004)",
    "Forgetting Sarah Marshall (2008)", "Knocked Up (2007)",
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="report without writing")
    parser.add_argument("--file", type=Path, help="file of titles, one per line")
    args = parser.parse_args()

    titles = SUNDAY_PLAYLIST
    if args.file:
        titles = [
            line.strip() for line in args.file.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.startswith("#")
        ]

    db = Database()
    found = added = already = 0
    try:
        for title in titles:
            try:
                result = search_and_capture(db, title, capture=not args.dry_run)
            except PlexUnavailable as e:
                print(f"\nPlex is unavailable, stopping: {e}", file=sys.stderr)
                return 2

            if result["found"]:
                found += 1
                names = ", ".join(f"{m['title']} ({m['year']})" for m in result["matches"][:3])
                print(f"  in library  {title:58s} -> {names}")
            elif result["added_to_wanted"]:
                added += 1
                print(f"  ADDED       {title}")
            elif result["already_wanted"]:
                already += 1
                print(f"  on list     {title:58s} -> already tracked ({result['wanted']['status']})")
            else:
                existing = db.find_wanted(result["title"], result["year"])
                if existing is None:
                    added += 1
                    print(f"  WOULD ADD   {title}")
                else:
                    already += 1
                    print(f"  on list     {title:58s} -> already tracked ({existing['status']})")
    finally:
        db.close()

    verb = "would be added" if args.dry_run else "added"
    print(f"\n{len(titles)} titles checked: {found} already in Plex, "
          f"{added} {verb} to wanted, {already} already on the list.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
