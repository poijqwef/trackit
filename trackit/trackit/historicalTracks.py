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
from selenium import webdriver
import inspect
import re
import time
import random

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

def writeFtp(numbers,user,output_dir='.'):

    if type(numbers) == int:
        numbers = [numbers]
    elif type(numbers) == list:
        assert type(numbers[0]) == int,'This is not a list of ints'
    else:
        raise Exception,'error: either pass a int or a list of ints'
   
    logTimeStamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')

    for i in numbers:

        confirmationNumber = i
        confirmationNumberFile = open(output_dir+'/'+str(confirmationNumber)+'.ftp.'+logTimeStamp+'.sh','w')
        confirmationNumberFile.write("#!/bin/bash\n\n")
        ftpFileContent=[
        "HOST='ftp.class.ngdc.noaa.gov'",
        "USER='anonymous'",
        "PASSWD='"+user+"'",
        "ORDERID="+str(confirmationNumber),
        "ftp -n $HOST << EOF",
        "user $USER $PASSWD",
        "binary",
        "cd 2$ORDERID/001",
        "prompt",
        "verbose on",
        "mget *",
        "bye",
        "EOF",
        '',
        ]

        for i in ftpFileContent:
            confirmationNumberFile.write(i+'\n')
        confirmationNumberFile.close()

def e(value):
    sys.exit(value)

def s(value):
    time.sleep(max(0,value+random.random()-0.5))

def getDate(jday,jdayRef='1858-11-17 00:00:00'):
    if not jday:
        return jday
    jDateRef = datetime.datetime.strptime(jdayRef,'%Y-%m-%d %H:%M:%S').toordinal()
    jdayToRef = jday + jDateRef 
    delta = datetime.timedelta(0,(jdayToRef - int(jdayToRef))*86400)
    date = datetime.datetime.fromordinal(int(jdayToRef)) + delta
    return date

def _downloadIr(args,dates):

    user = args.user
    pwd = args.pwd

    sleepTime=3

    delta = datetime.timedelta(0,0.5*args.hourTimeWindow*3600)

    baseUrl = 'https://www.nsof.class.noaa.gov/saa/products'

    for i in dates:

        start_date = i-delta
        end_date = i+delta
        start_date_string = start_date.strftime('%Y-%m-%d')
        end_date_string = end_date.strftime('%Y-%m-%d')
        start_time_string = start_date.strftime('%H:%M:%S')
        end_time_string = end_date.strftime('%H:%M:%S')
        comment_string = start_date_string+' '+start_time_string+' '+end_date_string+' '+end_time_string

        print('Doing: '+comment_string)

        driver = webdriver.Firefox()
        driver.get(baseUrl+'/catSearch')

        s(sleepTime)
        driver.get(baseUrl+'/classlogin')
        s(sleepTime)
        username = driver.find_element_by_name("j_username")
        password = driver.find_element_by_name("j_password")
        username.send_keys(user)
        password.send_keys(pwd)
        login_button = driver.find_element_by_xpath("//input[@class='Button'][@value='Login'][@type='submit']")
        login_button.click()
        s(sleepTime)

        driver.get(baseUrl+'/catSearch')
        gvar_img_select = driver.find_element_by_xpath("//select/option[@value='GVAR_IMG']")
        gvar_img_select.click()
        gvar_img_go = driver.find_element_by_xpath("//input[@type='image'][@name='submit'][@src='../images/go.gif']")
        gvar_img_go.click()
        start_date_input = driver.find_element_by_xpath("//input[@name='start_date'][@type='text'][@id='start_date']")
        start_date_input.clear()
        start_date_input.send_keys(start_date_string)
        start_time_input = driver.find_element_by_xpath("//input[@name='start_time'][@type='text'][@id='start_time']")
        start_time_input.clear()
        start_time_input.send_keys(start_time_string)
        end_date_input = driver.find_element_by_xpath("//input[@name='end_date'][@type='text'][@id='end_date']")
        end_date_input.clear()
        end_date_input.send_keys(end_date_string)
        end_time_input = driver.find_element_by_xpath("//input[@name='end_time'][@type='text'][@id='end_time']")
        end_time_input.clear()
        end_time_input.send_keys(end_time_string)
        range_input = driver.find_element_by_xpath("//input[@name='between_through'][@type='radio'][@id='between_through_T']")
        range_input.click()
        for i in ['R','RSO','SRSO','O']:
            checkbox= driver.find_element_by_xpath("//input[@name='Satellite Schedule'][@type='checkbox'][@value='"+i+"']")
            if not checkbox.is_selected():
                checkbox.click()
        checkbox= driver.find_element_by_xpath("//input[@name='Coverage'][@type='checkbox'][@value='FD']")
        if not checkbox.is_selected():
            checkbox.click()
        for i in ['G08','G09','G10','G11','G12','G13','G14','G15']:
            select_satellite = driver.find_element_by_xpath("//select/option[@name='Satellite'][@value='"+i+"'][@id='"+i+"']")
            select_satellite.click()
        search_button = driver.find_element_by_xpath("//input[@class='Button'][@value='Search']")
        search_button.click()
        s(sleepTime)
        selects_datasets = driver.find_elements_by_xpath("//select[@name='AddGroup']/option")
        if len(selects_datasets)>2:
            print('\nerror: not expecting more than on page to select: shrink time search')
            sys.exit(1)
        select_datasets = driver.find_element_by_xpath("//select[@name='AddGroup']/option[2]")
        select_datasets.click()
        s(sleepTime)
        goto_cart = driver.find_element_by_xpath("//input[@value='Goto Cart'][@class='Button']")
        goto_cart.click()
        s(sleepTime)
        formats = driver.find_elements_by_xpath("//select/option[@value='NetCDF']")
        for i in formats:
            i.click()
        order_comment = driver.find_element_by_xpath("//input[@type='text'][@name='order_comment']")
        order_comment.send_keys(comment_string.replace('-',' ').replace(':',' '))
        s(sleepTime)
        place_order = driver.find_element_by_xpath("//input[@value='PlaceOrder'][@name='cocoon-action'][@class='Button']")

        place_order.click()

        #responseFile = 'response.html'
        #with open(responseFile,'r') as f:
        #    wholeFile = ''.join(f.readlines())
        wholeFile = ''.join(driver.page_source)
        wholeFile = wholeFile.replace('\t',' ').replace('\n',' ')
        squeezer = re.compile(' +')
        wholeFile = squeezer.sub(' ',wholeFile)
        confirmationNumber = re.search('Your confirmation number is: \d+',wholeFile)

        if confirmationNumber != None:
            confirmationNumber = int(confirmationNumber.group()[30:])
        else:
            print('error while processing '+comment_string)
            sys.exit(1)

        writeFtp(confirmationNumber,user,args.output_dir)

        driver.close()

def _historical_tracks_attributes(args):
    """
    Dumps attributes for historical tracks file from ibtracs
    """
    ncf=netCDF4.Dataset(args.input_file,'r')
    varNames=ncf.variables.keys() 
    dimNames=ncf.dimensions.keys()
    varNames=list(set(varNames)-set(dimNames))
    print()
    print(args.input_file)
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
    ncf=netCDF4.Dataset(args.input_file,'r')
    lat = numpy.mean(ncf.variables['source_lat'][:],2)
    lon = numpy.mean(ncf.variables['source_lon'][:],2)
    wind = numpy.mean(ncf.variables['source_wind'][:],2)
    time = ncf.variables['source_time'][:]
    basin = ncf.variables['basin'][:]
    mindate = datetime.datetime.strptime(args.mindate,'%Y-%m-%d')
    maxdate = datetime.datetime.strptime(args.maxdate,'%Y-%m-%d')
    maxWind = args.minMaxWind

    cycloneDates=dict()
    sampledDates=dict()
    
    for istorm in range(time.shape[0]):
        stormDate = getDate(time[istorm,0])
        stormBasin = basins[basin[istorm,0]]
        if stormDate >= mindate and stormDate <= maxdate and stormBasin == args.basin:
            #print(stormDate,stormBasin)
            istormWind = wind[istorm,:]
            istormMaxWind=max(istormWind[~istormWind.mask])
            if istormMaxWind < args.minMaxWind:
                continue

            idxMaxWind=random.choice(numpy.where(istormWind == istormMaxWind)[0])
            nIdxs=len(istormWind)
            lowerIdx=max(0,idxMaxWind-args.nDeltaPtsCyclone)
            upperIdx=min(nIdxs,idxMaxWind+args.nDeltaPtsCyclone)
            selectedIdxs=[idxMaxWind]
            for i in range(args.nPtsCyclone):
                randI = random.randint(lowerIdx,upperIdx)
                if randI not in selectedIdxs:
                    selectedIdxs.append(randI)

            for itime in range(len(time[istorm,:])):
                old_wind = 0
                if time[istorm,itime]:
                    idate=getDate(time[istorm,itime])
                    if idate in cycloneDates:
                        cycloneDates[idate]+=1
                    else:
                        cycloneDates[idate]=1
                    if itime in selectedIdxs:
                        if idate in sampledDates:
                            sampledDates[idate]+=1
                        else:
                            sampledDates[idate]=1
                    if wind[istorm,itime]:
                        old_wind = wind[istorm,itime]
                    if args.plot:
                        marker_color = str(max(0.,1. - old_wind/maxWind))
                        if itime in selectedIdxs:
                            marker_color = 'red'
                        plt.plot(lon[istorm,itime],lat[istorm,itime],'.',color=marker_color)

    ncf.close()
    if args.plot:
        figFormat='png'
        filename='_'.join(['wind',args.basin,args.mindate,args.maxdate])+'.'+figFormat
        plt.title(filename+'\nMin Max Wind [kt]: '+str(maxWind))
        plt.savefig(filename,format=figFormat,dpi=300)
        print('Made file: '+filename)

    return cycloneDates,sampledDates

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
    parser.add_argument('-a',action='store_true',required=False,help="Input data file attributes dump")
    parser.add_argument('-f',required=False,help="Parameters input file")
    parser.add_argument('-plot',action='store_true',required=False)
    args = parser.parse_args(args)
    args.f = 'input.cfg' if not args.f else args.f
    args.f=os.path.abspath(args.f)

    config = ConfigParser.ConfigParser()
    config.readfp(open(args.f))
    args.user = config.get('noaa','user')
    args.pwd = config.get('noaa','pwd')
    args.input_file = config.get('IO','input_file')
    args.output_dir = config.get('IO','output_dir')
    args.plot = args.plot or config.getboolean('IO','plot')
    args.basin = config.get('tracks','basin')
    args.mindate = config.get('tracks','mindate')
    args.maxdate = config.get('tracks','maxdate')
    args.minMaxWind = config.getfloat('tracks','minMaxWind')
    args.nPtsCyclone = config.getint('tracks','nPtsCyclone')
    args.nDeltaPtsCyclone = config.getint('tracks','nDeltaPtsCyclone')
    args.hourTimeWindow = config.getint('tracks','hourTimeWindow')
    args.seed= config.getint('system','seed')
    return args

def downloadIr():
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    args = parse_args(sys.argv[1:])

    random.seed(args.seed)

    cycloneDates,sampledCycloneDates = _historical_tracks(args)
    sampledDates=[]
    for i in sorted(sampledCycloneDates.keys()):
        sampledDates.append(i)

    _downloadIr(args,sampledDates)

def run():

    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    args = parse_args(sys.argv[1:])

    random.seed(args.seed)

    if args.a:
        _historical_tracks_attributes(args)
    else:

        cycloneDates,sampledCycloneDates = _historical_tracks(args)
        dates=[]
        counts=[]
        for i,iv in sorted(cycloneDates.items()):
            dates.append(i)
            counts.append(iv)

        if args.plot:
            fig=plt.figure()
            ax=fig.add_subplot(111)
            ax.plot(dates,counts,'o',color='blue')
            ax.grid(True)
            ax.set_ylim([0,5])
            fig.autofmt_xdate()
            locs,labels = plt.xticks()
            plt.setp(labels,rotation=30)
            #axes = plt.gca()
            #axes.autofmt_xdate()
            figFormat='png'
            filename='_'.join(['counts',args.basin,args.mindate,args.maxdate])+'.'+figFormat
            plt.title(filename+' - Counts')
            plt.savefig(filename,format=figFormat,dpi=300)
            print('Made file: '+filename)

    _logger.info("run ends")

if __name__ == "__main__":
    run()
