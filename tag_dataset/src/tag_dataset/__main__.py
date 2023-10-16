import logging
import os
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    input_dir = os.getenv("ROBOTO_INPUT_DIR")
    output_dir = os.getenv("ROBOTO_OUTPUT_DIR")
    output_path_metadata = os.getenv("ROBOTO_DATASET_METADATA_CHANGESET_FILE")

    if not input_dir or not output_dir or not output_path_metadata:
        error_msg = "Set ROBOTO_INPUT_DIR, ROBOTO_OUTPUT_DIR and ROBOTO_DATASET_METADATA_CHANGESET_FILE env variables."
        logger.error(error_msg)
        raise RuntimeError(error_msg)

    log_file_path = os.path.join(input_dir, "log.txt")

    if not os.path.exists(log_file_path):
        logger.error("%s missing.", log_file_path)
        raise RuntimeError(f"{log_file_path} missing.")

    put_tags = list()

    try:
        with open(log_file_path, "r") as file:
            if "error" in file.read():
                print(f"Found word 'error' in log file.")
                put_tags.append("error")

        with open(output_path_metadata, "w") as json_file:
            metadata_dict = {
                "put_tags": put_tags,
                "remove_tags": [],
                "put_fields": {},
                "remove_fields": [],
            }
            print(f"Writing {output_path_metadata}...")
            json.dump(metadata_dict, json_file, indent=4)
    except Exception as exc:
        logger.error("Error while reading file", exc_info=exc)
        raise


if __name__ == "__main__":
    main()
