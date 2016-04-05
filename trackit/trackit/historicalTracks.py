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
from selenium import webdriver
import inspect
import re

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

    baseUrl = 'https://www.nsof.class.noaa.gov/saa/products'

    print('https://www.browserstack.com/automate/python')
    sys.exit(0)
    driver = webdriver.Firefox() 
    driver.get(baseUrl+'/classlogin')
    username = driver.find_element_by_name("j_username")
    password = driver.find_element_by_name("j_password")
    username.send_keys(user)
    password.send_keys(pwd)
    login_button = driver.find_element_by_xpath("//input[@class='Button'][@value='Login'][@type='submit']")
    login_button.click()
    driver.implicitly_wait(3)
    driver.get(baseUrl+'/user_profile')
    driver.get(baseUrl+'/upload')
    sys.exit(0)
    upload_file = driver.find_element_by_xpath("//input[@name='uploaded_file'][@type='file']")
    upload_button = driver.find_element_by_xpath("//input[@type='submit'][@class='Button'][@value='Upload File']")
    upload_file.send_keys(xmlfile)
    upload_button.click()
    search_button = driver.find_element_by_xpath("//input[@class='Button'][@value='Search']")
    search_button.click()
    select_datasets = driver.find_element_by_xpath("//select[@name='AddGroup']/option[2]")
    select_datasets.click()
    goto_cart = driver.find_element_by_xpath("//input[@value='Goto Cart'][@class='Button']")
    goto_cart.click()

    formats = driver.find_elements_by_xpath("//select/option[@value='NetCDF']")
    for i in formats:
        i.click()



    sys.exit(0)

    response = br.submit()
    sys.exit(0)


    # MECHANIZE ATTEMPT

    logger = logging.getLogger("mechanize")
    logger.addHandler(logging.StreamHandler(sys.stdout))
    logger.setLevel(logging.INFO)
    rf=open('response.html','w')
    print('Instantiating browser')
    br = mechanize.Browser()
    br.set_debug_http(False)
    br.set_debug_responses(False)
    br.set_debug_redirects(False)

    br.addheaders = [('User-agent','Firefox')]
    br.set_handle_robots(False)
    baseUrl = 'https://www.nsof.class.noaa.gov/saa/products'
    print('NOAA login page')
    classloginUrl= baseUrl+'/classlogin'
    response = br.open(classloginUrl)

    print('Selecting login form and passing username and password')
    br.select_form(name='frmLogin')
    br['j_username'] = user
    br['j_password'] = pwd
    print("FORM ACTION: "+br.form.action)
    response = br.submit()

    uploadUrl = baseUrl+'/upload'
    response = br.open(uploadUrl)
    rf.write(response.read())
    #clsmembers = inspect.getmembers(sys.modules['mechanize'],inspect.isclass)

    print('Opening file upload url and submitting file: '+xmlfile)
    uploadUrl = baseUrl+'/upload'
    response = br.open(uploadUrl)
    form = br.select_form(name='f1')
    br.form.add_file(open(xmlfile),'text/plain',xmlfile)
    response = br.submit()

    print('Selecting search form and submitting: '+xmlfile)
    form = br.select_form(name='search_frm')
    response = br.submit()

    print('Selecting refine form')
    form = br.select_form(name='rform')
    print('Emulating jscript for selecting all check boxes')
    attrs = {}
    control = mechanize._form.HiddenControl('hidden','group_index',attrs)
    control._value = 0
    control.add_to_form(br.form)
    control = mechanize._form.HiddenControl('hidden','update_action',attrs)
    control._value = 'AddGroup'
    control.add_to_form(br.form)
    response = br.submit()

    print('Re-Selecting refine form')
    print('Emulating jscript for going to cart')
    form = br.select_form(name='rform')
    attrs = {}
    control = mechanize._form.HiddenControl('hidden','update_action',attrs)
    control._value = 'Goto Cart'
    control.add_to_form(br.form)
    oldAction = br.form.action
    br.form.action = baseUrl+'/shopping_cart_upd'
    response = br.submit()

    print('Selecting shop form')
    form = br.select_form(name='shop')
    print('Changing format to netcdf for all datasets')
    for control in br.form.controls:
        if type(control.name)==str and re.search('^format_[0-9]+_GVAR_IMG$',control.name):
            control.value=['NetCDF']
        elif type(control.name)==str and control.name=='encryption':
            control.readonly = False
            control.value = 'Y'

    br['email']='drosawork@drosa.name'
    
    response = br.submit()
    rf.write(response.read())

    #for form in br.forms():
    #    print(form)
    #    print(form.action)

    sys.exit(0)
    response = br.submit()

    print(xmlfile)

    br.select_form(name='rform')
    for i in range(len(br.find_control('cart').items)):
        br.find_control('cart').items[i].selected=True

    gotoCart = mechanize._form.SubmitControl('hidden','update_action','Goto Cart')
    br.add_to_form(gotoCart)

    print(br.form)
    response = br.submit()
    rf.write(response.read())
    sys.exit(0)
    # /media/drosa/1T/Data/Cyclones/test.xml

    br.select_form(name='rform')
    print(br.form)
    sys.exit(0)

    response = br.submit()
    rf.write(response.read())
    print('----------------------')
    sys.exit(0)

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
