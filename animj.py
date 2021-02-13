#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec  3 16:40:22 2020

Collection of functions used for plotting animations using the matplotlib.animation module.

This code is based on the following websites/tutorials:
    - https://pythonmatplotlibtips.blogspot.com/2017/12/draw-3d-line-animation-using-python-matplotlib-funcanimation.html
    
@author: jochemvankempen
"""

import numpy

def def_lines(ax, plotdata):
    """
    Define line objects for matplotlib animation
    
    Parameters
    ----------
    ax : axis obect
        figure axis to plot lines in
    plotdata : numpy array
        array of size (numlines, numdimensions, numsamples) to plot numlines in numdimensions over numsamples
  
    Returns
    -------
    lines : list
        list with line objects
    """     
    
    # check input
    num_dims = numpy.shape(plotdata)[1] # 'the second dimension of plotdata is the number of dimensions to plot'
    
    # define lines
    if num_dims==2:
        lines = [ax.plot(dat[0, 0:1], dat[1, 0:1])[0] for dat in plotdata] # plot x,y for first samples
        
    elif num_dims==3:
        lines = [ax.plot(dat[0, 0:1], dat[1, 0:1], dat[2, 0:1])[0] for dat in plotdata] # plot x,y,z for first samples
    
    else:
        raise ValueError('def_lines not implemented for numdimensions=%d' % num_dims)
    
    return lines


def update_lines(num, plotdata, lines, numsamples=None):
    """
    Update line objects in matplotlib animation
    
    Parameters
    ----------
    num : int
        iteration of the animation
    plotdata : numpy array
        array of size (numlines, numdimensions, numsamples) to plot numlines in numdimensions over numsamples
    lines : list
        list of line objects acquired by calling _def_lines
    numsamples : int
        the number of samples to show on each iteration. Default is None, plotting plotdata[:,:,:num]
  
    Returns
    -------
    lines : list
        list with updated line objects
    """   
    
    # check input
    num_dims = numpy.shape(plotdata)[1] # 'the second dimension of plotdata is the number of dimensions to plot'
    
    # loop over line objects
    for line, data in zip(lines, plotdata):
        # NOTE: there is no .set_data() for 3 dim data...
        
        if numsamples is None:
            if num_dims==2: 
                line.set_data(data[:, :num])
                
            elif num_dims==3: 
                line.set_data(data[0:2, :num])
                line.set_3d_properties(data[2,:num])            

        else:
            if num_dims==2:                
                line.set_data(data[:, (num-numsamples):num])
                
            elif num_dims==3: 
                line.set_data(data[0:2, (num-numsamples):num])
                line.set_3d_properties(data[2, (num-numsamples):num])

        line.set_marker("o")
        
    return lines


def update_lines_counter(num, plotdata, lines, text_counter, data_counter, numsamples=None):
    """
    Update line and text objects in matplotlib animation. This function is similar to _update_lines but the final object is a text object
    
    Parameters
    ----------
    num : int
        iteration of the animation
    plotdata : numpy array
        array of size (numlines, numdimensions, numsamples) to plot numlines in numdimensions over numsamples
    lines : list
        list of line objects acquired by calling _def_lines, appended with text object
    text_counter : str
        string that is updated as text_counter % data_counter[num], 
    data_counter : array
        The samples iterated over (e.g. time). of same length as plotdata
    numsamples : int
        the number of samples to show on each iteration. Default is None, plotting plotdata[:,:,:num]
  
    Returns
    -------
    lines : list
        list with updated line objects
    """
    
    # check input
    num_dims = numpy.shape(plotdata)[1] # 'the second dimension of plotdata is the number of dimensions to plot'
    
    # loop over line objects
    for line, data in zip(lines, plotdata):
        # NOTE: there is no .set_data() for 3 dim data...
        
        if numsamples is None:

            if num_dims==2: 
                line.set_data(data[:, :num])
                
            elif num_dims==3: 
                line.set_data(data[0:2, :num])
                line.set_3d_properties(data[2,:num])            

        else:
            if num_dims==2:                
                line.set_data(data[:, (num-numsamples):num])
                
            elif num_dims==3: 
                line.set_data(data[0:2, (num-numsamples):num])
                line.set_3d_properties(data[2, (num-numsamples):num])

        line.set_marker("o")

    idx_text = len(lines)-1
    lines[idx_text].set_text(text_counter % data_counter[num])
    
    return lines




