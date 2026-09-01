import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

class LoggerService:
    def __init__(self, logs_dir: str = "logs"):
        self.logs_dir = Path(logs_dir)
        self.logs_dir.mkdir(parents=True, exist_ok=True)

        self.game_logger = self._create_logger("game", self.logs_dir / "game.log")
        self.admin_logger = self._create_logger("admin", self.logs_dir / "admin.log")

    def _create_logger(self, name: str, path: Path) -> logging.Logger:
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            handler = RotatingFileHandler(path, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8")
            formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger

    def log_game(self, message: str) -> None:
        self.game_logger.info(message)

    def log_admin(self, message: str) -> None:
        self.admin_logger.info(message)
