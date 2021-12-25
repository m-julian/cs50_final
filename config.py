from pathlib import Path

# GLOBAL_CONFIG
PROGRAM_NAME = "PCTimingManager"
DATABASE_NAME = PROGRAM_NAME + ".db"
# create database Path object
PROGRAM_PATH = (Path.cwd() / f"{PROGRAM_NAME}.exe").absolute()
DB_PATH = Path.home().absolute() / "Documents" / DATABASE_NAME
TIME_BETWEEN_RECORDINGS = 60  # time between db recording in seconds
