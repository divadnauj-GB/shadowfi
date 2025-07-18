
from utils import logger

def test_logger_setup(caplog):
    logger.setup_logger()
    import logging
    logging.info("Hello log")
    assert "Hello log" in caplog.text
