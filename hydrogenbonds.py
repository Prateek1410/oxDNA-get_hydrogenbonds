#!/usr/bin/python3
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sys
import argparse

'''This script reads the baby output bonds file and 1) gives a text file with the time steps column added and 
   2) another text file giving the HB bonds count for each time step i.e. configuration '''

parser = argparse.ArgumentParser(description='Adds the time steps column and returns the HB bonds count for each configuration.')
parser.add_argument('-f', '--file', metavar = 'file',  nargs='+',  action='append', help = 'Output bonds file to do analysis in')
args = parser.parse_args()

infile = vars(args).get('file')[0][0] 


#extracting the value of total steps and print configuration interval from input file
with open('input.txt', 'r') as inputfile:
        for line in inputfile.readlines():
            if line.startswith('steps ='):
                steps = int(float(line[7:].strip()))
            if line.startswith('print_conf_interval ='):
                pci = int(line[21:].strip())
          

ob_full = pd.read_csv(infile, sep = ' ', header = 0, dtype = {'#id1':'str', 'id2': 'str', 'HB': 'float'}) #import your baby output bonds; 
#mentioning dtypes is crucial to save memory else segmentation error pops up


frameindex = ob_full.index[ob_full['#id1'] == '#id1'].tolist() #stores the indexes of all the lines that contain
#the time information into a list. This will come into use further down to divide the list of indices of HB bonds as per the frames

df = ob_full[~ob_full['#id1'].astype(str).str.startswith('#')] #removing repeated header rows beginning with #
#I can do this cause I've already noted the indices of the rows containing the time information.

df = df[df['HB'] <= -0.1] #This will return a new dataframe containing only those entries having HB <=  -0.1.

indices = list(df.index.values) #storing the indexes of the filtered dataframe into a list

time = np.split(indices,np.searchsorted(indices, frameindex)) #splitting list into smaller arrays based on the 
#values given in the frameindex list
#This is because we want to know when a particular frame ends and the next one begins in the dataframe
#since each frame has multiple entries.

#print(len(time[0])) #time[0] will access the first sub-array of time corresponding to the first frame
# and thus, we can check the number of entries of the first frame

d = {f'Steps'+str(i+1) : [pci*(i+1) for x in range(len(time[i]))] for i in range(len(time))} 
#This creates a dictionary having key:value pairs of Stepsnumber:list of step number repeated as many times as there are entries of that step/frame
# in the time array. From this dictionary, we extract the sequence of steps for eventual addition to the dataframe

stepslist = list(d.values()) #returns of list of lists of values from the dictionary
mergestepslist = [] #running a loop to merge all the sublists of stepslist into one single list
for i in stepslist:
  mergestepslist += i

Stepsarray = np.array(mergestepslist) #converting the stepslist into array

df['Steps'] = Stepsarray #adding this array of steps into the filtered dataframe

bondsdict = {}
for i in range(pci, steps+1, pci): #ranging from first conf, over increments of pci and till steps+1 because otherwise last step/conf is not included.
  bondsdict[f'{i}'] = str(df.loc[df['Steps'] == i, 'Steps'].count()) #this creates a dict of frame:bond count pairs

df2 = pd.DataFrame(bondsdict.items()) #using this dict for building another df and later saving it to txt file
df2.columns = ['Frame', 'Bonds Count'] #renaming the columns 


#saving the dataframes to a csv as opposed to a fixed width text file since the latter was requiring longer computation (lappy fan activity
#increased)

df.to_csv('HB_bonds_all.txt', index = False) 
df2.to_csv('HB_bonds_count.txt', index = False) #index =False cause otherwise it was including a column of indices in my text file as well. 