# Testing Guide

This guide explains how to test the email action locally using MailHog, a testing SMTP server.

## What is MailHog?

MailHog is a local email testing tool that:
- Runs an SMTP server that accepts all emails
- Provides a web UI to view captured emails
- Doesn't actually send emails to real recipients
- Perfect for development and testing

## Quick Start

### 1. Start MailHog

Start MailHog using Docker Compose:

```bash
docker-compose -f docker-compose.mailhog.yml up -d
```

This will start MailHog with:
- **SMTP server** on `localhost:1025`
- **Web UI** on `http://localhost:8025`

### 2. Open the MailHog Web UI

Open your browser to view the MailHog inbox:

```bash
open http://localhost:8025
```

You should see an empty inbox ready to capture emails.

### 3. Run the Action Locally

Run the action with MailHog SMTP settings:

```bash
.venv/bin/roboto --log-level=info actions invoke-local \
    --file-query="dataset_id='<DATASET_ID>'" \
    --parameter smtp_host=localhost \
    --parameter smtp_port=1025 \
    --parameter smtp_username=test@example.com \
    --parameter smtp_password=any-password \
    --parameter email_sender=action@roboto.local \
    --parameter email_recipient=team@roboto.local
```

**Note:** MailHog doesn't require authentication, so you can use any username/password.

### 4. View the Email

After the action completes:
1. Refresh the MailHog web UI at `http://localhost:8025`
2. You should see the email that was sent
3. Click on it to view the full content

### 5. Stop MailHog

When you're done testing:

```bash
docker-compose -f docker-compose.mailhog.yml down
```

## Troubleshooting

### Connection Refused Error

If you get a connection error, make sure:
1. MailHog is running: `docker ps | grep mailhog`
2. Port 1025 is not in use by another service
3. You're using `localhost` (not `127.0.0.1` or `host.docker.internal`)

### Email Not Appearing

If the email doesn't appear in MailHog:
1. Check the action logs for errors
2. Verify the SMTP connection succeeded
3. Refresh the MailHog web UI
4. Check that you're using port `1025` for SMTP (not `8025`)

### Docker Network Issues

If running the action in Docker and it can't connect to MailHog:
- Use `host.docker.internal` instead of `localhost` for the SMTP host
- Or add the action container to the same Docker network as MailHog

## Testing Different Scenarios

### Test with No Files

```bash
.venv/bin/roboto actions invoke-local \
    --file-query="dataset_id='nonexistent'" \
    --parameter smtp_host=localhost \
    --parameter smtp_port=1025 \
    --parameter smtp_username=test \
    --parameter smtp_password=test \
    --parameter email_sender=action@roboto.local \
    --parameter email_recipient=team@roboto.local
```

Expected: Email with subject containing "[NO FILES]"

### Test with Multiple Files

```bash
.venv/bin/roboto actions invoke-local \
    --file-query="dataset_id='<DATASET_ID>' AND path LIKE '%.mcap'" \
    --parameter smtp_host=localhost \
    --parameter smtp_port=1025 \
    --parameter smtp_username=test \
    --parameter smtp_password=test \
    --parameter email_sender=action@roboto.local \
    --parameter email_recipient=team@roboto.local
```

Expected: Email with detailed file information and "[SUCCESS]" in subject

### Test Custom Subject Prefix

```bash
.venv/bin/roboto actions invoke-local \
    --file-query="dataset_id='<DATASET_ID>'" \
    --parameter smtp_host=localhost \
    --parameter smtp_port=1025 \
    --parameter smtp_username=test \
    --parameter smtp_password=test \
    --parameter email_sender=action@roboto.local \
    --parameter email_recipient=team@roboto.local \
    --parameter email_subject_prefix="Custom Report"
```

Expected: Email subject starts with "Custom Report"

## Alternative: Using MailHog CLI

You can also install MailHog directly (without Docker):

```bash
# macOS
brew install mailhog
mailhog

# Linux
go install github.com/mailhog/MailHog@latest
~/go/bin/MailHog
```

Then access the web UI at `http://localhost:8025` as before.

