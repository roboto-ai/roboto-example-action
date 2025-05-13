# check_camera_blur

Checks if a camera is out of focus. If so, it tags the file and creates Events to highlight corresponding time intervals.

## Getting started

1. Setup a virtual environment specific to this project and install development dependencies, including the `roboto` SDK: `./scripts/setup.sh`
2. Build Docker image: `./scripts/build.sh`
3. Run Action image locally: `./scripts/run.sh <path-to-input-data-directory>`
4. Deploy to Roboto Platform: `./scripts/deploy.sh`

## Action configuration file

This Roboto Action is configured in `action.json`. Refer to Roboto's latest documentation for the expected structure.
