# check_magnetometer_norm

This Roboto Action checks if a drone's magnetometer norm exceeds a defined threshold.

It adds a tag to the log file if the magnetometer norm exceeds the threshold and creates Roboto Events to highlight corresponding time intervals.

Note, this Action can only be run on files that have been ingested as it operates on processed topic data.

## Getting started

1. Setup Action environment and install dev dependencies: `./scripts/setup.sh`
2. Build Action image: `./scripts/build.sh`
3. Deploy Action to Roboto: `./scripts/deploy.sh`

## Action configuration file

This Roboto Action is configured in `action.json`. Refer to Roboto's latest documentation for the expected structure.
