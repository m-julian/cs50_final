from pathlib import Path

# GLOBAL_CONFIG
DATABASE_NAME = "PCUserUptime_timings.db"
PROGRAM_NAME = "PCUserUptime"
# create database Path object
DB_PATH = Path.home().absolute() / "Documents" / DATABASE_NAME
TIME_BETWEEN_RECORDINGS = 30 # time between db recording in seconds