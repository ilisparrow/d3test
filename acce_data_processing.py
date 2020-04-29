import pandas as pd
import numpy as np
import datetime
import math
from datetime import timedelta  
import os 
#'''
#For developpement :
import time
import matplotlib.pyplot as plt
#'''

def loadFile(_name) : #Returns a [bool : If it loaded the file, data : np array of the data, timestamp : array of when the measures where taken, it has the same size as data]
    try :   
        csvFile = pd.read_csv(_name) 
        print("succesfully loaded the file")
        timeStamp =pd.to_datetime(csvFile['created'])#TO CHECK : The current csv file has this category to store the time of the log
        npAccZ = np.array(csvFile['accZ'])#TO CHECK : The current csv file has this category to store the accel dat
        plt.plot(npAccZ)
        plt.show()
        return True,npAccZ,timeStamp
    except:
        print("Failed to load the input file")
        return False,0,0
    
def movingAverage(_a, _n=300) :
    ret = np.cumsum(_a, dtype=float)
    ret[_n:] = ret[_n:] - ret[:-_n]
    return ret[_n - 1:] / _n    
    
def sglProcessing(_sgl,_smoothingWindow=300):

    npAccCentered = _sgl-np.mean(_sgl)#Centers the data around 0
    plt.plot(npAccCentered)
    plt.show()
    
    npAccZqrd = np.square(npAccCentered)#it's the equivalent of the absolut value (to make all of the data positiv

    
    npAccZFiltered = movingAverage(npAccZqrd,_smoothingWindow)#Low pass filter (averaging over a 300 elment window)
    plt.plot(npAccZFiltered)
    plt.show()
    return npAccZFiltered    


def writToFile(_isOn, _newStampTime,_localSum):#Writes into a CSV file in the same folder as the script
    try:

        df = pd.DataFrame(data=_newStampTime, columns=["date"])
        df['value'] = _isOn
        df['localSum'] = _localSum
        dir_path = os.path.dirname(os.path.realpath(__file__))
        dir_path = os.path.join(dir_path, "export_dataframe.csv") 
        df.to_csv (dir_path, index = False, header=True)
        print(df.tail())
        print("File saved")
    except:
        print("Failed to save the CSV file")

#############################################################################
#                                                                           #
#                   Main code starts here                                   #
#                                                                           #
#############################################################################

#startTime = time.time()
smoothingWindow = 30#TO CHECK : THe value 300 was chosen for 30 000 values, to check for less values
threshHold = 200#TO CHECK : THe value 300 was chosen for a smoothening window of 300 values, to check for less values
loaded,data,timeStamp = loadFile('28042020.csv')

if  loaded :#Checks if the file was loaded correctly
    processed = sglProcessing(data, smoothingWindow)#Calls the processing function
    resizedTimeStamp = timeStamp[smoothingWindow-1:]#Calculates the size of the array after the filter is applied
    boolArray = (processed>threshHold)*1#Applies the threshold, and transforms it into 1 & 0
        

    lengthInMinutes = ((timeStamp[len(timeStamp)-1]-timeStamp[0]).total_seconds()//60)#Calculates the interval in minutes

    totalTime = np.zeros(int(lengthInMinutes))#Init of the array that will store the the 0s and 1 and will be summed up
    localSum = np.zeros(int(lengthInMinutes))#Init of the array that will store the the 0s and 1 and will be summed up
    newStampTime = []#Init. of the new time timestamp array, that has a one minute interval between measure (extrapolated)



    for i in range(int(lengthInMinutes)):
        totalTime[i] = boolArray[math.floor(len(boolArray)*(i/lengthInMinutes))]#Extrapolates if it's a one or a zero .
        newStampTime.append((timeStamp[0]+ timedelta(seconds=60)*i))#generates the new time stamps
        try:
            localSum[i]=totalTime[i]+localSum[i-1] 
        except:
            pass

    writToFile(totalTime,newStampTime,localSum)#Calls the write to a file function
    plt.plot(totalTime)
    plt.show()
    print(str(sum(totalTime)//60)+"h")
    #print(startTime -time.time())
    


    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    