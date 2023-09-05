# -*- coding: utf-8 -*-
"""
Created on Tue Sep  5 16:47:44 2023

@author: decabooter
"""

import numpy as np
import pandas as pd
import DistributionTools as dt

#Risk Premiums
lowRisk = 0.20
midRisk = 0.50
highRisk = 1.00

'''
Reading in the source file
This file has the following columns:
    ID = unique task identifier
    Module = which version of the release the work is related to
    Feature Set = which workflows the task applies to
    Task (Summary) = name of activity
    Details = detailed description of the activity
    Risk = Low/Medium/High perceived risk by the team
    Estimates = maximum estimates for the task
    Release = release cadence--Rel1 is before Rel2; '-' values = out of scope
    Adjusted Estimate= estimates, removing the out-of-scope tasks
    Whoe = who will do the work (not currently filled out)
    Date Started = start date (not currently filled out)
    Date Completed = finish date for tasks (not currently filled out)
    % Complete = how far along the task is (not currently filled out)
'''
taskList = pd.read_csv('lists/projectlist.csv',
                 usecols = ['ID', 'Module', 'Feature Set', 'Risk', 
                            'Adjusted Estimate'])

#Note:  the " -   " string is what Excel put into the CSV cell to 
#   represent zero/blank in the source spreadsheet
taskList = taskList.drop(taskList[taskList['Adjusted Estimate'] == ' -   '].index)
#This file's estimates are all risk-adjusted maximum estimates.  
#Rename column with max'es and add in the mins.
#NOTE:  the source spreadsheet used a 0% risk premium for low risks.  
#   We will use 20%.  This means that we need to increase the low risk task
#   max estimates by the risk factor.
taskList.rename(columns={'Adjusted Estimate': 'Maximum'}, inplace = True)
taskList[["Maximum"]] = taskList[["Maximum"]].apply(pd.to_numeric)
taskList.reset_index(inplace = True, drop=True)
minimums = []
for i in range(len(taskList)):
    if taskList.loc[i,'Risk'] == 'Low':
        minimums.append(taskList.loc[i,'Maximum'])
        taskList.loc[i,'Maximum'] *= (1+lowRisk)
    elif taskList.loc[i,'Risk'] == 'Medium':
        minimums.append(taskList.loc[i,'Maximum']/(1+midRisk))
    else:
        minimums.append(taskList.loc[i,'Maximum']/(1+highRisk))
taskList['Minimum'] = minimums

###got raw data loaded in--now need to build the MC

print(taskList.to_string())