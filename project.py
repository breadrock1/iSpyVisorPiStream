from datetime import datetime
from pathlib import Path

ROOT_DIR_PATH = Path('.').absolute()

LOGS_DIR_PATH = ROOT_DIR_PATH / 'logs'
RESOURCES_DIR_PATH = ROOT_DIR_PATH / 'resources'
STATIC_DIR_PATH = ROOT_DIR_PATH / 'static'
TEMPLATES_DIR_PATH = ROOT_DIR_PATH / 'templates'

LOGGING_FORMAT = '%(asctime)s - %(levelname)s - %(module)s - %(funcName)s: %(lineno)d - %(message)s'
LOG_FILE_PATH = LOGS_DIR_PATH / f'{datetime.now().strftime("%d.%m.%Y_%H-%M")}-application.log'
