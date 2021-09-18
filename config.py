from pathlib import Path

# GLOBAL_CONFIG
DATABASE_NAME = "timings.db"
# create database Path object
DB_PATH = Path.home().absolute() / "Desktop" / DATABASE_NAME
TIME_BETWEEN_RECORDINGS = 5 # time between db recording