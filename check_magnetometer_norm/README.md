# check_magnetometer_norm

This Roboto Action checks if a drone's magnetometer norm exceeds a defined threshold.

It adds a tag to the log file if the norm exceeds the threshold and creates Roboto Events to highlight the corresponding time intervals.

Note, this Action can only be run on files that have been ingested as it operates on processed topic data.

## Getting started

1. Setup Action environment and install dev dependencies: `./scripts/setup.sh`
2. Build Action image: `./scripts/build.sh`
3. Run Action locally to test: `./scripts/run.sh` (re: `test/input-manifest.txt`)
4. Deploy Action to Roboto: `./scripts/deploy.sh`

## Action configuration file

This Roboto Action is configured in `action.json`. Refer to Roboto's latest documentation for the expected structure.

## Input manifest file

To run this action locally, an example input manifest file is available at: `test/input-manifest.txt`.

This can be used in conjunction with `scripts/run.sh` to make inputs available to your local action runtime.

You can populate an input manifest with records of entities such as files and topics. For example, you can get the record for a file you've uploaded to Roboto with:

```python
from roboto import File
fl = File.from_id("fl_y4thd7ag228i2gvq7d0m")
print(fl)
```

Then add the record into the `"files": []` key of the input manifest.

You can also generate an input manifest for an entire dataset with a script (see [gist](https://gist.github.com/rowandempster/8704bf4ce42b38ad09d4c246be9af585)).