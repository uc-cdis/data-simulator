from .utils import attempt  # same as datasimulator.utils
from cdislogging import get_logger
logger = get_logger("data-simulator", log_level="info")


def write_submission_order_to_file_or_log_error(file_path, submission_order):
    file_open_result = attempt(lambda: open(file_path, "w"))
    if not file_open_result["success"]:
        exception = file_open_result["error"]
        logger.error(f"Error trying to open a new file '{file_path}'. Error: {exception}")
    else:
        output_file = file_open_result["result"]
        for node in submission_order:
            output_file.write(f"{node.name}\t{node.category}\n")
        output_file.close()
        logger.info("DataImportOrderPath.txt has been successfully created.")
    return file_open_result["success"]
