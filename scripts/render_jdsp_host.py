#!/usr/bin/env python3
"""Render one stereo WAV through a JDSP Liveprog script without persisting test state."""

from __future__ import annotations

import argparse
import os
import pathlib
import re
import select
import subprocess
import sys
import tempfile
import threading
import time
import wave
from typing import BinaryIO, Callable


COMMAND_TIMEOUT = 8
DEFAULT_PLAYBACK_SINK = "JamesDSP"
JDSP_APPLICATION_ID = "com.github.gstmgr"
JDSP_APPLICATION_NAME = "jamesdsp"
NEUTRAL_SETTINGS = {
    "tube_enable": "false",
    "compander_enable": "false",
    "bass_enable": "false",
    "graphiceq_enable": "false",
    "tone_enable": "false",
    "convolver_enable": "false",
    "ddc_enable": "false",
    "stereowide_enable": "false",
    "reverb_enable": "false",
    "master_limthreshold": "0",
    "master_limrelease": "60",
    "master_postgain": "0",
    "crossfeed_enable": "false",
}


class RenderError(RuntimeError):
    pass


def run_text(
    command: list[str],
    label: str,
    *,
    env: dict[str, str] | None = None,
    timeout: int = COMMAND_TIMEOUT,
) -> str:
    try:
        result = subprocess.run(
            command, text=True, capture_output=True, check=False, timeout=timeout, env=env
        )
    except FileNotFoundError as exc:
        raise RenderError(f"{label} failed: command not found: {command[0]}") from exc
    except subprocess.TimeoutExpired as exc:
        raise RenderError(f"{label} timed out after {timeout} seconds") from exc
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or f"exit {result.returncode}"
        raise RenderError(f"{label} failed: {detail}")
    return result.stdout


def pulse_environment(server: str) -> dict[str, str]:
    environment = os.environ.copy()
    environment["PULSE_SERVER"] = server
    return environment


def read_setting(key: str) -> str:
    return run_text(["jamesdsp", "--get", key], f"read JDSP setting {key}").strip()


def set_setting(key: str, value: str, *, force: bool = False) -> None:
    if not force and read_setting(key) == value:
        return
    try:
        run_text(["jamesdsp", "--set", f"{key}={value}"], f"write JDSP setting {key}")
    except RenderError:
        # JDSP4Linux may return failure for a setting update that it has applied.
        pass
    applied = read_setting(key)
    if applied != value:
        raise RenderError(f"JDSP did not apply {key}={value}; current value is {applied}")


def snapshot_host_state() -> dict[str, str]:
    keys = list(NEUTRAL_SETTINGS) + ["liveprog_enable", "liveprog_file"]
    return {key: read_setting(key) for key in keys}


def load_neutral_liveprog(eel_path: pathlib.Path) -> None:
    for key, value in NEUTRAL_SETTINGS.items():
        set_setting(key, value)
    set_setting("liveprog_enable", "false")
    set_setting("liveprog_file", str(eel_path.resolve()), force=True)
    set_setting("liveprog_enable", "true")


def restore_host_state(snapshot: dict[str, str]) -> list[str]:
    errors: list[str] = []
    restore_steps = (
        [("liveprog_enable", "false"), ("liveprog_file", snapshot["liveprog_file"])]
        + [(key, snapshot[key]) for key in NEUTRAL_SETTINGS]
        + [("liveprog_enable", snapshot["liveprog_enable"])]
    )
    for key, value in restore_steps:
        try:
            set_setting(key, value, force=(key == "liveprog_file"))
        except RenderError as exc:
            errors.append(str(exc))
    return errors


def short_objects(kind: str, pulse_env: dict[str, str]) -> dict[str, str]:
    output = run_text(["pactl", "list", "short", kind], f"list PulseAudio {kind}", env=pulse_env)
    found: dict[str, str] = {}
    for line in output.splitlines():
        columns = line.split("\t")
        if len(columns) >= 2:
            found[columns[1]] = columns[0]
    return found


def object_id(name: str, kind: str, pulse_env: dict[str, str]) -> str:
    found = short_objects(kind, pulse_env)
    if name not in found:
        choices = ", ".join(sorted(found)) or "<none>"
        raise RenderError(f"PulseAudio {kind[:-1]} not found: {name}; available: {choices}")
    return found[name]


def sink_inputs(pulse_env: dict[str, str]) -> list[dict[str, str]]:
    output = run_text(["pactl", "list", "sink-inputs"], "inspect PulseAudio sink inputs", env=pulse_env)
    streams: list[dict[str, str]] = []
    for block in re.split(r"\n(?=Sink Input #)", output.strip()):
        number = re.search(r"^Sink Input #(\d+)", block)
        sink = re.search(r"^\s*Sink:\s*(\d+)", block, re.MULTILINE)
        app_id = re.search(r'^\s*application\.id = "([^"]+)"', block, re.MULTILINE)
        app_name = re.search(r'^\s*application\.name = "([^"]+)"', block, re.MULTILINE)
        if number and sink:
            streams.append(
                {
                    "id": number.group(1),
                    "sink": sink.group(1),
                    "application.id": app_id.group(1) if app_id else "",
                    "application.name": app_name.group(1) if app_name else "",
                }
            )
    return streams


def jdsp_sink_input(pulse_env: dict[str, str]) -> dict[str, str] | None:
    matches = [
        stream
        for stream in sink_inputs(pulse_env)
        if stream["application.id"] == JDSP_APPLICATION_ID
        and stream["application.name"] == JDSP_APPLICATION_NAME
    ]
    if len(matches) > 1:
        raise RenderError("multiple JamesDSP processed-output sink inputs are active")
    return matches[0] if matches else None


def assert_private_sink_uncontaminated(
    sink_id: str, jdsp_id: str, pulse_env: dict[str, str]
) -> None:
    occupants = [stream for stream in sink_inputs(pulse_env) if stream["sink"] == sink_id]
    unwanted = [stream["id"] for stream in occupants if stream["id"] != jdsp_id]
    if unwanted:
        raise RenderError(f"private capture sink received unrelated sink input(s): {', '.join(unwanted)}")
    if not any(stream["id"] == jdsp_id for stream in occupants):
        raise RenderError("JamesDSP processed output is no longer routed to the private capture sink")


def read_wav(path: pathlib.Path) -> tuple[int, int, bytes]:
    try:
        with wave.open(str(path), "rb") as source:
            channels = source.getnchannels()
            sample_width = source.getsampwidth()
            rate = source.getframerate()
            frames = source.getnframes()
            compression = source.getcomptype()
            audio = source.readframes(frames)
    except (OSError, wave.Error) as exc:
        raise RenderError(f"cannot read input WAV {path}: {exc}") from exc
    if compression != "NONE" or channels != 2 or sample_width != 2:
        raise RenderError("input must be an uncompressed 16-bit stereo PCM WAV")
    if rate <= 0 or frames <= 0:
        raise RenderError("input WAV has no audio frames or an invalid sample rate")
    return rate, frames, audio


def read_exact(
    stream: BinaryIO, size: int, timeout: float, audit: Callable[[], None]
) -> bytes:
    captured = bytearray()
    deadline = time.monotonic() + timeout
    while len(captured) < size:
        audit()
        remaining_time = deadline - time.monotonic()
        if remaining_time <= 0:
            raise RenderError("capture timed out before the required frame count was recorded")
        ready, _, _ = select.select([stream], [], [], min(0.1, remaining_time))
        if not ready:
            continue
        chunk = os.read(stream.fileno(), min(size - len(captured), 65536))
        if not chunk:
            raise RenderError("capture stream ended before the required frame count was recorded")
        captured.extend(chunk)
    return bytes(captured)


def wait_for_jdsp_stream(pulse_env: dict[str, str], timeout: float = 3.0) -> dict[str, str]:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        stream = jdsp_sink_input(pulse_env)
        if stream is not None:
            return stream
        time.sleep(0.05)
    raise RenderError("JamesDSP processed output did not appear during playback")


def render_isolated(
    input_path: pathlib.Path,
    output_path: pathlib.Path,
    playback_sink: str,
    pulse_env: dict[str, str],
    pre_roll_ms: int,
    tail_ms: int,
) -> tuple[int, int, int, str]:
    rate, input_frames, audio = read_wav(input_path)
    object_id(playback_sink, "sinks", pulse_env)
    bytes_per_frame = 4
    pre_frames = round(rate * pre_roll_ms / 1000)
    tail_frames = round(rate * tail_ms / 1000)
    output_frames = pre_frames + input_frames + tail_frames
    capture_sink = f"AxiomRender_{os.getpid()}_{time.monotonic_ns()}"
    capture_source = f"{capture_sink}.monitor"
    module_id: str | None = None
    player: subprocess.Popen[bytes] | None = None
    recorder: subprocess.Popen[bytes] | None = None
    jdsp_id: str | None = None
    original_sink_id: str | None = None
    temporary_name: str | None = None
    writer_error: list[BaseException] = []
    cleanup_errors: list[str] = []
    try:
        module_id = run_text(
            [
                "pactl",
                "load-module",
                "module-null-sink",
                f"sink_name={capture_sink}",
                f"rate={rate}",
                "channels=2",
                "format=s16le",
                "norewinds=1",
            ],
            "create private capture sink",
            env=pulse_env,
        ).strip()
        private_sink_id = object_id(capture_sink, "sinks", pulse_env)
        object_id(capture_source, "sources", pulse_env)
        player = subprocess.Popen(
            [
                "paplay",
                f"--device={playback_sink}",
                "--raw",
                "--format=s16le",
                f"--rate={rate}",
                "--channels=2",
                "--latency-msec=20",
            ],
            stdin=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=pulse_env,
        )
        assert player.stdin is not None
        player.stdin.write(bytes(rate * bytes_per_frame // 2))
        player.stdin.flush()
        stream = wait_for_jdsp_stream(pulse_env)
        jdsp_id = stream["id"]
        original_sink_id = stream["sink"]
        run_text(
            ["pactl", "move-sink-input", jdsp_id, capture_sink],
            "route JamesDSP output to private capture sink",
            env=pulse_env,
        )
        time.sleep(0.2)
        assert_private_sink_uncontaminated(private_sink_id, jdsp_id, pulse_env)
        recorder = subprocess.Popen(
            [
                "parec",
                f"--device={capture_source}",
                "--raw",
                "--format=s16le",
                f"--rate={rate}",
                "--channels=2",
                "--latency-msec=20",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=pulse_env,
        )
        payload = bytes(pre_frames * bytes_per_frame) + audio + bytes(tail_frames * bytes_per_frame)

        def write_payload() -> None:
            try:
                assert player is not None and player.stdin is not None
                player.stdin.write(payload)
                player.stdin.flush()
            except BaseException as exc:
                writer_error.append(exc)

        writer = threading.Thread(target=write_payload, name="jdsp-render-playback", daemon=True)
        writer.start()
        assert recorder.stdout is not None
        captured = read_exact(
            recorder.stdout,
            output_frames * bytes_per_frame,
            max(10.0, output_frames / rate + 5.0),
            lambda: assert_private_sink_uncontaminated(private_sink_id, jdsp_id, pulse_env),
        )
        writer.join(timeout=max(10.0, output_frames / rate + 5.0))
        if writer.is_alive():
            raise RenderError("playback did not accept the render input before timeout")
        if writer_error:
            raise RenderError(f"playback failed while writing the render payload: {writer_error[0]}")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            prefix=f".{output_path.name}.", suffix=".tmp", dir=output_path.parent, delete=False
        ) as temporary:
            temporary_name = temporary.name
        with wave.open(temporary_name, "wb") as destination:
            destination.setnchannels(2)
            destination.setsampwidth(2)
            destination.setframerate(rate)
            destination.writeframes(captured)
        os.replace(temporary_name, output_path)
        temporary_name = None
    finally:
        if recorder is not None and recorder.poll() is None:
            recorder.terminate()
            try:
                recorder.wait(timeout=2)
            except subprocess.TimeoutExpired:
                recorder.kill()
                recorder.wait()
        if jdsp_id is not None and original_sink_id is not None:
            try:
                current = jdsp_sink_input(pulse_env)
                if current is not None and current["id"] == jdsp_id:
                    run_text(
                        ["pactl", "move-sink-input", jdsp_id, original_sink_id],
                        "restore JamesDSP output sink",
                        env=pulse_env,
                    )
            except RenderError as exc:
                cleanup_errors.append(str(exc))
        if player is not None and player.poll() is None:
            player.terminate()
            try:
                player.wait(timeout=2)
            except subprocess.TimeoutExpired:
                player.kill()
                player.wait()
        if module_id is not None:
            try:
                run_text(
                    ["pactl", "unload-module", module_id],
                    "unload private capture sink",
                    env=pulse_env,
                )
            except RenderError as exc:
                cleanup_errors.append(str(exc))
        if temporary_name is not None:
            pathlib.Path(temporary_name).unlink(missing_ok=True)
        if cleanup_errors:
            raise RenderError("; ".join(cleanup_errors))
    return rate, input_frames, output_frames, capture_source


def non_negative_int(value: str) -> int:
    parsed = int(value)
    if parsed < 0:
        raise argparse.ArgumentTypeError("must be zero or greater")
    return parsed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_wav", type=pathlib.Path)
    parser.add_argument("eel_script", type=pathlib.Path)
    parser.add_argument("output_wav", type=pathlib.Path)
    parser.add_argument(
        "--pulse-server",
        required=True,
        help="Pulse server used by the running JDSP service, for example unix:/run/user/1000/pulse/native",
    )
    parser.add_argument("--playback-sink", default=DEFAULT_PLAYBACK_SINK)
    parser.add_argument("--pre-roll-ms", type=non_negative_int, default=500)
    parser.add_argument("--tail-ms", type=non_negative_int, default=2000)
    args = parser.parse_args()
    eel_path = args.eel_script.resolve()
    snapshot: dict[str, str] | None = None
    error: Exception | None = None
    pulse_env = pulse_environment(args.pulse_server)
    try:
        if not eel_path.is_file():
            raise RenderError(f"EEL script not found: {eel_path}")
        read_wav(args.input_wav.resolve())
        object_id(args.playback_sink, "sinks", pulse_env)
        snapshot = snapshot_host_state()
        load_neutral_liveprog(eel_path)
        rate, input_frames, output_frames, capture_source = render_isolated(
            args.input_wav.resolve(),
            args.output_wav.resolve(),
            args.playback_sink,
            pulse_env,
            args.pre_roll_ms,
            args.tail_ms,
        )
    except (OSError, RenderError, subprocess.SubprocessError) as exc:
        error = exc
    finally:
        if snapshot is not None:
            restore_errors = restore_host_state(snapshot)
            if restore_errors:
                detail = "; ".join(restore_errors)
                error = RenderError(f"{error}; host restoration failed: {detail}" if error else detail)
    if error is not None:
        print(f"error: {error}", file=sys.stderr)
        return 1
    print(f"Rendered through JDSP Liveprog: {eel_path}")
    print(f"Route: {args.playback_sink} -> jamesdsp -> temporary {capture_source}")
    print(f"Input frames: {input_frames} at {rate} Hz; captured: {output_frames}")
    print(f"Output: {args.output_wav.resolve()}")
    print("Host settings and processed-output routing restored.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
