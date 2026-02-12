# Dataset-Summary-Example

An example of how Roboto Actions can be used to generate AI summaries of datasets


> **Note**: This README was generated from a template. Please customize it to describe what this specific action does: its inputs, outputs, parameters, and/or usage instructions.

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
    create-ai-summary  # Note required action name parameter for hosted invocation
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
