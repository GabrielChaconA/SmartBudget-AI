import logging

LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s %(message)s"


def configure_logging(level: str = "INFO") -> None:
    logging.basicConfig(level=level.upper(), format=LOG_FORMAT)
    logging.getLogger("app").setLevel(level.upper())
    # httpx/httpcore registran URLs y, en DEBUG, cuerpos de petición: los
    # silenciamos para no filtrar datos financieros a los logs.
    for noisy in ("httpx", "httpcore"):
        logging.getLogger(noisy).setLevel(logging.WARNING)
