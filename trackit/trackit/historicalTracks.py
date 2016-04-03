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
import mechanize
import inspect

# Mechanize:
# http://wwwsearch.sourceforge.net/mechanize/forms.html
# http://www.pythonforbeginners.com/cheatsheet/python-mechanize-cheat-sheet

from trackit import __version__

__author__ = "Daniele Rosa"
__copyright__ = "Daniele Rosa"
__license__ = "none"

_logger = logging.getLogger(__name__)

basins=dict()
basins[0] = 'North Atlantic'
basins[1] = 'South Atlantic'
basins[2] = 'West Pacific'
basins[3] = 'East Pacific'
basins[4] = 'South Pacific'
basins[5] = 'North Indian'
basins[6] = 'South Indian'
basins[7] = 'Arabian Sea'
basins[8] = 'Bay of Bengal'
basins[9] = 'Eastern Australia'
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

def _downloadIr(args):
    config = ConfigParser.ConfigParser()
    config.readfp(open(args.f))
    user = config.get('noaa','user')
    pwd = config.get('noaa','pwd')
    xmlfile = config.get('IO','xml_file')

    rf=open('response.html','w')

    browser = mechanize.Browser()
    browser.addheaders = [('User-agent','Firefox')]
    browser.set_handle_robots(False)
    baseUrl = 'https://www.nsof.class.noaa.gov/saa/products'

    #loginUrl = baseUrl+'/classlogin'
    #response = browser.open(loginUrl)
    #clsmembers = inspect.getmembers(sys.modules['mechanize'],
    #inspect.isclass)

    loginUrl = baseUrl+'/upload'
    response = browser.open(loginUrl)
    #rf.write(response.read())

    form = browser.select_form(name='f1')
    browser.form.add_file(open(xmlfile),'text/plain',xmlfile)
    print(browser.form)

    sys.exit(0)


    response = browser.submit()
    #rf.write(response.read())

    form = browser.select_form(name='search_frm')
    response = browser.submit()

    browser.select_form(name='rform')
    for i in range(len(browser.find_control('cart').items)):
        browser.find_control('cart').items[i].selected=True

    gotoCart = mechanize._form.SubmitControl('hidden','update_action','Goto Cart')
    browser.add_to_form(gotoCart)

    print(browser.form)
    response = browser.submit()
    rf.write(response.read())
    sys.exit(0)
    # /media/drosa/1T/Data/Cyclones/test.xml

    browser.select_form(name='rform')
    print(browser.form)
    sys.exit(0)

    response = browser.submit()
    rf.write(response.read())
    print('----------------------')
    sys.exit(0)

    for control in browser.form.controls:
        print(control,control.type,control.id,control._value,)
        print('======')

    sys.exit(0)

    #response = browser.submit()
    #response = browser.submit()
    rf.write(response.read())

    for form in browser.forms():
        print("Form name:", form.name)
        print(form)
        print('---------------------')

    sys.exit(0)

    #for form in browser.forms():
    #    print("Form name:", form.name)
    #    print(form)
    #    print('---------------------')

    rf.close()

    sys.exit(0)

    browser['uploaded_file'] = xmlfile
    browser['j_password'] = pwd
    response = browser.submit()
    print(response)
    sys.exit(0)

    #response = browser.follow_link(link)
    for form in browser.forms():
        print("Form name:", form.name)
        print(form)
        print('---------------------')
    sys.exit(0)

    #browser.select_form(name='frmLogin')
    #browser["j_username"] = user
    #browser["j_password"] = pwd
    #browser.submit()

    #print(response.geturl())

    #for link in browser.links():
    #    print(link.text)
    #    print(link.url)
    #    print('----------')
    #    #request = browser.click_link(link)
    #    #response = browser.follow_link(link)

    #print(browser.title())
    #print(user,pwd)

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

    cyclonesDates=dict()
    
    for istorm in range(time.shape[0]):
        stormDate = getDate(time[istorm,0])
        stormBasin = basins[basin[istorm,0]]
        if stormDate >= mindate and stormDate <= maxdate and stormBasin == args.basin:
            #print(stormDate,stormBasin)
            for itime in range(len(time[istorm,:])):
                old_wind = 0
                if time[istorm,itime]:
                    idate=getDate(time[istorm,itime])
                    if idate in cyclonesDates:
                        cyclonesDates[idate]+=1
                    else:
                        cyclonesDates[idate]=1
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
    parser = argparse.ArgumentParser(
        description="Historical cyclones reader")
    parser.add_argument(
        '-v',
        '--version',
        action='version',
        version='trackit {ver}'.format(ver=__version__))
    parser.add_argument('-a',action='store_true',required=False,help="input file attributes dump")
    parser.add_argument('-f',required=False,help="Parameter input file")
    parser.add_argument('-mindate',default='2013-01-01',required=False)
    parser.add_argument('-maxdate',default='2016-12-31',required=False)
    parser.add_argument('-basin',default='West Pacific',required=False)
    parser.add_argument('-plot',action='store_true',required=False)
    args = parser.parse_args(args)
    args.f = 'input.cfg' if not args.f else args.f
    args.f=os.path.abspath(args.f)
    return args

def main(args):
    args = parse_args(args)
    if args.a:
        _historical_tracks_attributes(args)
    else:
        cycloneDates = _historical_tracks(args)
        dates=[]
        counts=[]
        for i,iv in sorted(cycloneDates.items()):
            dates.append(i)
            counts.append(iv)
        
        plt.plot(dates,counts,'-')
        locs,labels = plt.xticks()
        plt.setp(labels,rotation=30)
        axes = plt.gca()
        axes.set_ylim([0,5])
        figFormat='png'
        filename='-'.join([args.basin,args.mindate,args.maxdate])+'.'+figFormat

        plt.title(filename+' - Counts')
        plt.savefig(filename,format=figFormat,dpi=300)

    #_historical_tracks(args)
    _logger.info("Script ends here")

def downloadIr():
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    args = parse_args(sys.argv[1:])
    _downloadIr(args)

def run():
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    args = parse_args(sys.argv[1:])
    if args.a:
        _historical_tracks_attributes(args)
    else:
        cycloneDates = _historical_tracks(args)
        dates=[]
        counts=[]
        for i,iv in sorted(cycloneDates.items()):
            dates.append(i)
            counts.append(iv)
        
        plt.plot(dates,counts,'-')
        locs,labels = plt.xticks()
        plt.setp(labels,rotation=30)
        axes = plt.gca()
        axes.set_ylim([0,5])
        figFormat='png'
        filename='-'.join([args.basin,args.mindate,args.maxdate])+'.'+figFormat

        plt.title(filename+' - Counts')
        plt.savefig(filename,format=figFormat,dpi=300)
    _logger.info("run ends")

if __name__ == "__main__":
    run()
