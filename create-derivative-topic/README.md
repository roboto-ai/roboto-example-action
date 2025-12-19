# create-derivative-topic

This Roboto Action serves as a reference implementation for creating **derivative topics** from existing topic data.

It demonstrates how to generate new, continuous time-series signals stored in dataframes and associate them with a file in Roboto.

The specific example takes data from two existing topis: `vehicle_local_position` and `vehicle_local_position_setpoints`, and produces a derivative topic called `setpoints_tracking_error`.

Note, this action can only be run on ULog files that have been ingested in Roboto as it operates on processed topic data.

To try it out, download the public sample ULog [6d3c6ab3-d970-4261-890b-685ba4d8f49e.ulg](https://app.roboto.ai/visualize?file=fl_y4thd7ag228i2gvq7d0m) (in [ds_rhq4frqm2tw9](app.roboto.ai/datasets/ds_rhq4frqm2tw9)). Upload it to a dataset in your own account, wait for it to ingest, and then run this action on it.

## Table of Contents

- [Quick Start](#quick-start)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Running](#running)
    - [Local Invocation](#local-invocation)
    - [Hosted Invocation](#hosted-invocation)
- [Development](#development)
- [Deployment](#deployment)

## Quick Start

### Prerequisites

- **Docker** (Engine 19.03+): Local invocation always runs in Docker for production parity
- **Python 3**: A supported version (see [.python-version](.python-version))

```bash
$ docker --version
$ python3 --version
```

### Installation

Set up a virtual environment and install dependencies with the following command:

```bash
$ ./scripts/setup.sh
```

You must be setup to [access Roboto programmatically](https://docs.roboto.ai/getting-started/programmatic-access.html). Verify with the following command:
```bash
$ .venv/bin/roboto users whoami
```

### Running

#### Local Invocation

> **Note:** For complete local invocation documentation and examples, see [DEVELOPING.md](DEVELOPING.md#invoking-locally).

Example invocation:
```bash
$ .venv/bin/roboto --log-level=info actions invoke-local \
    --file-query="dataset_id='<ID>' AND path LIKE '%.mcap'" \
    --dry-run
```


_Running without `--dry-run` may have side-effects, depending on how this action is implemented! See relevant section in [DEVELOPING.md](DEVELOPING.md#code-organization-best-practices) for more._

Full usage:
```bash
$ .venv/bin/roboto actions invoke-local --help
```

#### Hosted Invocation

> **Note:** To run this action on Roboto's hosted compute, you must first build and deploy it. See relevant section in [DEVELOPING.md](DEVELOPING.md#build-and-deployment) for more.

Example invocation:
```bash
$ .venv/bin/roboto actions invoke \
    --file-query="dataset_id='<ID>' AND path LIKE '%.mcap'" \
    create-derivative-topic  # Note required action name parameter for hosted invocation
```


Full usage:
```bash
$ .venv/bin/roboto actions invoke --help
```

## Development

See [DEVELOPING.md](DEVELOPING.md) for detailed information about developing this action, including:
- Project structure and key files
- Local invocation
- Adding dependencies (runtime, system, and development)
- Working with action parameters (including secrets)
- Handling input and output data
- Building and deploying to Roboto

## Deployment

Build and deploy to the Roboto Platform with the following commands:

```bash
$ ./scripts/build.sh
$ ./scripts/deploy.sh [ROBOTO_ORG_ID]
```
