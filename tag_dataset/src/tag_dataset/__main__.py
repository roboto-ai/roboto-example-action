import logging
from roboto import ActionRuntime
from roboto.domain import datasets

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    runtime = ActionRuntime.from_env()
    dataset = runtime.dataset

    log_path = runtime.input_dir / "log.txt"
    keyword = "error"

    with open(log_path, "r") as log_file:
        if keyword in log_file.read():
            dataset.put_tags([keyword])
            logger.info(f"Found '{keyword}' in log file.")
        else:
            logger.info(f"'{keyword}' not found in log file.")
