# -*- coding: utf-8 -*-
""" A collection of functions for importing MATLAB files from the Thiele lab.
For example the public dataset available at: https://gin.g-node.org/jochemvankempen/Thiele-attention-gratc-V1-V4-laminar
"""

import numpy
import os
import pandas
import scipy.io
import requests
import validators
import sys

def load_data(loadfilename, *variables2load):
    """
    Load Matlab data from Thiele lab.
    
    Args:
      loadfilename (str)    : String of file to load
      *variables2load (str) : Strings that indicate which variables to load from loadfilename, if not passed all variables are loaded
  
    Returns:
      (dict)                : Dictionary with the converted matlab variables
    """
    
    # check whether variable names to load were passed, if not: load all variables
    if variables2load:
        variable_names = variables2load
    else:
        variable_names = None
    
    # import data
    matdata = import_data(loadfilename, variable_names)
    
    # check what type of data 
    path, filename = os.path.split(loadfilename)
    filetype, ext = os.path.splitext(filename)
    
    # define whether certain filetypes contain analog data
    is_analog_file = {
        'LFP': True,
        'LFPb': True,
        'MUAe': True,
        'NCS': True,
        'CSC': True,
        'hash': False,
        'unit': False,
        'microsaccades': False 
        }
    
    
    # loop over keys and store in dict
    # --------------------------------
    pydata = {}
    for key in matdata:
        

        if 'Align' in key:
            # fields named '...Align' are data aligned to events
            
            # perform different operation depending on whether filetype is analog
            if is_analog_file[filetype]:
                
                pydata.update({key: {}}) # add key-value pair that is nested dict for timeseries data
            
                # convert numpyarray to nested dict
                pydata[key]['TimeStamps'] = matdata[key]['TimeStamps'][0,0]
                pydata[key]['Samples'] = matdata[key]['Samples'][0,0]
            
                # # convert np array to pandas series
                # pydata.update({key: pandas.DataFrame(matdata[key]['Samples'][0,0], index=matdata[key]['TimeStamps'][0,0]) })
            else:
                
                pydata.update({key: matdata[key]}) 
             
                
        elif (key=="area"):
            pydata.update({key: matdata[key]}) 
            
        elif (key=='unitList'):
            pydata.update({key: matdata[key]-1}) # update channel/unit indices, starting at index==0
            
        else:
            try:
                pydata.update({key: matdata[key]}) 
                
            except:
                print('Cannot process ' + key)
        
    
    # return dict
    return pydata


def load_trialdata(loadfilename):
    """
    Load Matlab trialdata from Thiele lab.
    
    Args:
      loadfilename (str)    : String of file to load
      *variables2load (str) : Strings that indicate which variables to load from loadfilename, if not passed all variables are loaded
  
    Returns:
      (dict)                : Dictionary with the converted matlab variables
    """
    
    # perform checks on inumpyut
    # -----------------------
    
    # check whether file exists
    assert (os.path.exists(loadfilename) == True),"File does not exist: " + loadfilename
    
    
    # load matlab file
    # ----------------
    matdata = import_data(loadfilename, variable_names=None)
    matdata = matdata['trialdata'][0]
    
    num_trial = len(matdata)
    
    CTX_events = [[] for i in range(num_trial)] # init list of lists
    NLX_events = [[] for i in range(num_trial)]
    
    cond = numpy.zeros(num_trial, dtype=int)
    trial_ID = numpy.zeros(num_trial, dtype=int)
    RT_evnt = numpy.zeros(num_trial, dtype=int)
    RT_EPP = numpy.zeros(num_trial, dtype=int)
    target_dim = numpy.zeros(num_trial, dtype=int)
    rf_dim = numpy.zeros(num_trial, dtype=int)
    position_RF = numpy.zeros(num_trial, dtype=int)
    position_out1 = numpy.zeros(num_trial, dtype=int)
    position_out2 = numpy.zeros(num_trial, dtype=int)
    fixbreak = numpy.zeros(num_trial, dtype=int)
    
    for itrial in range(num_trial):
        
        # variable names conform to legacy (e.g. https://gin.g-node.org/jochemvankempen/Thiele-attention-gratc-V1-V4-laminar), 
        # these are changed to conform to python conventions
        
        # matdata[itrial][0]: CTX_events
        # matdata[itrial][1]: NLX_events
        # matdata[itrial][2]: trialID
        # matdata[itrial][3]: cond_num
        # matdata[itrial][4]: RT_evnt
        # matdata[itrial][5]: RT_EPP
        # matdata[itrial][6]: target_dim
        # matdata[itrial][7]: rf_dim
        # matdata[itrial][8]: position_RF
        # matdata[itrial][9]: position_out1
        # matdata[itrial][10]: position_out2
        # trialdata[itrial][11]: fixbreak
        
        CTX_events[itrial] = matdata[itrial][0]
        NLX_events[itrial] = matdata[itrial][1]
        
        trial_ID[itrial]        = matdata[itrial][2][0][0]
        cond[itrial]            = matdata[itrial][3][0][0]
        RT_evnt[itrial]         = matdata[itrial][4][0][0]
        RT_EPP[itrial]          = matdata[itrial][5][0][0]
        target_dim[itrial]      = matdata[itrial][6][0][0]
        rf_dim[itrial]          = matdata[itrial][7][0][0]
        position_RF[itrial]     = matdata[itrial][8][0][0]
        position_out1[itrial]   = matdata[itrial][9][0][0]
        position_out2[itrial]   = matdata[itrial][10][0][0]
        fixbreak[itrial]        = matdata[itrial][11][0][0]
        
        
    # define attention conditions (two frating directions for each stimulus)
    attend = numpy.zeros(num_trial, dtype=int)
    attend[numpy.logical_or(cond==1, cond==4)] = 1 # attend RF
    attend[numpy.logical_or(cond==2, cond==5)] = 2 # attend away1
    attend[numpy.logical_or(cond==3, cond==6)] = 3 # attend away2
    
    trialdata = {
        'trial_ID': trial_ID,
        'attend': attend,
        'cond': cond,
        'RT_evnt': RT_evnt,
        'RT_EPP': RT_EPP,
        'target_dim': target_dim,
        'rf_dim': rf_dim,
        'position_RF': position_RF,
        'position_out1': position_out1,
        'position_out2': position_out2,
        'fixbreak': fixbreak,
        'CTX_events': CTX_events,
        'NLX_events': NLX_events
        }
    
    trialdata = pandas.DataFrame(trialdata)
    
    return trialdata
    
    
    
def check_filename(test_string):
    """
    Test whether string is a valid URL. If not, assume it is a local file and assert it exists
    
    Parameters
    ----------
    test_string : string
        string of URL or local filename

    Returns
    -------
    valid_URL: bool
        boolean indicating whether string is URL

    """
    valid_URL = validators.url(test_string)
    
    if not valid_URL:        
        # check whether file exists
        assert (os.path.exists(test_string) == True),"File does not exist: " + test_string
    
    return valid_URL

def import_data(loadfilename, variable_names):
    """
    import data from URL or load local file

    Parameters
    ----------
    loadfilename : string
        String of file to load
    variable_names : list
        Strings that indicate which variables to load from loadfilename, if not passed all variables are loaded.

    Returns
    -------
    matdata : numpy array
        DESCRIPTION.

    """
    
    # perform checks on input
    # -----------------------    
    filename_is_url = check_filename(loadfilename)
        
    
    # load data
    # --------- 
    if filename_is_url:
        
        matdata = requests.get(loadfilename)
        
        try:
            # load file from url          
            r = requests.get(loadfilename)
            
        except requests.ConnectionError:
            print("!!! Failed to download data !!!")
            
        else:
            
            sys.exit('Loading file from URL not yet implemented!')
            
            if r.status_code != requests.codes.ok:
                print("!!! Failed to download data !!!")
            else:
                with open(loadfilename, "r") as file:
                    matdata = file.read()
                # with open(fname[j], "wb") as fid:
                #     fid.write(r.content)
                    
                print(f'{loadfilename} downloaded')
    else:
        # load local file
        matdata = scipy.io.loadmat(loadfilename, variable_names=variable_names)
  
    return matdata

    
    