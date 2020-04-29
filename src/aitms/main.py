from __future__ import annotations

from aitms.config import Config
from aitms.ui.app import AITMSApp
from aitms.utils.logging_setup import setup_logging


def main() -> None:
    setup_logging()
    config = Config()
    app = AITMSApp(config)
    app.run()


if __name__ == "__main__":
    main()
