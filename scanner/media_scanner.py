import os
from pathlib import Path
from plexapi.server import PlexServer
from config import config


# Libraries where quality upgrades are managed manually
MANUAL_LIBRARIES = {"4k", "4k_tv"}


class MediaScanner:
    """Scans NAS mount paths and Plex libraries for media files."""

    MEDIA_EXTENSIONS = {
        ".mkv", ".mp4", ".avi", ".mov", ".wmv", ".flv", ".m4v",
        ".ts", ".webm", ".mpg", ".mpeg",
    }

    def __init__(self):
        self.plex = PlexServer(config["plex"]["url"], config["plex"]["token"])
        self.nas_paths = config["nas"]

    def _walk_path(self, base_path):
        """Walk a single directory and return all media files."""
        base = Path(base_path)
        if not base.exists():
            return []
        media_files = []
        for root, _dirs, files in os.walk(base):
            for f in files:
                if Path(f).suffix.lower() in self.MEDIA_EXTENSIONS:
                    media_files.append(Path(root) / f)
        return media_files

    def scan_nas_path(self, path_key):
        """Scan all volumes for a library key. Paths are lists."""
        paths = self.nas_paths.get(path_key, [])
        if isinstance(paths, str):
            paths = [paths]
        media_files = []
        for p in paths:
            media_files.extend(self._walk_path(p))
        # Hook: track new files in poster_status for poster management
        self._poster_hook(path_key, media_files)
        return media_files

    def _poster_hook(self, library_key, file_paths):
        """After files are inserted into media_files, add missing entries to poster_status."""
        if not file_paths:
            return
        try:
            from scanner.poster_manager import hook_new_media
            from db import Database
            db = Database()
            added = hook_new_media(db, library_key, file_paths)
            if added:
                print(f"  [poster_hook] Added {added} new items to poster tracking")
            db.close()
        except Exception as e:
            print(f"  [poster_hook] Warning: {e}")

    def scan_single_path(self, raw_path):
        """Scan one specific directory path (for testing)."""
        return self._walk_path(raw_path)

    def scan_all_nas(self):
        """Scan all configured NAS library keys."""
        results = {}
        for key in self.nas_paths:
            results[key] = self.scan_nas_path(key)
        return results

    def is_manual_library(self, library_key):
        """True if this library is manually managed (no auto quality upgrades)."""
        return library_key in MANUAL_LIBRARIES

    def get_plex_libraries(self):
        """Return all Plex library sections."""
        return self.plex.library.sections()

    def get_plex_library_items(self, library_name):
        """Return all items in a specific Plex library."""
        return self.plex.library.section(library_name).all()

    def find_unmatched(self, library_name):
        """Find files on NAS that aren't in the Plex library."""
        plex_items = self.get_plex_library_items(library_name)
        plex_paths = set()
        for item in plex_items:
            for media in item.media:
                for part in media.parts:
                    plex_paths.add(part.file)

        nas_files = set(str(f) for f in self.scan_nas_path(library_name))
        return nas_files - plex_paths
