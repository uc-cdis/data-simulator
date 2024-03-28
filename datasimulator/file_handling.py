from cdislogging import get_logger
logger = get_logger("data-simulator", log_level="info")


def try_writing_to_file(file_path, action):
    """
    Args:
        file_path (str): alleged path to file
        action (callable): whatever you want to do with the open file

    Returns: result dict in the form
        - "success" (bool): whether it succeeded
        - "result": action return if successful
        - "error": exception if failed
    """
    try:
        output_file = open(file_path, "w")
        result = action(output_file)
        output_file.close()
        return {"success": True, "result": result}
    except Exception as e:
        logger.error(f"Error trying to open a new file '{file_path}'. Error: {e}")
        return {"success": False, "result": e}


def write_submission_order_to_file(submission_order):
    def write_node_to_file(output_file):
        for node in submission_order:
            output_file.write(f"{node.name}\t{node.category}\n")
    return write_node_to_file

