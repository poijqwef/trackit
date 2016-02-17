#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This is for reading historical tracks from a netcdf files provided by
https://www.ncdc.noaa.gov/ibtracs/index.php?name=ibtracs-data
"""
from __future__ import division, print_function, absolute_import

import argparse
import sys
import os
import logging
import netCDF4
import ConfigParser
import matplotlib.pyplot as plt

from trackit import __version__

__author__ = "Daniele Rosa"
__copyright__ = "Daniele Rosa"
__license__ = "none"

_logger = logging.getLogger(__name__)

def _historical_tracks_attributes(args):
    """
    Dump attributes for historical tracks file from ibtracs
    """
    print(args.f)
    ncf=netCDF4.Dataset(args.f,'r')
    varNames=ncf.variables.keys() 
    dimNames=ncf.dimensions.keys()
    varNames=list(set(varNames)-set(dimNames))
    print()
    print(args.f)
    print()
    dimSizes=dict()
    for ivar in dimNames:
        if ivar in ncf.dimensions:
            ncvar=ncf.dimensions[ivar]
            print('DIMENSION: ',ncvar.name)
            print('Dim. Size: ',ncvar.size)
            print('Unlimited: ',ncvar.isunlimited())
            dimSizes[ncvar.name]=ncvar.size
        print('~~~~~~~~~~~~~~~~~~~~')
    for ivar in varNames:
        ncvar=ncf.variables[ivar]
        print('VARIABLE: ',ivar)
        print([x for x in ncvar.dimensions])
        print([dimSizes[x] for x in ncvar.dimensions])
        for iatt in ncvar.ncattrs():
            iattValue=ncvar.getncattr(iatt)
            print(iatt,': ',iattValue)
        print('~~~~~~~~~~~~~~~~~~~~')

    lat = ncf.variables['source_lat'][:]
    lon = ncf.variables['source_lon'][:]
    plt.plot(lon[:,:,0],lat[:,:,0],'.')
    plt.savefig('ciao.png',format='png',dpi=300)

    ncf.close()

def _historical_tracks(args):
    """
    Find the historical tracks from ibtracs
    """
    ncf=netCDF4.Dataset(args.f,'r')
    varNames=ncf.variables.keys() 
    dimNames=ncf.dimensions.keys()
    varNames=list(set(varNames)-set(dimNames))
    for ivar in varNames:
        print('VARIABLE: ',ivar)
        ncvar=ncf.variables[ivar]
        for iatt in ncvar.ncattrs():
            iattValue=ncvar.getncattr(iatt)
            print(iatt," -> ",iattValue)


        print('~~~~~~~~~~~~~~~~~~~~')

    for ivar in dimNames:
        print(ivar)
    ncf.close()

    #lats=ncf.variables['latitude'][:]
    #lons=ncf.variables['longitude'][:]
    #ncvar=ncf.variables['C3crop']
    #data=ncvar[0,:,:]
    #mask=np.ma.getmask(data)
    #data[mask]=0.


    return ncf


def parse_args(args):
    """
    Parse command line parameters

    :param args: command line parameters as list of strings
    :return: command line parameters as :obj:`airgparse.Namespace`
    """

    if os.path.exists('input.cfg'):
        config = ConfigParser.ConfigParser()
        config.readfp(open('input.cfg'))
        INPUT_FILE = config.get('IO','input_file')
    else:
        INPUT_FILE = None

    parser = argparse.ArgumentParser(
        description="Historical cyclones reader")
    parser.add_argument(
        '-v',
        '--version',
        action='version',
        version='trackit {ver}'.format(ver=__version__))
    parser.add_argument('-a',action='store_true',required=False,help="input file attributes dump")
    parser.add_argument('-f',required=(INPUT_FILE == None),help="input file")
    args = parser.parse_args(args)
    args.f = args.f or INPUT_FILE
    return args

def main(args):
    args = parse_args(args)
    if args.a:
        _historical_tracks_attributes(args)

    #_historical_tracks(args)
    _logger.info("Script ends here")

def run():
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    main(sys.argv[1:])


if __name__ == "__main__":
    run()
