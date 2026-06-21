#!/usr/bin/env python3
"""Local browser player for Axiom WSL/JDSP listening."""

from __future__ import annotations

import argparse
import base64
import hashlib
import ipaddress
import json
import os
import pathlib
import shutil
import socket
import subprocess
import sys
import time
import urllib.request
from dataclasses import dataclass
from typing import Any

from flask import Flask, jsonify, request, send_from_directory
from mutagen import File as MutagenFile


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
APP_ROOT = pathlib.Path(__file__).resolve().parent
STATIC_ROOT = APP_ROOT / "static"
DEFAULT_LIBRARY = pathlib.Path("/mnt/c/Users/soloa/Music")
STATE_DIR = pathlib.Path.home() / ".local/state/axiom-engineering/player"
DEFAULT_PULSE_SERVER = "unix:/tmp/jdsp-win/native"
DEFAULT_JDSP_UI = "http://127.0.0.1:6080/vnc.html?autoconnect=true&resize=scale&host=127.0.0.1&port=6080"
SUPPORTED_EXTENSIONS = {".wav", ".flac", ".mp3", ".m4a", ".aac", ".ogg", ".opus", ".wma"}
DEFAULT_MPV_AUDIO_BUFFER_SECONDS = 0.2
DEFAULT_MPV_PULSE_BUFFER_MS = 150
DEFAULT_MPV_DEMUXER_READAHEAD_SECONDS = 16.0
DEFAULT_MPV_CACHE_SECONDS = 120.0
DEFAULT_ROUTE_STATUS_CACHE_SECONDS = 10.0
DEFAULT_JDSP_VNC_HELPER = pathlib.Path.home() / ".local/bin/jamesdsp-vnc"


class PlayerError(RuntimeError):
    pass


def run(command: list[str], label: str, *, env: dict[str, str] | None = None, timeout: float = 30.0) -> subprocess.CompletedProcess[str]:
    try:
        result = subprocess.run(command, text=True, capture_output=True, env=env, timeout=timeout, check=False)
    except FileNotFoundError as exc:
        raise PlayerError(f"{label} failed: command not found: {command[0]}") from exc
    except subprocess.TimeoutExpired as exc:
        raise PlayerError(f"{label} timed out after {timeout:g} seconds") from exc
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or f"exit {result.returncode}"
        raise PlayerError(f"{label} failed: {detail}")
    return result


def pulse_env(pulse_server: str) -> dict[str, str]:
    env = os.environ.copy()
    env["PULSE_SERVER"] = pulse_server
    return env


def env_float(name: str, default: float, *, minimum: float) -> float:
    value = os.environ.get(name)
    if value is None:
        return default
    try:
        parsed = float(value)
    except ValueError as exc:
        raise PlayerError(f"{name} must be a number") from exc
    if parsed < minimum:
        raise PlayerError(f"{name} must be >= {minimum:g}")
    return parsed


def env_int(name: str, default: int, *, minimum: int, maximum: int | None = None) -> int:
    value = os.environ.get(name)
    if value is None:
        return default
    try:
        parsed = int(value)
    except ValueError as exc:
        raise PlayerError(f"{name} must be an integer") from exc
    if parsed < minimum or (maximum is not None and parsed > maximum):
        upper = f" and <= {maximum:g}" if maximum is not None else ""
        raise PlayerError(f"{name} must be >= {minimum:g}{upper}")
    return parsed


def env_bool(name: str, default: bool) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() not in ("0", "false", "no", "off")


def windows_to_wsl_path(value: str) -> pathlib.Path:
    if len(value) >= 3 and value[1] == ":" and value[2] in ("/", "\\"):
        drive = value[0].lower()
        rest = value[2:].replace("\\", "/")
        return pathlib.Path("/mnt") / drive / rest.lstrip("/")
    return pathlib.Path(value).expanduser()


def encode_id(path: pathlib.Path) -> str:
    return base64.urlsafe_b64encode(str(path).encode("utf-8")).decode("ascii").rstrip("=")


def decode_id(value: str) -> pathlib.Path:
    try:
        padding = "=" * (-len(value) % 4)
        decoded = base64.b64decode((value + padding).encode("ascii"), altchars=b"-_", validate=True)
        return pathlib.Path(decoded.decode("utf-8"))
    except (ValueError, UnicodeDecodeError) as exc:
        raise PlayerError("invalid track ID") from exc


def is_loopback_host(host: str) -> bool:
    if host.lower() == "localhost":
        return True
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False


def audio_files(root: pathlib.Path) -> list[pathlib.Path]:
    if not root.is_dir():
        return []
    return sorted(path for path in root.rglob("*") if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS)


def first_tag(tags: Any, *names: str) -> str:
    if not tags:
        return ""
    lowered = {str(key).lower(): value for key, value in tags.items()}
    for name in names:
        value = lowered.get(name.lower())
        if isinstance(value, list) and value:
            return str(value[0])
        if value:
            return str(value)
    return ""


def track_metadata(path: pathlib.Path, root: pathlib.Path) -> dict[str, Any]:
    rel_path = path.relative_to(root).as_posix()
    album_folder = path.parent.name if path.parent != root else "Music"
    title = path.stem
    artist = ""
    album = album_folder
    track_no = ""
    duration = None
    try:
        audio = MutagenFile(path, easy=True)
        if audio:
            title = first_tag(audio.tags, "title") or title
            artist = first_tag(audio.tags, "artist", "albumartist")
            album = first_tag(audio.tags, "album") or album
            track_no = first_tag(audio.tags, "tracknumber")
            if audio.info and getattr(audio.info, "length", None):
                duration = float(audio.info.length)
    except Exception:
        pass
    return {
        "id": encode_id(path),
        "path": str(path),
        "relPath": rel_path,
        "filename": path.name,
        "title": title,
        "artist": artist,
        "album": album,
        "albumFolder": album_folder,
        "trackNumber": track_no,
        "duration": duration,
        "extension": path.suffix.lower().lstrip("."),
    }


def library_payload(root: pathlib.Path) -> dict[str, Any]:
    tracks = [track_metadata(path, root) for path in audio_files(root)]
    albums: dict[str, dict[str, Any]] = {}
    for track in tracks:
        album_id = track["albumFolder"]
        album = albums.setdefault(
            album_id,
            {
                "id": album_id,
                "title": track["album"] or album_id,
                "folder": album_id,
                "artist": track["artist"],
                "trackCount": 0,
            },
        )
        album["trackCount"] += 1
        if not album["artist"] and track["artist"]:
            album["artist"] = track["artist"]
    return {
        "root": str(root),
        "albums": sorted(albums.values(), key=lambda item: item["folder"].lower()),
        "tracks": tracks,
    }


@dataclass
class MpvController:
    socket_path: pathlib.Path
    pulse_server: str
    process: subprocess.Popen[str] | None = None

    def command_args(self) -> list[str]:
        audio_buffer = env_float(
            "AXIOM_PLAYER_MPV_AUDIO_BUFFER",
            DEFAULT_MPV_AUDIO_BUFFER_SECONDS,
            minimum=0.2,
        )
        pulse_buffer = env_int(
            "AXIOM_PLAYER_MPV_PULSE_BUFFER",
            DEFAULT_MPV_PULSE_BUFFER_MS,
            minimum=100,
            maximum=2000,
        )
        demuxer_readahead = env_float(
            "AXIOM_PLAYER_MPV_DEMUXER_READAHEAD",
            DEFAULT_MPV_DEMUXER_READAHEAD_SECONDS,
            minimum=1.0,
        )
        cache_seconds = env_float(
            "AXIOM_PLAYER_MPV_CACHE_SECS",
            DEFAULT_MPV_CACHE_SECONDS,
            minimum=5.0,
        )
        return [
            "mpv",
            "--idle=yes",
            "--no-terminal",
            "--no-video",
            "--force-window=no",
            "--audio-display=no",
            "--really-quiet",
            "--cache=yes",
            f"--cache-secs={cache_seconds:g}",
            f"--demuxer-readahead-secs={demuxer_readahead:g}",
            f"--audio-buffer={audio_buffer:g}",
            f"--pulse-buffer={pulse_buffer}",
            "--input-ipc-server=" + str(self.socket_path),
            "--audio-device=pulse/JamesDSP",
            "--volume=70",
        ]

    def is_running(self) -> bool:
        return self.process is not None and self.process.poll() is None and self.socket_path.exists()

    def start(self) -> None:
        if self.is_running():
            return
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        if self.socket_path.exists():
            self.socket_path.unlink()
        env = pulse_env(self.pulse_server)
        self.process = subprocess.Popen(
            self.command_args(),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            text=True,
            env=env,
        )
        deadline = time.time() + 5.0
        while time.time() < deadline:
            if self.socket_path.exists() and self.process.poll() is None:
                return
            time.sleep(0.05)
        raise PlayerError("mpv did not create its IPC socket")

    def command(self, command: list[Any]) -> Any:
        self.start()
        return self.commands([command])[0]

    def commands(self, commands: list[list[Any]], *, allow_unavailable: bool = False) -> list[Any]:
        self.start()
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
            client.settimeout(3.0)
            client.connect(str(self.socket_path))
            for index, command in enumerate(commands):
                payload = json.dumps({"command": command, "request_id": index}).encode("utf-8") + b"\n"
                client.sendall(payload)
            responses: list[Any] = [None] * len(commands)
            pending = len(commands)
            buffer = b""
            while pending:
                chunk = client.recv(65536)
                if not chunk:
                    break
                buffer += chunk
                while b"\n" in buffer:
                    line, buffer = buffer.split(b"\n", 1)
                    if not line:
                        continue
                    decoded = json.loads(line.decode("utf-8"))
                    request_id = int(decoded.get("request_id", len(responses)))
                    if 0 <= request_id < len(responses):
                        responses[request_id] = decoded
                        pending -= 1
        data = []
        for decoded in responses:
            if not decoded:
                raise PlayerError("mpv command failed: no response")
            if decoded.get("error") not in (None, "success"):
                if allow_unavailable and decoded.get("error") == "property unavailable":
                    data.append(None)
                    continue
                raise PlayerError(f"mpv command failed: {decoded.get('error')}")
            data.append(decoded.get("data"))
        return data

    def get_property(self, name: str) -> Any:
        return self.command(["get_property", name])

    def set_property(self, name: str, value: Any) -> Any:
        return self.command(["set_property", name, value])

    def status(self) -> dict[str, Any]:
        if not self.is_running():
            return {"running": False}
        names = ("path", "filename", "pause", "time-pos", "duration", "volume", "playlist-pos", "playlist-count", "ab-loop-a", "ab-loop-b")
        values = self.commands([["get_property", name] for name in names], allow_unavailable=True)
        properties = dict(zip(names, values))
        return {"running": True, **properties}


class AxiomPlayer:
    def __init__(self, library_root: pathlib.Path, pulse_server: str):
        self.library_root = library_root.expanduser().resolve()
        self.pulse_server = pulse_server
        self.mpv = MpvController(STATE_DIR / "mpv.sock", pulse_server)
        self.bookmarks_path = STATE_DIR / "bookmarks.json"
        self.cache_root = STATE_DIR / "audio-cache"
        self.route_status_cache: tuple[float, dict[str, Any]] | None = None
        self.playback_sources: dict[str, str] = {}

    def route_status(self) -> dict[str, Any]:
        now = time.monotonic()
        if self.route_status_cache and now - self.route_status_cache[0] < DEFAULT_ROUTE_STATUS_CACHE_SECONDS:
            return self.route_status_cache[1]
        env = pulse_env(self.pulse_server)
        sinks = []
        jdsp_connected = False
        jdsp_status = ""
        try:
            output = run(["pactl", "list", "short", "sinks"], "list Pulse sinks", env=env, timeout=5).stdout
            sinks = [line.split("\t")[1] for line in output.splitlines() if "\t" in line]
        except Exception:
            pass
        try:
            run(["jamesdsp", "--is-connected"], "verify JamesDSP service", env=env, timeout=5)
            jdsp_connected = True
            jdsp_status = run(["jamesdsp", "--status"], "read JamesDSP status", env=env, timeout=5).stdout.strip()
        except Exception as exc:
            jdsp_status = str(exc)
        status = {
            "pulseServer": self.pulse_server,
            "sinks": sinks,
            "jamesdspConnected": jdsp_connected,
            "jamesdspStatus": jdsp_status,
            "jamesdspUi": self.jdsp_ui_url(),
        }
        self.route_status_cache = (now, status)
        return status

    def jdsp_ui_url(self) -> str:
        url_file = pathlib.Path("/tmp/jdsp-win/novnc-url.txt")
        if url_file.is_file():
            return url_file.read_text(encoding="utf-8").strip()
        return DEFAULT_JDSP_UI

    def start_route(self) -> None:
        run([str(REPO_ROOT / "scripts/start_wsl_jdsp_listening.sh")], "start WSL/JDSP listening route", timeout=30)
        self.route_status_cache = None

    def start_jdsp_ui(self) -> str:
        if not DEFAULT_JDSP_VNC_HELPER.is_file():
            raise PlayerError(f"JamesDSP UI helper not found: {DEFAULT_JDSP_VNC_HELPER}")
        run([str(DEFAULT_JDSP_VNC_HELPER), "--ui-only"], "start JamesDSP noVNC UI", timeout=20)
        self.route_status_cache = None
        return self.jdsp_ui_url()

    def cached_audio_path(self, path: pathlib.Path) -> pathlib.Path:
        if not env_bool("AXIOM_PLAYER_LOCAL_AUDIO_CACHE", True):
            return path
        stat = path.stat()
        digest = hashlib.sha256(str(path).encode("utf-8")).hexdigest()[:24]
        target = self.cache_root / f"{digest}{path.suffix.lower()}"
        metadata_path = self.cache_root / f"{digest}.json"
        expected_metadata = {
            "source": str(path),
            "sourceSize": stat.st_size,
            "sourceMtimeNs": stat.st_mtime_ns,
        }
        try:
            metadata = json.loads(metadata_path.read_text(encoding="utf-8")) if metadata_path.is_file() else {}
        except Exception:
            metadata = {}
        if target.is_file() and metadata == expected_metadata:
            return target
        self.cache_root.mkdir(parents=True, exist_ok=True)
        temp_target = target.with_suffix(target.suffix + ".tmp")
        shutil.copy2(path, temp_target)
        temp_target.replace(target)
        metadata_path.write_text(json.dumps(expected_metadata, indent=2) + "\n", encoding="utf-8")
        return target

    def play_track(self, track_id: str, append: bool = False) -> None:
        path = decode_id(track_id).expanduser()
        try:
            path = path.resolve(strict=True)
            path.relative_to(self.library_root)
        except (OSError, ValueError) as exc:
            raise PlayerError("selected track is outside the configured music library") from exc
        if not path.is_file() or path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            raise PlayerError("selected track is not a supported audio file")
        playback_path = self.cached_audio_path(path)
        self.playback_sources[str(playback_path)] = str(path)
        self.mpv.command(["loadfile", str(playback_path), "append-play" if append else "replace"])
        if not append:
            self.mpv.set_property("pause", False)

    def queue_tracks(self, track_ids: list[str]) -> None:
        first = True
        for track_id in track_ids:
            self.play_track(track_id, append=not first)
            first = False

    def load_eel(self, path_value: str) -> str:
        path = windows_to_wsl_path(path_value).resolve()
        if not path.is_file() or path.suffix.lower() != ".eel":
            raise PlayerError(f"EEL script not found: {path}")
        run([str(REPO_ROOT / "scripts/validate_axiom_static.sh"), str(path)], "validate EEL script", timeout=20)
        run([str(REPO_ROOT / "scripts/hot_reload_liveprog.sh"), str(path), "Axiom-player-current"], "hot reload EEL script", env=pulse_env(self.pulse_server), timeout=20)
        return str(path)

    def repo_eel_scripts(self) -> list[dict[str, str]]:
        return [
            {"name": path.name, "path": str(path)}
            for path in sorted((REPO_ROOT / "src").glob("*.eel"))
        ]

    def bookmarks(self) -> list[dict[str, Any]]:
        if not self.bookmarks_path.is_file():
            return []
        try:
            return json.loads(self.bookmarks_path.read_text(encoding="utf-8"))
        except Exception:
            return []

    def save_bookmark(self, label: str) -> dict[str, Any]:
        status = self.mpv.status()
        path = self.playback_sources.get(str(status.get("path")), status.get("path"))
        item = {
            "label": label or f"Bookmark {len(self.bookmarks()) + 1}",
            "path": path,
            "position": status.get("time-pos"),
            "createdAt": int(time.time()),
        }
        bookmarks = self.bookmarks()
        bookmarks.append(item)
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        self.bookmarks_path.write_text(json.dumps(bookmarks, indent=2) + "\n", encoding="utf-8")
        return item


def error_response(exc: Exception, status: int = 400):
    return jsonify({"ok": False, "error": str(exc)}), status


def create_app(library_root: pathlib.Path = DEFAULT_LIBRARY, pulse_server: str = DEFAULT_PULSE_SERVER) -> Flask:
    app = Flask(__name__, static_folder=str(STATIC_ROOT), static_url_path="/static")
    player = AxiomPlayer(library_root, pulse_server)

    @app.get("/")
    def index():
        return send_from_directory(STATIC_ROOT, "index.html")

    @app.get("/api/status")
    def api_status():
        player_status = player.mpv.status()
        path = player_status.get("path")
        if path:
            player_status["sourcePath"] = player.playback_sources.get(str(path), path)
        return jsonify({"ok": True, "route": player.route_status(), "player": player_status})

    @app.post("/api/route/start")
    def api_start_route():
        try:
            player.start_route()
            return jsonify({"ok": True, "route": player.route_status()})
        except Exception as exc:
            return error_response(exc, 500)

    @app.post("/api/jdsp-ui/start")
    def api_start_jdsp_ui():
        try:
            return jsonify({"ok": True, "url": player.start_jdsp_ui(), "route": player.route_status()})
        except Exception as exc:
            return error_response(exc, 500)

    @app.get("/api/library")
    def api_library():
        return jsonify({"ok": True, **library_payload(player.library_root)})

    @app.post("/api/play")
    def api_play():
        try:
            payload = request.get_json(force=True)
            player.play_track(str(payload["id"]))
            return jsonify({"ok": True})
        except Exception as exc:
            return error_response(exc)

    @app.post("/api/queue")
    def api_queue():
        try:
            payload = request.get_json(force=True)
            player.queue_tracks([str(item) for item in payload.get("ids", [])])
            return jsonify({"ok": True})
        except Exception as exc:
            return error_response(exc)

    @app.post("/api/player/command")
    def api_player_command():
        try:
            payload = request.get_json(force=True)
            command = payload.get("command")
            value = payload.get("value")
            if command == "pause":
                player.mpv.set_property("pause", True)
            elif command == "resume":
                player.mpv.set_property("pause", False)
            elif command == "toggle":
                current = bool(player.mpv.get_property("pause"))
                player.mpv.set_property("pause", not current)
            elif command == "seek":
                player.mpv.command(["seek", float(value), "absolute"])
            elif command == "relative-seek":
                player.mpv.command(["seek", float(value), "relative"])
            elif command == "next":
                player.mpv.command(["playlist-next", "weak"])
            elif command == "previous":
                player.mpv.command(["playlist-prev", "weak"])
            elif command == "volume":
                player.mpv.set_property("volume", max(0, min(100, float(value))))
            elif command == "loop-a":
                player.mpv.set_property("ab-loop-a", player.mpv.get_property("time-pos"))
            elif command == "loop-b":
                player.mpv.set_property("ab-loop-b", player.mpv.get_property("time-pos"))
            elif command == "loop-clear":
                player.mpv.set_property("ab-loop-a", "no")
                player.mpv.set_property("ab-loop-b", "no")
            else:
                raise PlayerError(f"unknown player command: {command}")
            return jsonify({"ok": True, "player": player.mpv.status()})
        except Exception as exc:
            return error_response(exc)

    @app.get("/api/eel")
    def api_eel():
        return jsonify({"ok": True, "scripts": player.repo_eel_scripts()})

    @app.post("/api/eel/load")
    def api_eel_load():
        try:
            payload = request.get_json(force=True)
            path = player.load_eel(str(payload["path"]))
            return jsonify({"ok": True, "path": path})
        except Exception as exc:
            return error_response(exc)

    @app.get("/api/bookmarks")
    def api_bookmarks():
        return jsonify({"ok": True, "bookmarks": player.bookmarks()})

    @app.post("/api/bookmarks")
    def api_bookmark_save():
        try:
            payload = request.get_json(force=True)
            return jsonify({"ok": True, "bookmark": player.save_bookmark(str(payload.get("label", "")))})
        except Exception as exc:
            return error_response(exc)

    return app


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--library", type=pathlib.Path, default=DEFAULT_LIBRARY)
    parser.add_argument("--pulse-server", default=DEFAULT_PULSE_SERVER)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args(argv)
    if not is_loopback_host(args.host):
        parser.error("--host must be a loopback address (127.0.0.1, ::1, or localhost)")
    app = create_app(args.library.expanduser(), args.pulse_server)
    app.run(host=args.host, port=args.port, debug=False, threaded=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
