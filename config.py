import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DEFINITIONS_FOLDER = os.path.join(BASE_DIR, 'Definitions')
MEMORY_FOLDER = os.path.join(BASE_DIR, 'Memory')

SAVE_FILE = os.path.join(MEMORY_FOLDER, 'timetable.json')