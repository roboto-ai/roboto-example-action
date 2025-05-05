# Roboto Example Action

This repository contains example Roboto Actions, intended as straightforward starting points for learning or building with Roboto.

## Prerequisites

Make sure Docker is installed on your machine:  
- [Docker Installation Guide](https://docs.docker.com/engine/install/)

Ensure your Roboto account is set up and the CLI is installed:  
- [Roboto Account Setup](https://docs.roboto.ai/getting-started/account.html)

## Quickstart

Follow these steps to get an Action running:

### 1. Clone the Repository

Clone the repository using the command below:

```shell
git clone https://github.com/roboto-ai/roboto-example-action.git
```

### 2. Build and Deploy an Action

Navigate into one of the top-level Action directories in this package, e.g.

```shell
cd roboto-example-action/tag_dataset
```

Then build and deploy the Action:

```shell
./scripts/setup.sh
./scripts/build.sh
./scripts/deploy.sh
```

You can now run this Action in Roboto via the CLI or web app.

## Contributing

We welcome suggestions and contributions! If you have ideas for improvement or run into any issues, feel free to open an issue or pull request.