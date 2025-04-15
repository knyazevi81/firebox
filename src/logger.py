import logging
from logging.handlers import RotatingFileHandler
from src.config import LOGGING_FORMAT, LOGGING_FILENAME, VERBOSE, DATE_FORMAT

def setup_logger():
    """Настраивает логгер для приложения."""
    logger = logging.getLogger("FastFire")
    logger.setLevel(logging.DEBUG if VERBOSE else logging.INFO)

    # Формат логов
    formatter = logging.Formatter(
        LOGGING_FORMAT,
        datefmt=DATE_FORMAT
    )

    # Обработчик для записи в файл с ротацией
    file_handler = RotatingFileHandler(
        LOGGING_FILENAME, maxBytes=10 * 1024 * 1024, backupCount=5
    )
    file_handler.setFormatter(formatter)

    # Обработчик для вывода в консоль
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # Удаляем предыдущие обработчики, чтобы избежать дублирования
    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger