from importlib.metadata import version

try:
    __version__ = version("aitms")
except Exception:
    __version__ = "0.1.0"
