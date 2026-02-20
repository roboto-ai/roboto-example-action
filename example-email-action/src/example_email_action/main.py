import roboto

from .email_builder import IncrementalEmailBuilder, send_email
from .logger import logger


def main(context: roboto.InvocationContext) -> None:
    logger.setLevel(context.log_level)

    # Get SMTP configuration from action parameters
    smtp_host = context.get_parameter("smtp_host")
    smtp_port = int(context.get_parameter("smtp_port"))
    smtp_username = context.get_parameter("smtp_username")
    smtp_password = context.get_parameter("smtp_password")
    email_sender = context.get_parameter("email_sender")
    email_recipient = context.get_parameter("email_recipient")
    email_subject_prefix = context.get_parameter("email_subject_prefix")

    logger.info("Initializing email builder...")

    # Initialize the incremental email builder
    email_builder = IncrementalEmailBuilder(
        sender=email_sender,
        recipient=email_recipient,
        subject=email_subject_prefix
    )

    action_input = context.get_input()

    if action_input.files:
        file_count = len(action_input.files)
        logger.info("Processing %d input file(s):", file_count)

        # Add summary to subject
        email_builder.append_subject(f"- {file_count} file(s) processed")

        # Add header to email body
        email_builder.append_body("File Ingest Report")
        email_builder.append_body("=" * 50)
        email_builder.append_body(f"Total files processed: {file_count}")
        email_builder.append_body("")

        # Process each file and aggregate details
        for idx, (file, local_path) in enumerate(action_input.files, start=1):
            logger.info("Processing file %d/%d: %s", idx, file_count, file.relative_path)

            # Add file details to email body
            email_builder.append_body(f"File {idx}: {file.relative_path}")
            email_builder.append_body(f"  File ID: {file.file_id}")

            if local_path:
                # File is downloaded and available at local_path
                file_size = local_path.stat().st_size
                logger.info("  Local path: %s", local_path)
                logger.info("  File size: %d bytes", file_size)

                email_builder.append_body(f"  Size: {file_size:,} bytes ({file_size / 1024:.2f} KB)")
                email_builder.append_body(f"  Local path: {local_path}")
            else:
                logger.warning("  File not downloaded (requires_downloaded_inputs may be false)")
                email_builder.append_body("  Status: Not downloaded")

            # Add topic information if available
            topics = list(file.get_topics())
            if topics:
                logger.info("  Found %d topic(s)", len(topics))
                email_builder.append_body(f"  Topics ({len(topics)}):")
                for topic in topics:
                    logger.info("    - %s (%s)", topic.topic_name, topic.schema_name)
                    email_builder.append_body(f"    - {topic.topic_name} ({topic.schema_name})")
            else:
                email_builder.append_body("  Topics: None")

            # Add separator between files
            email_builder.append_body("")

        # Add footer
        email_builder.append_body("=" * 50)
        email_builder.append_body("End of report")

        # Mark as success in subject
        email_builder.append_subject("[SUCCESS]")

    else:
        logger.info("No input files provided")
        email_builder.append_subject("- No files processed")
        email_builder.append_body("No input files were provided to this action.")
        email_builder.append_subject("[NO FILES]")

    # Build and send the email
    logger.info("Building email message...")
    email_message = email_builder.build()

    logger.info("Sending email to %s via %s:%d...", email_recipient, smtp_host, smtp_port)

    # NOTE: Ensure that one invocation of this action does not send multiple emails
    # If this is necessary, make sure to implement waits or other throttling mechanisms, otherwise
    # you may run into issues with email providers blocking your account for sending too many emails 
    # in a short period of time.
    try:
        send_email(
            smtp_host=smtp_host,
            smtp_port=smtp_port,
            username=smtp_username,
            password=smtp_password,
            message=email_message,
        )
        logger.info("Email sent successfully!")
    except Exception as e:
        logger.error("Failed to send email: %s", str(e))
        raise
