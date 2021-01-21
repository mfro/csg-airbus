# csg-airbus
Converter to help translate from CSV bus schedules to SQL for the airbus site

Based on the [Haskell version](https://github.com/mitchellvitez/csg-airbus) for a different format by Mitchell Vitez

For more on updating Airbus data, see the [airbus tutorial](https://github.com/mitchellvitez/UM-CSG-Tutorials/blob/master/airbus.md)

## Usage

There should be a column in the CSV for trip number, vehicle block number, and 1 for the ***departing time*** for each of the 4 stops. The program will prompt for those column numbers as well as some other values, many of which have defaults if not provided.

Running the converter:
```
$ python3 parse.py trip1.csv trip2.csv
```
