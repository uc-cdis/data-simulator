from .utils import attempt  # same as datasimulator.utils
from cdislogging import get_logger
logger = get_logger("data-simulator", log_level="info")


def write_node_to_file(outfile, node):
    outfile.write(f"{node.name}\t{node.category}\n")


def write_to_file_or_log_error(file_path, submission_order):
    file_open_result = attempt(lambda: open(file_path, "w"))
    if not file_open_result["success"]:
        exception = file_open_result["error"]
        logger.error(f"Error trying to open a new file DataImportOrderPath. Error: {exception}")
    else:
        output_file = file_open_result["result"]
        for node in submission_order:
            write_node_to_file(output_file, node)
        logger.info("DataImportOrderPath.txt has been successfully created.")
    return file_open_result["success"]
