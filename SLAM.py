#   SLAM : a method for the automatic Stylization and LAbelling of speech Melody
#   Copyright (C) 2014  Julie BELIAO
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.


# -*- coding: utf-8 -*-
""""
#####################################################################
Automatic Stylizer.
#####################################################################

Takes a wavefile and a textgrid file as an input and compute the
styles of all the intervals of a desired tier with the SLAM algorithm.

PARAMETERS:

I/O:
---
* wavFile            : path to the wave file to process
* inputTextgridFile  : path to the input TextGrid file 
* outputTextgridFile : path to the output TextGrid file

tiers of interest:
------------------
* speakerTier : average register of each speaker is computed 
                using this tier. For each different label in
                this tier, we assume a different speaker, for
                whom the average register is computed.
* targetTier  : The tier whose intervals will be stylized using
                SLAM

display:
-------
* displayExamples : True or False: whether or not to display examples 
                   of stylized f0 segments
* displaySummary : True or False: whether or not to display a small
                   summary of the distribution of the stylizes 
#####################################################################"""


essai

timeStep = .001 #in seconds, step for swipe pitch analysis
voicedThreshold = 0.2 #for swipe

#Tiers for the speaker and the target intervals, put your own tier names
speakerTier= 'locuteur' 
targetTier = 'packageType'

#display
examplesDisplayCount = 5 #number of example plots to do. Possibly 0
minLengthDisplay = 30 #min number of f0 points for an interval to be displayed


#END OF PARAMETERS (don't touch below please)
#------------------------------------------------------

#imports
from SLAMpy import TextGrid, swipe, stylize
import sys, glob, os
import numpy as np


change = raw_input("""
Current parameters are:
  tier to use for categorizing registers : %s
  tier to stylize                        : %s
  Number of examples to display          : %d

  ENTER = ok
  anything+ENTER = change
  
  """%(speakerTier, targetTier,examplesDisplayCount))
  
print change
if len(change):
    new = raw_input('reference tier (empty = keep %s) : '%speakerTier)
    if len(new):speakerTier=new
    new = raw_input('target tier (empty = keep %s) : '%targetTier)
    if len(new):targetTier=new
    new = raw_input('number of displays (empty = keep %d) : '%examplesDisplayCount)
    if len(new):examplesDisplayCount=int(new)
    
  


#all styles, for statistics
styles = []
totalN=0

wavFiles = glob.glob('./data/*.wav')
    
for ifile, wavFile in enumerate(wavFiles):
    basename =  os.path.split(wavFile)[1][:-4]

    outputTextgridFile = './output/%s.TextGrid'%basename
    inputTextgridFile =  './data/%s.TextGrid'%basename
     
    #Create TextGrid object
    print ''
    print 'Handling %s....'%basename
    print 'Loading input TextGrid...'
    tg = TextGrid.TextGrid()
    tg.read(inputTextgridFile)
    tierNames = [t.name() for t in tg]
    
    while targetTier not in tierNames:
        print '    TextGrid does not have a tier named %s. Available tiers are:'%targetTier
        for t in tierNames: print '        %s'%t
        targetTier=raw_input('Type the tier name to use (+ENTER):')
    while speakerTier not in tierNames:
        print '    TextGrid does not have a tier named %s. Available tiers are:'%targetTier
        for t in tierNames: print '        %s'%t
        speakerTier=raw_input('Type the tier name indicating speaker (or any categorizing variable):')
        
    
    #create interval tier for output
    newTier = TextGrid.IntervalTier(name = '%sStyle'%targetTier, 
                           xmin = tg[targetTier].xmin(), xmax=tg[targetTier].xmax())    
            
    #Create swipe file
    print 'Computing pitch on wave file'
    sf = swipe.Swipe(wavFile, pMin=75, pMax=500, s=timeStep, t=voicedThreshold, mel=False)
    
    print 'Computing average register for each speaker' 
    registers = stylize.averageRegisters(sf, tg[speakerTier])
    
        
    	
    print 'Stylizing each interval of the target tier'
    
    #computing at which iterations to give progress  
    LEN = float(len(tg[targetTier]))
    totalN+=LEN
    POSdisplay = set([int(float(i)/100.0*LEN) for i in range(0,100,10)])

    for pos,interval in enumerate(tg[targetTier]):
        if pos in POSdisplay:
            print 'stylizing: %d percents'%(pos/LEN*100.0)
            
        #compute style of current interval
        (style,original, smooth)=stylize.stylizeObject(interval,sf,tg[speakerTier],registers)
        
        #if style computed, adding it to global list
        if len(style) and (style!='_') :styles+=[style]
        
        #then add an interval with that style to the (new) style tier
        newInterval = TextGrid.Interval(interval.xmin(), interval.xmax(), style)
        newTier.append(newInterval)    
        
        #display if interval is sufficiently large
        if (examplesDisplayCount>0) and len(style) and len(original)>=minLengthDisplay:
            import pylab as pl
            pl.figure(1)
            pl.clf()
            pl.plot(np.linspace(0,1,len(original)),original,'b')
            pl.hold(True)
            pl.plot(np.linspace(0,1,len(smooth)),smooth,'r')
            pl.title(style)
            pl.grid(True)
            pl.show()
            examplesDisplayCount-=1
    
    #done, now writing tier into textgrid and saving textgrid
    print 'Saving computed styles in file %s'%outputTextgridFile
    tg.append(newTier)
    tg.write(outputTextgridFile)


#Now output statistics
#---------------------
count = {}
for unique_style in set(styles):
    if not len(unique_style):continue
    count[unique_style] = styles.count(unique_style)


#valeurs triees par importance decroissante
unsorted_values = np.array(count.values())
nbStylesRaw = len(unsorted_values)
total = float(sum(unsorted_values))

#remove styles that appear less than 0.5 percents of the time
for style in count.keys():
    if count[style]/total < 0.005: del count[style]

unsorted_values = np.array(count.values())
stylesNames = count.keys()
argsort = np.argsort(unsorted_values)[::-1] # from most to less important
sorted_values = unsorted_values[argsort]

total = float(sum(unsorted_values))
L = min(len(count.keys()),20)
print """
------------------------------------------------------------------
SLAM analysis overall summary:
------------------------------------------------------------------
- %d intervals to stylize.
- %d intervals with a non empty style (others are unvoiced)
- %d resulting styles appearing in total
- %d resulting nonnegligible styles (appearing more than 0.5%% of the time)
------------------------------------------------------------------
- The %d most important nonnegligible styles along with their frequency are:"""%(
totalN,                                                                                 
len(styles),
len(set(styles)),
len(count),
L)
styleNames=sorted(count,key=count.get)
styleNames.reverse()
for styleName in styleNames[:L]:
    print '\t%s\t:\t:%0.1f%% (%d occurrences)'%(styleName,count[styleName]/total*100.0,count[styleName])
print '''

x------------------------------------------x---------------------x
| explained proportion of the observations | number of styles    |
|         (percents)                       |                     |
x------------------------------------------x---------------------x'''

cumulative_values = np.cumsum(sorted_values)
cumulative_values = cumulative_values/float(cumulative_values[-1])

for P in [70, 75, 80, 85, 90, 95, 99]:
    N = np.nonzero(cumulative_values>float(P)/100.0)[0][0]+1
    print '|                %d                        |         %d          |'%(P,N)
print 'x------------------------------------------x---------------------x'
    
