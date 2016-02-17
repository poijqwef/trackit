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
import numpy
import matplotlib.pyplot as plt
import datetime

from trackit import __version__

__author__ = "Daniele Rosa"
__copyright__ = "Daniele Rosa"
__license__ = "none"

_logger = logging.getLogger(__name__)

basins=dict()
basins[0 ] = 'North Atlantic'
basins[1 ] = 'South Atlantic'
basins[2 ] = 'West Pacific'
basins[3 ] = 'East Pacific'
basins[4 ] = 'South Pacific'
basins[5 ] = 'North Indian'
basins[6 ] = 'South Indian'
basins[7 ] = 'Arabian Sea'
basins[8 ] = 'Bay of Bengal'
basins[9 ] = 'Eastern Australia'
basins[10] = 'Western Australia'
basins[11] = 'Central Pacific'
basins[12] = 'Carribbean Sea'
basins[13] = 'Gulf of Mexico'
basins[14] = 'Missing'

def getDate(jday,jdayRef='1858-11-17 00:00:00'):
    if not jday:
        return jday
    jDateRef = datetime.datetime.strptime(jdayRef,'%Y-%m-%d %H:%M:%S').toordinal()
    jdayToRef = jday + jDateRef 
    delta = datetime.timedelta(0,(jdayToRef - int(jdayToRef))*86400)
    date = datetime.datetime.fromordinal(int(jdayToRef)) + delta
    return date

def _historical_tracks_attributes(args):
    """
    Dumps attributes for historical tracks file from ibtracs
    """
    print(args.f)
    ncf=netCDF4.Dataset(args.f,'r')
    varNames=ncf.variables.keys() 
    dimNames=ncf.dimensions.keys()
    varNames=list(set(varNames)-set(dimNames))
    print()
    print(args.f)
    print()
    print('VARIABLES: ',varNames)
    print('DIMENSIONS: ',dimNames)
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

    ncf.close()

def _historical_tracks(args):
    """
    Finds the historical tracks from ibtracs
    """
    ncf=netCDF4.Dataset(args.f,'r')
    lat = numpy.mean(ncf.variables['source_lat'][:],2)
    lon = numpy.mean(ncf.variables['source_lon'][:],2)
    wind = numpy.mean(ncf.variables['source_wind'][:],2)
    time = ncf.variables['source_time'][:]
    basin = ncf.variables['basin'][:]
    mindate = datetime.datetime.strptime(args.mindate,'%Y-%m-%d')
    maxdate = datetime.datetime.strptime(args.maxdate,'%Y-%m-%d')
    stormDays = 21
    maxWind = 100

    cyclonesDates=[]
    
    for istorm in range(time.shape[0]):
        stormDate = getDate(time[istorm,0])
        stormBasin = basins[basin[istorm,0]]
        if stormDate >= mindate and stormDate <= maxdate and stormBasin == args.basin:
            #print(stormDate,stormBasin)
            for itime in range(len(time[istorm,:])):
                old_wind = 0
                if time[istorm,itime]:
                    cyclonesDates.append(getDate(time[istorm,itime]))
                    #days = time[istorm,itime] - time[istorm,0]
                    #marker_color=str(days/stormDays)
                    if wind[istorm,itime]:
                        old_wind = wind[istorm,itime]
                    if args.plot:
                        marker_color = str(max(0.,1. - old_wind/maxWind))
                        plt.plot(lon[istorm,itime],lat[istorm,itime],'.',color=marker_color)

    ncf.close()
    if args.plot:
        figFormat='png'
        filename='-'.join([args.basin,args.mindate,args.maxdate])+'.'+figFormat
        plt.title(filename+' - Ref. Wind for dot colors: '+str(maxWind))
        plt.savefig(filename,format=figFormat,dpi=300)

    return cyclonesDates

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
        INPUT_FILE_README = config.get('IO','input_file_readme')
    else:
        INPUT_FILE = None
        INPUT_FILE_README = None

    parser = argparse.ArgumentParser(
        description="Historical cyclones reader")
    parser.add_argument(
        '-v',
        '--version',
        action='version',
        version='trackit {ver}'.format(ver=__version__))
    parser.add_argument('-a',action='store_true',required=False,help="input file attributes dump")
    parser.add_argument('-f',required=(INPUT_FILE == None),help="input file")
    parser.add_argument('-mindate',default='2014-01-01',required=False)
    parser.add_argument('-maxdate',default='2016-12-31',required=False)
    parser.add_argument('-basin',default='West Pacific',required=False)
    parser.add_argument('-plot',action='store_true',required=False)
    args = parser.parse_args(args)
    args.f = args.f or INPUT_FILE
    return args

def main(args):
    args = parse_args(args)
    if args.a:
        _historical_tracks_attributes(args)
    else:
        cycloneDates = _historical_tracks(args)
        print(sorted(cycloneDates))
        print(len(cycloneDates))

    #_historical_tracks(args)
    _logger.info("Script ends here")

def run():
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    main(sys.argv[1:])


if __name__ == "__main__":
    run()
