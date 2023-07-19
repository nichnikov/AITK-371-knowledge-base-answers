import os
import json
import logging
from pathlib import Path
from dotenv import load_dotenv

def get_project_root() -> Path:
    """"""
    return Path(__file__).parent


PROJECT_ROOT_DIR = get_project_root()
print(PROJECT_ROOT_DIR)

logging.basicConfig(
    filename=os.path.join(PROJECT_ROOT_DIR, "data", "expert_bot_update.logs"),
    filemode='a',
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S', )

logger = logging.getLogger()
logger.setLevel(logging.INFO)

load_dotenv()
data_url = os.getenv("URL")
es_url = os.getenv("HOSTS")
es_user = os.getenv("USER_NAME")
es_pass = os.getenv("PASSWORD")