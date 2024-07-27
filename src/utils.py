import os


def get_sample_image() -> bytes:
    sample_image_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../sample", "sample.jpg")
    )
    with open(sample_image_path, "rb") as f:
        return f.read()


def get_sample_audio() -> bytes:
    sample_audio_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../sample", "sample.mp3")
    )
    with open(sample_audio_path, "rb") as f:
        return f.read()


def get_sample_video() -> bytes:
    sample_audio_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../sample", "sample.mp4")
    )
    with open(sample_audio_path, "rb") as f:
        return f.read()


def get_sample_text() -> str:
    return "Hello, World!"


def bytes_to_file(data: bytes, path: str) -> None:
    with open(path, "wb") as f:
        f.write(data)
