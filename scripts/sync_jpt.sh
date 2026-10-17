#!/bin/bash
# Copy JPT's faces from iCloud into the app's icons folder.
#
# The art lives in iCloud so it can be added from a phone, named however is
# natural - "Good idea.png", "Thinking .png". This takes whatever is there,
# tidies the name into a slug the page can ask for (jpt-good-idea.png), and
# shrinks it on the way.
#
# The shrinking matters: the originals are ~850px tall and ~380KB, and the
# page never draws one bigger than 168px. Sent whole to a phone on mobile
# data that is most of a megabyte for a picture of a man shrugging.
#
# iCloud files can be placeholders that have not been downloaded, so anything
# missing is nudged and waited for rather than copied as a stub.

set -u

SRC="$HOME/Library/Mobile Documents/com~apple~CloudDocs/JPT"
DEST="$(cd "$(dirname "$0")/.." && pwd)/dashboard/icons"
HEIGHT=420          # 2.5x the largest size the page draws, for retina

[ -d "$SRC" ] || { echo "No iCloud JPT folder at $SRC"; exit 1; }

# Wake anything iCloud has left as a placeholder.
for stub in "$SRC"/.*.png.icloud; do
    [ -e "$stub" ] || continue
    name=$(basename "$stub" .icloud); name=${name#.}
    echo "  fetching $name from iCloud..."
    /usr/bin/brctl download "$SRC/$name" 2>/dev/null
done
for _ in 1 2 3 4 5; do
    ls "$SRC"/.*.png.icloud >/dev/null 2>&1 || break
    sleep 1
done

copied=0
saved_before=0
saved_after=0
shopt -s nullglob
for file in "$SRC"/*.png "$SRC"/*.PNG; do
    base=$(basename "$file")
    base=${base%.[pP][nN][gG]}
    # "Good idea" -> good-idea, "Thinking " -> thinking
    slug=$(printf '%s' "$base" | tr '[:upper:]' '[:lower:]' \
           | sed 's/[^a-z0-9]\{1,\}/-/g; s/^-//; s/-$//')
    [ -n "$slug" ] || continue
    out="$DEST/jpt-$slug.png"
    before=$(stat -f%z "$file")
    if sips --resampleHeight "$HEIGHT" "$file" --out "$out" >/dev/null 2>&1; then
        after=$(stat -f%z "$out")
        saved_before=$((saved_before + before))
        saved_after=$((saved_after + after))
        copied=$((copied + 1))
        printf '  %-14s %4dKB -> %3dKB\n' "$slug" $((before / 1024)) $((after / 1024))
    else
        echo "  $slug: could not be read"
    fi
done

echo
echo "$copied faces in place: $((saved_before / 1024))KB of art served as $((saved_after / 1024))KB."
[ "$copied" -gt 0 ] && echo "Live straight away - no restart needed."
