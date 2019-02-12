# Data Simulator
Used to generate datasets based on dictionary


# Motivation

It is sometimes necessary to create simulated data when it is impractical to obtain real data. This is an important technique to generate data that can be used for building models or running services over datasets that may have protected information or may not be available for legal reasons.  The functions in this simulation suite allow a user to:

* Simulate and validate data
* Organize simulated data by nodes in a data model and export to json for easy upload.


## Basic Functionality

#### Dictionary Validation

This function is very helpful for user to validate dictionary
```
data-simulator validate --url https://s3.amazonaws.com/dictionary-artifacts/bhcdictionary/0.4.3/schema.json
```

#### Simulating data

Simulate the data using dictionary
```
data-simulator simulate --url https://s3.amazonaws.com/dictionary-artifacts/bhcdictionary/0.4.3/schema.json --path ./data-simulator/sample_test_data --program DEV --project test
```

Some other options
```
--max_samples 100 # maximum number of instances for each node
--required_only # only simulate required properties
--random # randomly generate the numbers of node instances. If this value is not set, all nodes have the same number of instances
-- node_num_instances_file ./file.txt # generate the numbers of node instances specified in the text file. The file should contain multiple lines, each line have node name and an integer for the node instance
```

#### Submission Order

Generate a submission order given a node name and a dictionary
```
data-simulator submission_order --url https://s3.amazonaws.com/dictionary-artifacts/bhcdictionary/0.4.3/schema.json --node_name case --path ./data-simulator/sample_test_data
```

#### Submitting Data

Submit the data via sheepdog api

```
data-simulator submitting_data --host http://devplanet.planx-pla.net --project DEV/test --dir ./data-simulator/sample_test_data --access_token_file ./token --chunk_size 10
```

## Setup
To install data simulator for common use, run the following command.
```
python setup.py install
```

##  For Development
```
pip install -r dev-requirements.txt
python setup.py develop

```
