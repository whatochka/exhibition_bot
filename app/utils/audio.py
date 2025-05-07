import tempfile
import subprocess


def convert_to_ogg_voice(file_bytes: bytes, input_format: str = "mp3") -> str:
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{input_format}") as source_file:
        source_file.write(file_bytes)
        source_path = source_file.name

    target_path = source_path.replace(f".{input_format}", ".ogg")

    subprocess.run([
        "ffmpeg",
        "-i", source_path,
        "-ar", "48000",
        "-ac", "1",
        "-c:a", "libopus",
        target_path
    ], check=True)

    return target_path
