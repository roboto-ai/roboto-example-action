import logging
from roboto import ActionRuntime
from roboto.domain import datasets

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    runtime = ActionRuntime.from_env()
    dataset = datasets.Dataset.from_id(runtime.dataset_id)

    log_path = runtime.input_dir / "log.txt"
    keyword = "error"

    with open(log_path, "r") as log_file:
        if keyword in log_file.read():
            dataset.put_tags([keyword])
            logger.info(f"Found '{keyword}' in log file.")
        else:
            logger.info(f"'{keyword}' not found in log file.")
