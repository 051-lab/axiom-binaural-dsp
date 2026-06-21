import importlib.util
import json
import os
import pathlib
import sys
import tempfile
import unittest
import wave


REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
PLAYER_PATH = REPO_ROOT / "tools" / "axiom-player" / "axiom_player.py"


spec = importlib.util.spec_from_file_location("axiom_player", PLAYER_PATH)
axiom_player = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules["axiom_player"] = axiom_player
spec.loader.exec_module(axiom_player)


class AxiomPlayerTests(unittest.TestCase):
    def write_wav(self, path: pathlib.Path) -> None:
        with wave.open(str(path), "wb") as output:
            output.setnchannels(2)
            output.setsampwidth(2)
            output.setframerate(44100)
            output.writeframes(b"\x00\x00\x00\x00" * 32)

    def test_windows_path_conversion(self) -> None:
        path = axiom_player.windows_to_wsl_path(r"C:\Users\soloa\Music\Track.flac")
        self.assertEqual(path.as_posix(), "/mnt/c/Users/soloa/Music/Track.flac")

    def test_track_ids_round_trip(self) -> None:
        path = pathlib.Path("/mnt/c/Users/soloa/Music/example.flac")
        encoded = axiom_player.encode_id(path)
        self.assertEqual(axiom_player.decode_id(encoded), path)

    def test_invalid_track_id_is_rejected(self) -> None:
        with self.assertRaisesRegex(axiom_player.PlayerError, "invalid track ID"):
            axiom_player.decode_id("%%%")

    def test_library_payload_reads_audio_files_and_ignores_other_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            album = root / "Album"
            album.mkdir()
            self.write_wav(album / "Song.wav")
            (album / "notes.txt").write_text("ignore me", encoding="utf-8")

            payload = axiom_player.library_payload(root)

        self.assertEqual(len(payload["tracks"]), 1)
        self.assertEqual(payload["tracks"][0]["albumFolder"], "Album")
        self.assertEqual(payload["tracks"][0]["extension"], "wav")
        self.assertEqual(payload["albums"][0]["trackCount"], 1)

    def test_flask_library_endpoint(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            album = root / "Album"
            album.mkdir()
            self.write_wav(album / "Song.wav")
            app = axiom_player.create_app(root, "unix:/tmp/nonexistent")
            client = app.test_client()

            response = client.get("/api/library")

        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.data)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["tracks"][0]["filename"], "Song.wav")

    def test_mpv_defaults_include_smooth_playback_buffers(self) -> None:
        controller = axiom_player.MpvController(pathlib.Path("/tmp/mpv.sock"), "unix:/tmp/pulse")

        args = controller.command_args()

        self.assertIn("--cache=yes", args)
        self.assertIn("--cache-secs=120", args)
        self.assertIn("--demuxer-readahead-secs=16", args)
        self.assertIn("--audio-buffer=0.2", args)
        self.assertIn("--pulse-buffer=150", args)

    def test_mpv_buffer_env_overrides_are_validated(self) -> None:
        controller = axiom_player.MpvController(pathlib.Path("/tmp/mpv.sock"), "unix:/tmp/pulse")
        previous = os.environ.get("AXIOM_PLAYER_MPV_PULSE_BUFFER")
        os.environ["AXIOM_PLAYER_MPV_PULSE_BUFFER"] = "20"
        try:
            with self.assertRaises(axiom_player.PlayerError):
                controller.command_args()
        finally:
            if previous is None:
                os.environ.pop("AXIOM_PLAYER_MPV_PULSE_BUFFER", None)
            else:
                os.environ["AXIOM_PLAYER_MPV_PULSE_BUFFER"] = previous

    def test_cached_audio_path_copies_track_to_local_state_cache(self) -> None:
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as state_tmp:
            source_root = pathlib.Path(tmp)
            state_root = pathlib.Path(state_tmp)
            source = source_root / "Song.wav"
            self.write_wav(source)
            player = axiom_player.AxiomPlayer(source_root, "unix:/tmp/nonexistent")
            player.cache_root = state_root / "audio-cache"

            cached = player.cached_audio_path(source)

        self.assertNotEqual(cached, source)
        self.assertTrue(cached.name.endswith(".wav"))
        self.assertTrue(cached.parent.name == "audio-cache")

    def test_cached_audio_path_can_be_disabled(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source_root = pathlib.Path(tmp)
            source = source_root / "Song.wav"
            self.write_wav(source)
            player = axiom_player.AxiomPlayer(source_root, "unix:/tmp/nonexistent")
            previous = os.environ.get("AXIOM_PLAYER_LOCAL_AUDIO_CACHE")
            os.environ["AXIOM_PLAYER_LOCAL_AUDIO_CACHE"] = "0"
            try:
                cached = player.cached_audio_path(source)
            finally:
                if previous is None:
                    os.environ.pop("AXIOM_PLAYER_LOCAL_AUDIO_CACHE", None)
                else:
                    os.environ["AXIOM_PLAYER_LOCAL_AUDIO_CACHE"] = previous

        self.assertEqual(cached, source)

    def test_play_track_rejects_file_outside_library(self) -> None:
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as outside_tmp:
            root = pathlib.Path(tmp)
            outside = pathlib.Path(outside_tmp) / "Outside.wav"
            self.write_wav(outside)
            player = axiom_player.AxiomPlayer(root, "unix:/tmp/nonexistent")

            with self.assertRaisesRegex(axiom_player.PlayerError, "outside the configured music library"):
                player.play_track(axiom_player.encode_id(outside))

    def test_play_track_rejects_symlink_that_escapes_library(self) -> None:
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as outside_tmp:
            root = pathlib.Path(tmp)
            outside = pathlib.Path(outside_tmp) / "Outside.wav"
            self.write_wav(outside)
            link = root / "Linked.wav"
            link.symlink_to(outside)
            player = axiom_player.AxiomPlayer(root, "unix:/tmp/nonexistent")

            with self.assertRaisesRegex(axiom_player.PlayerError, "outside the configured music library"):
                player.play_track(axiom_player.encode_id(link))

    def test_flask_play_endpoint_rejects_file_outside_library(self) -> None:
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as outside_tmp:
            root = pathlib.Path(tmp)
            outside = pathlib.Path(outside_tmp) / "Outside.wav"
            self.write_wav(outside)
            app = axiom_player.create_app(root, "unix:/tmp/nonexistent")
            client = app.test_client()

            response = client.post("/api/play", json={"id": axiom_player.encode_id(outside)})

        self.assertEqual(response.status_code, 400)
        payload = json.loads(response.data)
        self.assertFalse(payload["ok"])
        self.assertIn("outside the configured music library", payload["error"])

    def test_player_host_must_be_loopback(self) -> None:
        self.assertTrue(axiom_player.is_loopback_host("127.0.0.1"))
        self.assertTrue(axiom_player.is_loopback_host("::1"))
        self.assertTrue(axiom_player.is_loopback_host("localhost"))
        self.assertFalse(axiom_player.is_loopback_host("0.0.0.0"))
        self.assertFalse(axiom_player.is_loopback_host("192.168.1.10"))


if __name__ == "__main__":
    unittest.main()
