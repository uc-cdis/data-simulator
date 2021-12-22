import os
from os.path import join
import requests
import json

from cdislogging import get_logger

logger = get_logger("data-simulator submitting_data", log_level="info")


def submit_test_data(host, project, dir, access_token_file, max_chunk_size=1):
    """
    Submit the test data. `project` is in the format of `program/project`
    """
    program_name = project.split("/")[0]
    api_root_endpoint = host + "/api/v0/submission"
    api_program_endpoint = "{}/{}".format(api_root_endpoint, program_name)
    api_endpoint = "{}/{}".format(api_root_endpoint, project)

    token = ""
    if os.path.isfile(access_token_file):
        with open(access_token_file, "r") as reader:
            token = reader.read()
        token = token.strip()
    else:
        logger.error("There is no input token text file. Continue anyway!")

    # Create program
    try:
        data = {
            "dbgap_accession_number": project.split("/")[0],
            "type": "program",
            "name": project.split("/")[0],
        }
    except IndexError as e:
        logger.error("Can not create program. Detail {}".format((e)))
        return

    response = requests.put(
        api_root_endpoint,
        data=json.dumps(data),
        headers={
            "content-type": "application/json",
            "Authorization": "bearer " + token,
        },
    )

    if response.status_code not in [200, 201]:
        logger.error("Can not create the program. Response {}".format(response.json()))
        return

    submission_order = ""
    if os.path.isfile(join(dir, "DataImportOrder.txt")):
        with open(join(dir, "DataImportOrder.txt"), "r") as reader:
            submission_order = reader.read()
    else:
        logger.error("There is no DataImportOrder.txt file!")
        return

    submission_order = submission_order.split("\n")

    for fname in submission_order:
        chunk_size = max_chunk_size
        if fname is None or fname == "":
            continue
        logger.info("Submitting {}".format(fname))
        complete_fname = join(dir, fname + ".json")
        if not os.path.exists(complete_fname):
            logger.warn(
                "There is no `{}` file in input directory - nothing to submit".format(
                    complete_fname
                )
            )
            continue
        with open(complete_fname, "r") as rfile:
            data = json.loads(rfile.read())
            if fname == "project":
                response = requests.put(
                    api_program_endpoint,
                    data=json.dumps(data),
                    headers={
                        "content-type": "application/json",
                        "Authorization": "bearer " + token,
                    },
                )
                if response.status_code not in [200, 201]:
                    logger.error(
                        "Can not create the project. Response {}".format(
                            response.json()
                        )
                    )
                    return
                continue

            if not isinstance(data, list):
                data = [data]
            index = 0
            while index < len(data):
                response = requests.put(
                    api_endpoint,
                    data=json.dumps(
                        list(data[index : min(index + chunk_size, len(data))])
                    ),
                    headers={
                        "content-type": "application/json",
                        "Authorization": "bearer " + token,
                    },
                )
                if response.status_code == 504:
                    chunk_size = chunk_size / 2
                    logger.info("Reduce the chunk size by half. {}".format(chunk_size))
                    if chunk_size == 0:
                        break
                    continue

                elif response.status_code != 200:
                    logger.error(
                        "\n\n=============================== {} =================================".format(
                            fname
                        )
                    )
                    logger.error("Failed at chunk {}".format(index / chunk_size))
                    if index == 0:
                        logger.info(response.content)
                    logger.info(response.status_code)

                index = index + chunk_size
