"""Quick validation: checks Plex connectivity, NAS path access, and a small scan."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from config import config
from plexapi.server import PlexServer


def test_plex():
    print("--- Plex Server ---")
    try:
        plex = PlexServer(config["plex"]["url"], config["plex"]["token"])
        print(f"  Connected: {plex.friendlyName} (v{plex.version})")
        print(f"  Libraries: {[s.title for s in plex.library.sections()]}")
        return True
    except Exception as e:
        print(f"  FAILED: {e}")
        return False


def test_nas_paths():
    print("\n--- NAS Paths ---")
    all_ok = True
    for key, paths in config["nas"].items():
        if isinstance(paths, str):
            paths = [paths]
        for p in paths:
            exists = Path(p).exists()
            status = "OK" if exists else "MISSING"
            print(f"  [{status}] {key}: {p}")
            if not exists:
                all_ok = False
    return all_ok


def test_small_scan():
    movie_paths = config["nas"]["movies"]
    test_path = Path(movie_paths if isinstance(movie_paths, str) else movie_paths[0])
    print(f"\n--- Test Scan: {test_path} ---")
    if not test_path.exists():
        print("  Path not accessible, skipping")
        return False

    from scanner import MediaScanner
    scanner = MediaScanner()
    files = scanner.scan_single_path(str(test_path))
    print(f"  Found {len(files)} media files")
    for f in files[:5]:
        size_mb = f.stat().st_size / (1024 * 1024)
        print(f"    {f.name} ({size_mb:.1f} MB)")
    if len(files) > 5:
        print(f"    ... and {len(files) - 5} more")
    return True


if __name__ == "__main__":
    plex_ok = test_plex()
    nas_ok = test_nas_paths()
    scan_ok = test_small_scan() if nas_ok else False

    print("\n--- Summary ---")
    print(f"  Plex: {'PASS' if plex_ok else 'FAIL'}")
    print(f"  NAS:  {'PASS' if nas_ok else 'FAIL (some paths missing)'}")
    print(f"  Scan: {'PASS' if scan_ok else 'SKIP/FAIL'}")
