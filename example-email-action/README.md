# example-email-action

An example action that sends email reports when files are ingested into Roboto. This action demonstrates how to:
- Send emails from within a Roboto Action using SMTP
- Incrementally build email content while processing files
- Aggregate file metadata and topic information
- Use Roboto Secrets for secure credential management

Also included is an optional email builder utility, created with the assumption that this kind of action is intended to programmatically build a report over the course of the action's execution.

## Overview

This action processes input files and sends a detailed email report containing:
- Total number of files processed
- File paths and IDs
- File sizes
- Topic information (if available)
- Processing status

The email is built incrementally as files are processed, then sent once all files have been analyzed.

## Table of Contents

- [Quick Start](#quick-start)
  - [Prerequisites](#prerequisites)
  - [Configuration](#configuration)
  - [Installation](#installation)
  - [Running](#running)
    - [Local Invocation](#local-invocation)
    - [Hosted Invocation](#hosted-invocation)
- [Development](#development)
- [Deployment](#deployment)

## Quick Start

### Prerequisites

- **Docker**
- **Python 3.13**: 
- **SMTP Server Access**: You'll need credentials for an SMTP server

```bash
$ docker --version
$ python3 --version
```

### Configuration

This action requires the following parameters:

| Parameter | Required | Description | Example |
|-----------|----------|-------------|---------|
| `smtp_host` | Yes | SMTP server hostname | `smtp.gmail.com` |
| `smtp_port` | Yes | SMTP server port | `587` (TLS) or `465` (SSL) |
| `smtp_username` | Yes | SMTP login username | `your-email@gmail.com` |
| `smtp_password` | Yes | SMTP password (use Roboto Secret!) | `secret://your-org/smtp-password` |
| `email_sender` | Yes | Email sender address | `notifications@example.com` |
| `email_recipient` | Yes | Email recipient address | `team@example.com` |
| `email_subject_prefix` | Yes | Subject line prefix | `Roboto File Ingest Report: ` |

#### Setting up SMTP Credentials as Secrets

For security, store your SMTP password as a Roboto Secret:

```bash
# Create a secret for your SMTP password (CLI)
$ roboto secrets write --org <your-org-id> smtp-password "your-actual-password"

# Use the secret URI in your action parameters
# secret://your-org-id/smtp-password
```

#### Gmail-specific Setup

If using Gmail, you'll need to:
1. You will need to enable 2-factor authentication on the intended sender's Google account. If your organization uses Okta or other auth services, this may require additional steps or may even be restricted. Contact your IT administrator for information.
2. Generate an [App Password](https://support.google.com/accounts/answer/185833) - this allows you to reserve your regular password while allowing this action to authenticate.

    **Warning**: *Simply copying and pasting the generated app password may not work, as this can result in non-ASCII characters being passed to Roboto. It is recommended to type the password in manually when creating or updating the secret.*

3. Use the app password (and not your regular password) as the `smtp_password`
4. Use `smtp.gmail.com` as the host and `587` as the port

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

Example local invocation:
```bash
$ roboto --log-level=info actions invoke-local \
    --file-query="dataset_id='<DATASET_ID>' AND path LIKE '%.mcap'" \
    --parameter smtp_host=smtp.gmail.com \
    --parameter smtp_port=587 \
    --parameter smtp_username=your-email@gmail.com \
    --parameter smtp_password=secret://your-org/smtp-password \
    --parameter email_sender=notifications@example.com \
    --parameter email_recipient=team@example.com \
    --parameter email_subject_prefix="File Ingest Report"
```

> **Warning**: This action will send an actual email! Make sure your SMTP credentials are correct and you're comfortable with the recipient address.

Full usage:
```bash
$ roboto actions invoke-local --help
```

#### Hosted Invocation

> **Note:** To run this action on Roboto's hosted compute, you must first build and deploy it. See relevant section in [DEVELOPING.md](DEVELOPING.md#build-and-deployment) for more.

Example invocation:
```bash
$ roboto actions invoke \
    --file-query="dataset_id='<ID>>' AND path LIKE '%.bag'" \
    --parameter smtp_host=host.docker.internal \     # update with your SMTP host
    --parameter smtp_port=1025 \                     # update with your SMTP port
    --parameter smtp_username=test@example.com \     # update with your SMTP username
    --parameter smtp_password=any-password \         # update with your SMTP password
    --parameter email_sender=action@roboto.local \   # update with your email sender address
    --parameter email_recipient=team@roboto.local \  # update with your email recipient address
    --parameter email_subject_prefix="Roboto Alert: "
```


Full usage:
```bash
$ roboto actions invoke --help
```

## Example Email Output

When the action runs successfully, it will send an email that could look like this:

**Subject:** `Roboto Alert: Example Action - 3 file(s) processed [SUCCESS]`

**Body:**
```
File Ingest Report
==================================================
Total files processed: 3

File 1: data/sensor_data.mcap
  File ID: file_abc123
  Size: 1,234,567 bytes (1205.63 KB)
  Local path: /tmp/roboto/file_abc123
  Topics (2):
    - /sensor/imu (sensor_msgs/Imu)
    - /sensor/gps (sensor_msgs/NavSatFix)

File 2: data/camera_feed.mcap
  File ID: file_def456
  Size: 5,678,901 bytes (5545.80 KB)
  Local path: /tmp/roboto/file_def456
  Topics (1):
    - /camera/image (sensor_msgs/Image)

File 3: logs/system.log
  File ID: file_ghi789
  Size: 12,345 bytes (12.06 KB)
  Local path: /tmp/roboto/file_ghi789
  Topics: None

==================================================
End of report
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
