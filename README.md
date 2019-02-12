# data-simulator
Used to generate datasets based on dictionary


# Motivation

It is sometimes necessary to create simulated data when it is impractical to obtain real data. This is an important technique to generate data that can be used for building models or running services over datasets that may have protected information or may not be available for legal reasons.  The functions in this simulation suite allow a user to:

* Simulate and validate data
* Organize simulated data by nodes in a data model and export to json for easy upload.


## Basics of Simulation



### Example Simulation

The following will simulate 10 rows from our sample compendium. 

```
source('https://raw.githubusercontent.com/occ-data/data-simulator/master/SimData.R')
compendium <- read.csv('https://raw.githubusercontent.com/occ-data/data-simulator/master/SampleCompendium/sampleClinical.csv', header=T, stringsAsFactors = F)


```

## Validation
