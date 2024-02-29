# Roboto Example Action

This repository provides a sample Action for the Roboto platform, designed to read a log file and append a tag to a dataset upon detecting a specific string within the log file.

## Prerequisites

Ensure you have Docker installed:
- [Docker Installation Guide](https://docs.docker.com/engine/install/)

## Quickstart

Follow these steps to get the Action set up:

1. **Clone the Repository**

    Clone the repository using the command below:
    ```shell
    git clone https://github.com/roboto-ai/robologs-example-action.git
    ```

2. **Execute the Action Locally**

    Navigate to the project directory and execute the following commands:
    ```shell
    cd robologs-example-action/tag_dataset/
    # Build the Docker image
    ./scripts/build.sh
    # Run the Action
    ./scripts/run.sh $PWD/input/
    ```
    A JSON file will be generated in the `output` directory with this structure:
    ```json
    {
        "put_tags": ["error"],
        "remove_tags": [],
        "put_fields": {},
        "remove_fields": []
    }
    ```

3. **Deploy the Action to the Roboto Platform**

    Ensure your Roboto Platform account is set up and the CLI is installed:
    - [Roboto Account Setup](https://docs.roboto.ai/getting-started/account.html)

    Deploy the action using:
    ```shell
    ./scripts/setup.sh
    ./scripts/deploy.sh
    ```

4. **Utilize the CLI to Execute the Action on a Dataset**

    Create a dataset and retrieve the dataset ID:
    ```shell
    roboto datasets create
    ```
    With the dataset ID, proceed with the following steps:
    ```shell
    # Upload a sample log file
    roboto datasets upload-files -d <dataset_id> -p $PWD/input/log.txt
    # Run the Action
    roboto actions invoke tag_dataset --dataset-id <dataset_id> --input-data log.txt
    ```
    Retrieve the invocation ID from the output. You can check the invocation status with:
    ```shell
    roboto invocations status <invocation_id> --tail
    ```

    Upon completion, verify the `error` tag addition:
    ```shell
    roboto datasets show --dataset-id <dataset_id>
    ```
    The output should include:
    ```json
    {
        "org_id": "your_org_id",
        "dataset_id": "some_dataset_id",
        "tags": ["error"]
    }
    ```

    Confirm the tag presence via the Roboto Platform UI:
    - [Roboto Datasets](https://app.roboto.ai/datasets)

## Contributing

Feel free to suggest improvements or report issues. Your feedback is valuable in improving Actions for Roboto users. 

**Happy Coding!**
