#!/usr/bin/env python3
"""
Tests the email_builder module directly with MailHog, without invoking the full action.
"""

import sys
from pathlib import Path

# Add src to path so we can import the module
sys.path.insert(0, str(Path(__file__).parent / "src"))

from example_email_action.email_builder import IncrementalEmailBuilder, send_email


def main():
    print("Testing email functionality with MailHog")
    print("=" * 60)
    
    # Create an incremental email builder
    builder = IncrementalEmailBuilder(
        sender="test-action@roboto.local",
        recipient="team@roboto.local",
        subject="Test Email Report"
    )
    
    # Simulate processing files
    print("\nSimulating file processing")
    builder.append_subject("- 3 file(s) processed")
    
    builder.append_body("File Ingest Report")
    builder.append_body("=" * 50)
    builder.append_body("Total files processed: 3")
    builder.append_body("")
    
    # File 1
    builder.append_body("File 1: data/sensor_data.mcap")
    builder.append_body("  File ID: file_abc123")
    builder.append_body("  Size: 1,234,567 bytes (1205.63 KB)")
    builder.append_body("  Topics (2):")
    builder.append_body("    - /sensor/imu (sensor_msgs/Imu)")
    builder.append_body("    - /sensor/gps (sensor_msgs/NavSatFix)")
    builder.append_body("")
    
    # File 2
    builder.append_body("File 2: data/camera_feed.mcap")
    builder.append_body("  File ID: file_def456")
    builder.append_body("  Size: 5,678,901 bytes (5545.80 KB)")
    builder.append_body("  Topics (1):")
    builder.append_body("    - /camera/image (sensor_msgs/Image)")
    builder.append_body("")
    
    # File 3
    builder.append_body("File 3: logs/system.log")
    builder.append_body("  File ID: file_ghi789")
    builder.append_body("  Size: 12,345 bytes (12.06 KB)")
    builder.append_body("  Topics: None")
    builder.append_body("")
    
    builder.append_body("=" * 50)
    builder.append_body("End of report")
    
    builder.append_subject("[SUCCESS]")
    
    # Build the email
    print("Building email message")
    message = builder.build()
    
    print("\nEmail Details:")
    print(f"  From: {message['From']}")
    print(f"  To: {message['To']}")
    print(f"  Subject: {message['Subject']}")
    print(f"  Body length: {len(message.get_content())} characters")
    
    # Send via MailHog
    print("\nSending email to MailHog (localhost:1025)")
    try:
        send_email(
            smtp_host="localhost",
            smtp_port=1025,
            username="test",  # MailHog doesn't require auth
            password="test",
            message=message
        )
        print("Email sent successfully!")
        print("\n" + "=" * 60)
        print("Check the MailHog web UI at: http://localhost:8025")
        print("=" * 60)
    except Exception as e:
        print(f"Failed to send email: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

