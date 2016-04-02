# Trackit

This wants to be a Machine Learning tool for tracking atmospheric phenomena such as tropical and extra-tropical cyclone from observationally derived data.

First, cyclone historcal data [ibtracs](http://www.ncdc.noaa.gov/oa/ibtracs/) is considered.

## Install

I activate the virtual environment so that the install stays contained in there:

    virtualenv myenv
    source myenv/bin/activate

## Configuration

Although the code is free, the configuration parameters are contained in an encrypted file [input.cfg.gpg](./input.cfg.pgp) of which a template is provided [input.cfg.template](./input.cfg.template).


## Execution

    cd trackit
    python setup.py install && historicalTracks -a
    python setup.py install && historical_tracks

