import camera_logging

log_client, dcr, stream_name = camera_logging.initialize_azure_connection()
camera_logging.output_log_to_azure(log_client, dcr, stream_name, "Logging Test")
