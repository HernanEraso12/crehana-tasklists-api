"""Configura el logging del paquete `app` (p. ej. `LoggingNotifier`,
E2) para que llegue a stdout junto a los logs de uvicorn. No toca el
logger raíz ni la configuración de logging de uvicorn: solo fija nivel
y formato en el logger `app`, del que heredan sus submódulos."""

import logging
import sys

_FORMAT = "%(asctime)s %(levelname)s %(name)s: %(message)s"


def configure_logging(level: str = "INFO") -> None:
    logger = logging.getLogger("app")
    logger.setLevel(level.upper())
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(_FORMAT))
        logger.addHandler(handler)
