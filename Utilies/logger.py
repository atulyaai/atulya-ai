from loguru import logger

class AtulyaLogger:
    def __init__(self, name="atulya"):
        self.name = name
        logger.add(f"Logs/{name}.log", rotation="10 MB", retention="5 days", level="INFO")

    def info(self, msg, **kwargs):
        logger.info(f"{msg} | {kwargs}")

    def warning(self, msg, **kwargs):
        logger.warning(f"{msg} | {kwargs}")

    def error(self, msg, **kwargs):
        logger.error(f"{msg} | {kwargs}")

    def debug(self, msg, **kwargs):
        logger.debug(f"{msg} | {kwargs}")

atulya_logger = AtulyaLogger() 