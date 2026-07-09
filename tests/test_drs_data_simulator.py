import os
from pathlib import Path
from datasimulator.graph import Graph
from dictionaryutils import DataDictionary, dictionary
import urllib.request
import json


def local_simulation(
    n_samples: int = 50,
    local_test_path: str = "tests/TestDataTemp",
    run: bool = False,
    dictionary_url: str | None = None,
):
    """
    Creates local, mocked data per a specified schema.
    Mocked data will have up to N entries.
    Set run = True locally before running test to simulate data.

    params:
    -- n_samples =  Number of mocked entries is randomly selected between 0 & this number.
    -- local_test_path = Folder path for local, mocked data
    -- run = Determines whether to generate local, mocked data. Defaults to false.
    -- dictionary_url = URL path to schema. Required to run.
    """

    # Skip test if local run is not required
    if run is False:
        return
    # Skip tests if dictionary url is not provided.
    if dictionary_url is None:
        return

    # Set up test (delete any existing files in test data folder before test starts)
    test_generated_files = os.listdir(local_test_path)
    for file in test_generated_files:
        os.remove(local_test_path + f"/{file}")

    # Create graph based on specified data dictionary (from url)
    dictionary.init(DataDictionary(url=dictionary_url))
    graph = Graph(dictionary, "DEV", "test")  # create graph
    graph.generate_nodes_from_dictionary()  # create node
    graph.construct_graph_edges()  # create link

    # Check if graph passess validaiton
    assert graph.graph_validation()

    # Simulate data whether the graph passes validation or not
    graph.simulate_graph_data(path=local_test_path, n_samples=n_samples)


def test_drs_data_simulator(
    drs_run: bool | None = bool,
    staging_base_url: str | None = None,
    dictionary_url: str | None = None,
):
    """
    Creates mocked data in local path with staging drs uri data.
    User must set drs_run = True to enable local generation.
    User must define staging_base_url.
    User must define schema dictionary url.
    Otherwise, test will effect be empty by default.

    Running this pytest will create the mocked JSON data locally, per the specified path.
    To convert the test data files to a PFB .avro:
    1. Run this pytest
    2. Run CLI command in terminal: pfb from -o schema.avro dict <dictionary_url_here>
    3. Run CLI command in terminal: pfb from -o data.avro json -s schema.avro --program DEV --project test tests/TestDataTemp
    """
    # Take no action unless user sets drs_run = True for a local simulation
    if drs_run is False:
        return
    # Take no action if staging url is not provided
    if staging_base_url is None:
        return
    # Take no action if (schema) dictionary url is not provided
    if dictionary_url is None:
        return
    # Generate mocked data from dictionary url schema
    local_simulation(
        n_samples=50,
        local_test_path="tests/TestDataTemp",
        run=True,
        dictionary_url=dictionary_url,
    )
    # Get local tests reference info
    local_file_name = "tests/TestDataTemp/submitted_aligned_reads.json"
    with open(local_file_name, "r") as local_json:
        local_records = json.load(local_json)

    # Init variables
    n_original_records = len(local_records)
    limit = 100
    page = 1
    updated_records = []
    n_updated_records = 0
    # staging_base_url =

    # Update local mocked data with staging DRS URI info
    while n_updated_records < n_original_records:
        # print(f"beginning loop... page: {page}")
        url = staging_base_url + "&page=" + str(page) + "&limit=" + str(limit)
        with urllib.request.urlopen(url) as response:
            response_body = response.read()
            url_schema = json.loads(response_body)
        schema_records = url_schema["records"]
        # Exit if schema records are empty
        if schema_records == []:
            # print(f"breaking out of loop... page: {page}")
            break

        # Extract updated records
        for schema in schema_records:
            # Extract local_record & update some info to match that of a schema
            local_entry = local_records[n_updated_records]
            local_entry["md5sum"] = "test_" + schema["hashes"]["md5"]
            local_entry["bucket_path"] = schema["urls"]
            local_entry["did"] = schema["did"]
            schema_file_name = schema["file_name"]
            if schema_file_name != "":
                local_entry["file_name"] = "test_" + str(schema_file_name)
            # Append new to new content list and update count
            updated_records.append(local_entry)
            n_updated_records += 1
            # Exit if updated records if we've updated all available local test records
            if n_updated_records == n_original_records:
                break

        # Update url page number
        page += 1

    # Save new json with updated records after exiting while loop (overwrites original mock file)
    with open("tests/TestDataTemp/submitted_aligned_reads.json", "w") as file:
        json.dump(updated_records, file)
