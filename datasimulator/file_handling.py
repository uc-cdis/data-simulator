from cdislogging import get_logger
logger = get_logger("data-simulator", log_level="info")


def write_submission_order_to_file(submission_order, file_path):
    """ given a correct file path, writes a name-category pair to the file from a list of nodes """
    with open(file_path, "w") as output_file:
        for node in submission_order:
            output_file.write(f"{node.name}\t{node.category}\n")
    return True

