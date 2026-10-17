"""Offline tests: no real config, credentials, Plex, or Posteria service is used."""

import importlib.util
from pathlib import Path
import sys
import types
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class PosteriaConfigurationTests(unittest.TestCase):
    def setUp(self):
        settings = {
            "plex": {"url": "http://127.0.0.1:32400", "token": "test-only"},
            "tmdb": {"base_url": "https://api.themoviedb.org/3", "api_key": ""},
            "posteria": {
                "url": "https://posteria.example/",
                "username": "example-user",
                "password": "example-password",
            },
        }
        spec = importlib.util.spec_from_file_location(
            "poster_manager_under_test", ROOT / "scanner" / "poster_manager.py"
        )
        self.module = importlib.util.module_from_spec(spec)
        with mock.patch.dict(sys.modules, {"config": types.SimpleNamespace(config=settings)}):
            spec.loader.exec_module(self.module)
        self.transport = mock.Mock()
        self.transport.post.return_value = types.SimpleNamespace(status_code=200, text="ok")
        self.session_patch = mock.patch.object(
            self.module.requests, "Session", return_value=self.transport
        )
        self.session_patch.start()
        self.addCleanup(self.session_patch.stop)

    def test_unconfigured_credentials_never_send_a_request(self):
        for username, password in [("", ""), ("example-user", ""), ("", "example-password")]:
            with self.subTest(username=username, has_password=bool(password)):
                with mock.patch.object(self.module, "POSTERIA_USER", username), mock.patch.object(
                    self.module, "POSTERIA_PASS", password
                ):
                    client = self.module.PosteriaSession()
                    self.assertFalse(client.login())
                    self.assertFalse(client.send_to_plex("sample.jpg", "movies")[0])
                    self.assertFalse(client.import_from_plex("sample.jpg", "movies")[0])
        self.transport.post.assert_not_called()

    def test_configured_credentials_are_used_and_successful_login_is_reused(self):
        client = self.module.PosteriaSession()
        self.assertTrue(client.send_to_plex("sample.jpg", "movies")[0])
        self.assertTrue(client.import_from_plex("sample.jpg", "movies")[0])
        self.assertEqual(self.transport.post.call_count, 3)
        login_call = self.transport.post.call_args_list[0]
        self.assertEqual(login_call.args[0], "https://posteria.example/src/include/login.php")
        self.assertEqual(
            login_call.kwargs["data"],
            {"username": "example-user", "password": "example-password"},
        )

    def test_rejected_login_stops_the_poster_operation(self):
        self.transport.post.return_value = types.SimpleNamespace(status_code=403, text="denied")
        client = self.module.PosteriaSession()
        ok, message = client.send_to_plex("sample.jpg", "movies")
        self.assertFalse(ok)
        self.assertIn("config.yaml", message)
        self.assertEqual(self.transport.post.call_count, 1)
        self.assertTrue(self.transport.post.call_args.args[0].endswith("login.php"))


if __name__ == "__main__":
    unittest.main()
