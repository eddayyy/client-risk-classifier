import logging
import structlog

# 1. Configure the stdlib logging first
logging.basicConfig(format="%(message)s", level=logging.INFO)

# 2. Configure structlog to wrap around it
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
)

# 3. Expose one shared logger instance
log = structlog.get_logger()
