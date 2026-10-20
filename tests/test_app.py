import json
import tempfile
import threading
import unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import urlopen

from app import create_server


class WebAppTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # A real HTTP server on a free port exercises configuration and routing.
        cls.temp = tempfile.TemporaryDirectory()
        config_path = Path(cls.temp.name) / "app.json"
        config_path.write_text(json.dumps({"message": "Hello <CI>!"}), encoding="utf-8")
        cls.server = create_server("127.0.0.1", 0, config_path)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.url = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()
        cls.temp.cleanup()

    def test_home_uses_config_and_escapes_html(self):
        with urlopen(self.url + "/", timeout=5) as response:
            self.assertEqual(response.status, 200)
            self.assertIn("Hello &lt;CI&gt;!", response.read().decode())

    def test_health(self):
        with urlopen(self.url + "/health", timeout=5) as response:
            self.assertEqual(response.headers.get_content_type(), "application/json")
            self.assertEqual(json.load(response), {"status": "ok"})

    def test_unknown_path(self):
        with self.assertRaises(HTTPError) as caught:
            urlopen(self.url + "/missing", timeout=5)
        self.assertEqual(caught.exception.code, 404)
        caught.exception.close()


if __name__ == "__main__":
    unittest.main()
