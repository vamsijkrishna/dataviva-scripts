dataviva-scripts
================

Helper scripts for DataViva data calculations and transformations

* ```git clone https://github.com/DataViva/dataviva-scripts.git dataviva-scripts```
* ```cd dataviva-scripts```
* ```git submodule update --init --recursive``` <- necessary for all product space calcs e.g. rca, distance, opp_gain
* ```pip install -r requirements.txt ```

### Caveats
* Need the following environment vars to be set:
 * ```DATAVIVA_DB_NAME```
 * ```DATAVIVA2_DB_NAME```
 * ```DATAVIVA_DB_USER```
 * ```DATAVIVA2_DB_USER```
 * ```DATAVIVA_DB_PW```
 * ```DATAVIVA2_DB_PW```
* Need unrar tool installed
 * ```brew install unrar```

### Environment Configuration
Please see the the documtation for getting your environment set up in the  [wiki](https://github.com/DataViva/dataviva-scripts/wiki/Configuration).

### Instructions for Running Scripts
Please see the documation for how the run the scripts for adding new years of data in the [wiki](https://github.com/DataViva/dataviva-scripts/wiki).