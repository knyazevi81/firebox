from decouple import config

PORT = config("PORT", default=8080, cast=int)
TARGET_HOST = config("TARGET_HOST", default="127.0.0.1")
VERBOSE = config("VERBOSE", default=True, cast=bool)
LOGGING_FORMAT = "%(asctime)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M" 
LOGGING_FILENAME = "firewall_logs.log"
MACHINE_SEC = config("MACHINE_SEC", default=False, cast=bool)
SIGNATURE_SEC = config("SIGNATURE_SEC", default=False, cast=bool)
RATE_LIMIT = config("RATE_LIMIT", default="60:50", cast=str)