# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/API/locoDataMunger.ipynb.

# %% auto 0
__all__ = ['extractDateStr', 'readMetaAndCount', 'calculateSpeedinCountLog', 'calculatePeriFeedLoco', 'fallEvents',
           'labelStretches', 'correctInPortData', 'intrapolateUnderThreshold', 'assignStatus']

# %% ../nbs/API/locoDataMunger.ipynb 3
"""
Created on Thu Oct  7 12:45:55 2021

@author: xusy
"""

# 25/08/2021 added gaussian smoothing function for x and y. can input gaussian window size and std
# 26/08/2021 fixed printout of metadata currently processed in readMetaAndCount
# 26/01/2021 added fall events
# 23/01/2023 added stacked plots

import numpy as np
import pandas as pd
import os
from . import locoUtilities
import datetime
import re

# %% ../nbs/API/locoDataMunger.ipynb 4
def extractDateStr(s):
    dateString = re.search(r'\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}', s).group()
    dateTime = datetime.datetime.strptime(dateString, '%Y-%m-%d_%H-%M-%S')
    return dateString, dateTime


# %% ../nbs/API/locoDataMunger.ipynb 5
def readMetaAndCount(dataFolder, companionEspObj,  startMin, endMin, initialResamplePeriod, smoothing, longForm=False):
    """

    Reads the MetaDatas, CountLogs, FeedLogs, PortLocations from the path provided 

    Parameters
    ----------

    dataFolder : str
        path to folder that contains all the relevant data files.
    companionEspObj : data object 
        calculated from espresso package.
    startMin : int, 
        the starting minute for the period to be included in the analysis.
    endMin : int
        the ending minute for the period to be included in the analysis.
    initialResamplePeriod : int
        period for resampling functions in milliseconds, default 50. 
    smoothing : boolean
        parameter for whether or not to smooth the data.
    longForm : boolean
        parameter to indicate whether or not the multiple data files were from one longitudinal experiment. 
   
   Returns
    -------
    `bigMetaDataDf` : pandas dataframe 
        contains all the metaData tables.
    `bigCountLogDf` : pandas dataframe 
        contains all the countLog tables.
    `bigPortLocationsDf` : pandas dataframe 
        contains all the portLocation tables.
    `experimentSummary`:  pandas dataframe 
        contains information on each experiment. 

    """
    
    filelist = os.listdir(dataFolder)
    countLogList = [s for s in filelist if s.startswith('CountLog')]
    if countLogList:
        countLogList = np.sort(countLogList)
        print('countLog files found: \n')
        print(countLogList)
    else:
        print('Warning: no countLog files')
        exit()
    metaDataList = [s for s in filelist if s.startswith('MetaData')]
    if metaDataList:
        metaDataList = np.sort(metaDataList)
        print('\nmetaData files found: \n')
        print(metaDataList)
    else:
        print('Warning: no metaData files')
        exit()
    portLocationsList = [s for s in filelist if s.startswith('PortLocations')]
    if portLocationsList:
        portLocationsList = np.sort(portLocationsList)
        print('portLocations files found: \n')
        print(portLocationsList)
    else:
        print('Warning: no portlocations files')
        exit()

    feedLogList = [s for s in filelist if s.startswith('FeedLog')]
    if feedLogList:
        feedLogList = np.sort(feedLogList)
        print('\nfeedLog files found: \n')
        print(feedLogList)
    else:
        if companionEspObj:
            feedLogList = np.unique([extractDateStr(i)[0]
                                    for i in companionEspObj.flies.ChamberID])
            print(feedLogList)

        else:
            print('Warning: no feedlog files')

    experimentSummary = []
    for i in range(len(countLogList)):
        companionMetaData = metaDataList[np.argmin([np.abs(extractDateStr(
            m)[1] - extractDateStr(countLogList[i])[1]) for m in metaDataList])]
        companionPortLocations = portLocationsList[np.argmin([np.abs(extractDateStr(
            m)[1] - extractDateStr(countLogList[i])[1]) for m in portLocationsList])]
        companionFeedLog = [m for m in feedLogList if np.abs(extractDateStr(
            m)[1] - extractDateStr(countLogList[i])[1]).total_seconds() < 15]
        if companionFeedLog:
            companionFeedLog = companionFeedLog[0]
            companionFeedLogDate = extractDateStr(companionFeedLog)[0]
        else:
            companionFeedLog = 'N/A'
            companionFeedLogDate = 'N/A'
        experimentSummary.append({'countLogFile': countLogList[i],
                                  'countLogDate': extractDateStr(countLogList[i])[0],
                                  'metaDataFile': companionMetaData,
                                  'metaDataDate': extractDateStr(companionMetaData)[0],
                                  'portLocationsFile': companionPortLocations,                                  
                                  'countLogDate': extractDateStr(countLogList[i])[0],
                                  'portLocationsDate': extractDateStr(companionPortLocations)[0],
                                  'feedLogFile': companionFeedLog,
                                  'feedLogDate': companionFeedLogDate
                                  })

    experimentSummary = pd.DataFrame(experimentSummary)

# definition:
#   LeftPortX = the centerline  of the left capillary
#   LeftPortY = the bottom of the left feed port
#   etc

    bigPortLocationsDf = pd.DataFrame()
    for dataSetNumber in range(0, len(portLocationsList)):
        portLocationsDf = pd.read_csv(
            dataFolder + portLocationsList[dataSetNumber])
        portLocationsDf['Date'] = portLocationsList[dataSetNumber][14:33]
        portLocationsDf['DateChamberID'] = portLocationsDf['Date'] + \
            '_Chamber' + (portLocationsDf.index+1).astype(str)
        xconv = portLocationsDf.XmmPerPix[0]
        yconv = portLocationsDf.YmmPerPix[0]
        portLocationsDf['ChamberTopConv'] = (
            portLocationsDf.ChamberBottom - portLocationsDf.ChamberTop) * yconv
        portLocationsDf['ChamberBottomConv'] = (
            portLocationsDf.ChamberBottom - portLocationsDf.ChamberBottom) * yconv
        portLocationsDf['ChamberLeftConv'] = (
            portLocationsDf.ChamberLeft - portLocationsDf.ChamberLeft) * xconv
        portLocationsDf['ChamberRightConv'] = (
            portLocationsDf.ChamberRight - portLocationsDf.ChamberLeft) * xconv
        portLocationsDf['PortsMidpointXConv'] = (
            portLocationsDf.PortsMidpointX - portLocationsDf.ChamberLeft) * xconv
        portLocationsDf['LeftPortXConv'] = (
            portLocationsDf.LeftPortX - portLocationsDf.ChamberLeft) * xconv
        portLocationsDf['LeftPortYConv'] = (
            portLocationsDf.ChamberBottom - portLocationsDf.LeftPortY) * yconv
        portLocationsDf['RightPortXConv'] = (
            portLocationsDf.RightPortX - portLocationsDf.ChamberLeft) * xconv
        portLocationsDf['RightPortYConv'] = (
            portLocationsDf.ChamberBottom - portLocationsDf.RightPortY) * yconv
        meanLeftPort = [np.mean(portLocationsDf['LeftPortXConv']), np.mean(
            portLocationsDf['LeftPortYConv'])]
        portLocationsDf['LeftPortXConvDev'] = portLocationsDf['LeftPortXConv'] - meanLeftPort[0]
        portLocationsDf['LeftPortYConvDev'] = portLocationsDf['LeftPortYConv'] - meanLeftPort[1]
        bigPortLocationsDf = pd.concat(
            [bigPortLocationsDf, portLocationsDf], axis=0)

    bigCountLogDf = pd.DataFrame()
    bigMetaDataDf = pd.DataFrame()
    for dataSetNumber in range(0, len(countLogList)):
        print(countLogList[dataSetNumber])
        experimentEntry = experimentSummary.loc[experimentSummary['countLogFile']
                                                == countLogList[dataSetNumber]]
        companionMetaData = experimentEntry['metaDataFile'].iloc[0]
        print(companionMetaData)
        companionPortLocationsDf = bigPortLocationsDf.loc[bigPortLocationsDf.Date == extractDateStr(
            experimentEntry['portLocationsFile'].iloc[0])[0]]
        metaDataDf = pd.read_csv(dataFolder + companionMetaData)
        reader = pd.read_csv(
            dataFolder + countLogList[dataSetNumber], chunksize=(endMin+1) * 60 * 30)
        countLogDfUnselected = reader.get_chunk()
        expectedIDs = {int(re.search(r'Ch(.*)_Obj1_X', s).group(1))
                       for s in countLogDfUnselected.filter(regex='Obj1_X').columns}
        existingIDs = set(metaDataDf.ID)
        diffID = expectedIDs - existingIDs
        if len(diffID) > 0:
            print('MetaData is missing IDs ' + str(np.sort(list(diffID))))
        for id in diffID:
            todrop = countLogDfUnselected.filter(regex='Ch'+str(id)).columns
            countLogDfUnselected = countLogDfUnselected.drop(
                todrop.tolist(), axis=1)
        companionPortLocationsDf = companionPortLocationsDf.loc[companionPortLocationsDf.index.isin(
            metaDataDf.index)]
        countLogDfTrimmed = calculateSpeedinCountLog(
            countLogDfUnselected, companionPortLocationsDf, smoothing)
        countLogDfTimeBanded = countLogDfTrimmed.loc[(
            countLogDfTrimmed.Seconds > startMin * 60) & (countLogDfTrimmed.Seconds < endMin * 60)]
        metaDataDf.columns = metaDataDf.columns.str.replace(' ', '')
        metaDataDf['Date'] = extractDateStr(countLogList[dataSetNumber])[0]
        countLogDfNew, countLogDfOld = locoUtilities.resampleCountLog(
            countLogDfTimeBanded, countLogList[dataSetNumber], initialResamplePeriod, longForm)
        countLogDfNew = correctInPortData(countLogDfNew)

        if longForm is False:
            countLogDfNew.columns = countLogList[dataSetNumber][9:28] + \
                '_' + countLogDfNew.columns
        if dataSetNumber == 0:
            bigCountLogDf = countLogDfNew
            bigMetaDataDf = metaDataDf
        else:
            if longForm:
                bigCountLogDf = pd.concat(
                    [bigCountLogDf, countLogDfNew], axis=0)
            else:
                bigCountLogDf = pd.concat(
                    [bigCountLogDf, countLogDfNew], axis=1)
                bigMetaDataDf = pd.concat([bigMetaDataDf, metaDataDf], axis=0)

    bigMetaDataDf = bigMetaDataDf.reset_index(drop=True)
    bigMetaDataDf['Genotype'] = bigMetaDataDf['Genotype'].str.lower()
    bigMetaDataDf['Food1'] = bigMetaDataDf['Food1'].astype(str)
    bigMetaDataDf['Food2'] = bigMetaDataDf['Food2'].astype(str)
    bigMetaDataDf['Starvedhrs'] = bigMetaDataDf['Starvedhrs'].astype(str)
    bigMetaDataDf = assignStatus(bigMetaDataDf)
    return bigMetaDataDf, bigCountLogDf, bigPortLocationsDf, experimentSummary



# %% ../nbs/API/locoDataMunger.ipynb 6
def calculateSpeedinCountLog(countLogDf, companionPortLocationsDf, smoothing, speedThreshold=30, gaussianWindowSize=10, gaussianSTD=3):
    """

    Calcualtes speed from data in countLogs  

    Parameters
    ----------

    countLogDf : pandas dataframe
        contains all the countLog tables.
    companionPortLocationsDf : pandas dataframe
        contains all of the portLocation tables.
    smoothing: boolean
        parameter for whether or not to smooth the data.
    speedThreshold : int
        threshold to remove data points where speed is deemed too high, default value 30.
    gaussianWindowSize : int
        window size for gaussian smoothing, default value 10.

    Returns
    -------
    `newCountLog` : pandas dataframe
        contains all updated countLogs, including newly calculated speed.

    """
    xconv = companionPortLocationsDf.XmmPerPix[0]
    yconv = companionPortLocationsDf.YmmPerPix[0]
    cx = countLogDf.filter(regex='_X') * xconv
    cy = countLogDf.filter(regex='_Y') * yconv
    cv = countLogDf.filter(regex='_Vpix/s')
    ct = countLogDf.filter(regex='Seconds')
    X = cx.rename(columns=lambda x: ''.join(
        [str(x).split('_')[0], '_', str(x).split('_')[1]]))
    Y = cy.rename(columns=lambda x: ''.join(
        [str(x).split('_')[0], '_', str(x).split('_')[1]]))
    ctc = [companionPortLocationsDf.ChamberTopConv.values for i in range(
        0, Y.shape[0])]
    chamberTops = pd.DataFrame(ctc, columns=Y.columns)
    Y = chamberTops - Y
    if smoothing:
        # smoothing X and Y
        XX = X.rolling(gaussianWindowSize, win_type='gaussian').mean(
            std=gaussianSTD)
        YY = Y.rolling(gaussianWindowSize, win_type='gaussian').mean(
            std=gaussianSTD)
    else:
        XX = X
        YY = Y
    deltaXX = np.diff(XX, axis=0)
    deltaYY = np.diff(YY, axis=0)
    deltaT = np.diff(ct, axis=0)
    VV = (deltaXX**2+deltaYY**2)**0.5/deltaT
    VV = pd.DataFrame(np.concatenate(
        [np.zeros([1, VV.shape[1]]), VV]), columns=cv.columns)
    VV = VV.rename(columns=lambda x: ''.join(
        [str(x).split('_')[0], '_', str(x).split('_')[1]]))
    for column in VV.columns:
        VV[column] = intrapolateUnderThreshold(
            VV.loc[:, column], speedThreshold)
    Vy = deltaYY/deltaT
    Vy = pd.DataFrame(np.concatenate(
        [np.zeros([1, Vy.shape[1]]), Vy]), columns=cv.columns)
    Vy = Vy.rename(columns=lambda x: ''.join(
        [str(x).split('_')[0], '_', str(x).split('_')[1]]))
    Vx = deltaXX/deltaT
    Vx = pd.DataFrame(np.concatenate(
        [np.zeros([1, Vx.shape[1]]), Vx]), columns=cv.columns)
    Vx = Vx.rename(columns=lambda x: ''.join(
        [str(x).split('_')[0], '_', str(x).split('_')[1]]))

    lp = [companionPortLocationsDf.LeftPortYConv.values for i in range(
        0, YY.shape[0])]
    leftPort = pd.DataFrame(lp, columns=YY.columns)
    rp = [companionPortLocationsDf.RightPortYConv.values for i in range(
        0, YY.shape[0])]
    rightPort = pd.DataFrame(rp, columns=YY.columns)
    mpX = [companionPortLocationsDf.PortsMidpointXConv.values for i in range(
        0, YY.shape[0])]
    midpointX = pd.DataFrame(mpX, columns=YY.columns)

    InLeftPort = (1*(YY > leftPort) + 1*(XX < midpointX)) == 2
    InRightPort = (1*(YY > rightPort) + 1*(XX > midpointX)) == 2

    XX = XX.rename(columns=lambda x: str(x)+'_X')
    YY = YY.rename(columns=lambda x: str(x)+'_Y')
    VV = VV.rename(columns=lambda x: str(x)+'_V')
    Vy = Vy.rename(columns=lambda x: str(x)+'_vY')
    Vx = Vx.rename(columns=lambda x: str(x)+'_vX')
    InLeftPort = InLeftPort.rename(columns=lambda x: str(x)+'_InLeftPort')
    InRightPort = InRightPort.rename(columns=lambda x: str(x)+'_InRightPort')
    newCountLog = pd.concat([countLogDf.iloc[:, [0, 1, 2]],
                            XX, YY, VV, Vy, Vx, InLeftPort, InRightPort], axis=1)
    return newCountLog



# %% ../nbs/API/locoDataMunger.ipynb 7
def calculatePeriFeedLoco(countLogDf, companionPortLocationsDf, companionEspObj, exptSum, monitorWindow=120, maxDuration_s = None, maxFeedSpeed_nl_s = None, startMin = 0, endMin = 120):
    """

    Calculates speed around feeds 

    Parameters
    ----------

    countLogDf : pandas dataframe 
        contains all the countLog tables.
    companionPortLocationsDf : pandas dataframe
        contains all of the portLocation tables.
    companionEspObj : data object 
        calculated from espresso package.
    exptSum: pandas dataframe
        contains a summary of the expriments.
    monitorWindow : int, default 120
        window size in seconds for the period before and after feed for speed to be calculated
    startMin : int, default 0
        the starting minute for the period to be included in the analysis
    endMin : int, default 120
        the ending minute for the period to be included in the analysis

    Returns
    -------
    `feedsRevisedDf` : pandas dataframe
        contains updated feeds with associated per feed metrics.
    `countLogDfNew` : pandas dataframe
        contains updated countLog tables.
    `feedResults` : pandas dataframe
        contains updated feed metric values calculated.
    `maxSpeed` : pandas dataframe
        contains all updated countLogs, including newly calculated speed.

    """
    feedsRevisedDf = companionEspObj.feeds[companionEspObj.feeds.Valid].sort_values(by = 'RelativeTime_s')
    feedsRevisedDf.insert(len(feedsRevisedDf.columns),'startMonitorIdx',np.nan)
    feedsRevisedDf.insert(len(feedsRevisedDf.columns),'startFeedIdx',np.nan)
    feedsRevisedDf.insert(len(feedsRevisedDf.columns),'startFeedIdxRevised',np.nan)
    feedsRevisedDf.insert(len(feedsRevisedDf.columns),'endFeedIdx',np.nan)
    feedsRevisedDf.insert(len(feedsRevisedDf.columns),'endFeedIdxRevised',np.nan)
    feedsRevisedDf.insert(len(feedsRevisedDf.columns),'endMonitorIdx',np.nan)
    feedsRevisedDf.insert(len(feedsRevisedDf.columns),str(monitorWindow)+'beforeFeedSpeed_mm/s',np.nan)
    feedsRevisedDf.insert(len(feedsRevisedDf.columns),'duringFeedSpeed_mm/s',np.nan)
    feedsRevisedDf.insert(len(feedsRevisedDf.columns),str(monitorWindow)+'afterFeedSpeed_mm/s',np.nan)
    feedsRevisedDf.insert(len(feedsRevisedDf.columns),'revisedFeedDuration_s',np.nan)
    feedsRevisedDf.insert(len(feedsRevisedDf.columns),'countLogID',np.nan)

    feedsRevisedDf = feedsRevisedDf.drop(labels=feedsRevisedDf.loc[np.isnan(
        feedsRevisedDf['FeedDuration_s'])].index, axis=0)

    # setup toolbar

    print('recalculating feed duration for feeds...')
    locoUtilities.startProgressbar()
    for i in feedsRevisedDf.index:
        feed = feedsRevisedDf.loc[i]
        if feed.RelativeTime_s > startMin * 60  and feed.RelativeTime_s <= endMin * 60:
            chamberID = feed['ChamberID']
            feedDate = extractDateStr(chamberID)[0]
            # print(feedDate)
            # print(exptSum.loc[exptSum['feedLogDate']==feedDate])
            countDate = exptSum.loc[exptSum['feedLogDate']
                                    == feedDate]['countLogDate'].iloc[0]
            countLogObjID = countDate + '_Ch' + \
                chamberID.split('amber')[1]+'_Obj1'
            y = countLogDf[countLogObjID+'_Y']
            t = countLogDf[countDate+'_Seconds']
            v = countLogDf[countLogObjID+'_V']
            ploc = companionPortLocationsDf.loc[companionPortLocationsDf.DateChamberID == chamberID]
            startFeedTime = feed['RelativeTime_s']
            endFeedTime = feed['RelativeTime_s'] + feed['FeedDuration_s']
            startFeedIdx = np.abs(t - startFeedTime).idxmin()
            endFeedIdx = np.abs(t - endFeedTime).idxmin()
            outPort = 1*(y[startFeedIdx:endFeedIdx].values -
                         ploc.LeftPortYConv.values < 0)
            longestFeedStretch = np.cumsum(
                outPort) == np.bincount(outPort.cumsum()).argmax()
            longestFeedStretchIdx = [
                j for j, l in enumerate(longestFeedStretch) if l]
            startFeedIdx1 = t.index[t.index.get_loc(
                startFeedIdx)+longestFeedStretchIdx[0]]
            endFeedIdx1 = t.index[t.index.get_loc(
                startFeedIdx)+longestFeedStretchIdx[-1]]
            startFeedTime1 = t[startFeedIdx1]
            endFeedTime1 = t[endFeedIdx1]
            startMonitorTime = np.max([0, startFeedTime1 - monitorWindow])
            startMonitorIdx = np.abs(t - startMonitorTime).idxmin()
            endMonitorTime = np.nanmin(
                [np.nanmax(t.values), endFeedTime1 + monitorWindow])
            endMonitorIdx = np.abs(t - endMonitorTime).idxmin()
            feedsRevisedDf.loc[i, 'countLogID'] = countLogObjID
            feedsRevisedDf.loc[i, 'startMonitorIdx'] = startMonitorIdx
            feedsRevisedDf.loc[i, 'startFeedIdx'] = startFeedIdx
            feedsRevisedDf.loc[i, 'startFeedIdxRevised'] = startFeedIdx1
            feedsRevisedDf.loc[i, 'endFeedIdx'] = endFeedIdx
            feedsRevisedDf.loc[i, 'endFeedIdxRevised'] = endFeedIdx1
            feedsRevisedDf.loc[i, 'endMonitorIdx'] = endMonitorIdx
            feedsRevisedDf.loc[i,'revisedFeedDuration_s'] = endFeedTime1 - startFeedTime1
            vb = np.nanmean(v[startMonitorIdx:startFeedIdx1])
            vd = np.nanmean(v[startFeedIdx1:endFeedIdx1])
            va = np.nanmean(v[endFeedIdx1:endMonitorIdx])
            feedsRevisedDf.loc[i, str(monitorWindow) +
                               'beforeFeedSpeed_mm/s'] = vb
            feedsRevisedDf.loc[i, 'duringFeedSpeed_mm/s'] = vd
            feedsRevisedDf.loc[i, str(monitorWindow) +
                               'afterFeedSpeed_mm/s'] = va
            feedsRevisedDf.loc[i, str(
                monitorWindow)+'duringPercSpeedGain'] = ((vd - vb)/(vb))*100
            feedsRevisedDf.loc[i, str(monitorWindow) +
                               'afterPercSpeedGain'] = ((va - vb)/vb)*100
            if i % 10 == 0:
                locoUtilities.drawProgressbar()
        else:
            break    
    locoUtilities.endProgressbar()
    feedsRevisedDf['revisedFeedDuration_min'] = feedsRevisedDf['revisedFeedDuration_s']/60
    feedsRevisedDf['FeedVol_pl'] = feedsRevisedDf['FeedVol_nl']*1000
    if maxDuration_s:
        feedsRevisedDf = feedsRevisedDf.loc[feedsRevisedDf['FeedDuration_s']< maxDuration_s]
    if maxFeedSpeed_nl_s:
        feedsRevisedDf = feedsRevisedDf.loc[feedsRevisedDf['FeedSpeed_nl/s']< maxFeedSpeed_nl_s]
    grouped_df = feedsRevisedDf.groupby(['ChamberID', 'countLogID'])
    mean_df = feedsRevisedDf.groupby(['ChamberID', 'countLogID']).mean(numeric_only=True)
    total_df = feedsRevisedDf.groupby(['ChamberID', 'countLogID']).sum(numeric_only=True)
    non_numeric_df = feedsRevisedDf.select_dtypes(include='object').groupby(['ChamberID', 'countLogID']).first()
    first_df = feedsRevisedDf.groupby(['ChamberID', 'countLogID']).first(numeric_only=True)
    first_df = first_df.rename(columns = {'RelativeTime_s': 'Latency_s'})
    feedResults = pd.concat([non_numeric_df, first_df[['Latency_s']]], axis = 1)
    feedResults = pd.concat([feedResults, pd.merge(mean_df, total_df, how = 'outer', on = ['ChamberID', 'countLogID'], suffixes=("_Mean", "_Total"))], axis = 1)
    feedResults.reset_index(inplace = True)
    feedResults = feedResults.drop(columns=[ 'revisedFeedDuration_min_Mean',
                                             'revisedFeedDuration_s_Total',
                                            '120duringPercSpeedGain_Mean',
                                            '120afterPercSpeedGain_Mean',
                                            'RelativeTime_s_Mean',
                                            'Valid_Mean', 
                                            'FeedVol_µl_Mean',
                                            'FeedVol_pl_Mean',
                                            'FeedDuration_ms_Mean',
                                            'FeedDuration_s_Mean', 
                                            'FeedSpeed_nl/s_Mean', 
                                            'FeedVol_nl_Mean', 
                                            'AverageFeedCountPerFly_Mean', 
                                            'FeedDuration_ms_Total',
                                            'FeedDuration_s_Total', 
                                            'FeedVol_nl_Total', 
                                            'Valid_Total',
                                            str(monitorWindow)+'duringPercSpeedGain_Total',
                                            str(monitorWindow)+'afterPercSpeedGain_Total', 
                                            'FeedSpeed_nl/s_Total', 
                                            'RelativeTime_s_Total', 
                                            'Starved hrs_Total', 
                                            str(monitorWindow)+'beforeFeedSpeed_mm/s_Total', 
                                            'duringFeedSpeed_mm/s_Total', 
                                            str(monitorWindow)+'afterFeedSpeed_mm/s_Total',
                                              'AverageFeedSpeedPerFly_µl/s_Total',
                                              'FeedVol_µl_Total'])
                                            
                                             
    mealSizeColumn = [i for  i, s in enumerate(feedResults.columns) if ('AverageFeedVolumePerFly_' in s) & ('Mean' in s )][0]
    feedResults['Latency_s'] = feedResults['Latency_s']/60
    feedResults = feedResults.rename(
        columns = {'Starved hrs_Mean':'Starved hrs',
                   feedResults.columns[mealSizeColumn]:'MealSizePerFly_µL',
                   str(monitorWindow)+'beforeFeedSpeed_mm/s_Mean': 'MeanSpeed'+str(monitorWindow)+'sBeforeFeed_mm/s',
                   'duringFeedSpeed_mm/s_Mean': 'MeanSpeedDuringFeed_mm/s',
                   str(monitorWindow)+'afterFeedSpeed_mm/s_Mean': 'MeanSpeed'+str(monitorWindow)+'sAfterFeed_mm/s',
                   'revisedFeedDuration_s_Mean': 'MeanMealDurationPerFly_s',
                   'revisedFeedDuration_min_Total': 'AverageFeedDurationPerFly_min',
                   'AverageFeedCountPerFly_Total': 'AverageFeedCountPerFly',
                    'AverageFeedVolumePerFly_µl_Total': 'AverageFeedVolumePerFly_µl',
                    'AverageFeedSpeedPerFly_µl/s_Mean': 'AverageFeedSpeedPerFly_µl/s',
                    'Latency_s': 'Latency_min',
                    'FeedVol_pl_Total': 'FeedVol_pl'
                  })
    feedResults['duringBeforeSpeedRatio'] = feedResults['MeanSpeedDuringFeed_mm/s'] /feedResults['MeanSpeed'+str(monitorWindow)+'sBeforeFeed_mm/s']
    feedResults['afterBeforeSpeedRatio'] = feedResults['MeanSpeed'+str(monitorWindow)+'sAfterFeed_mm/s'] / feedResults['MeanSpeed'+str(monitorWindow)+'sBeforeFeed_mm/s']
    
    feedVolColumns = [s.replace('_X', '_feedVol_pl')
                      for s in countLogDf.filter(regex='_X').columns]
    feedCountColumns = [s.replace('_X', '_feedCount')
                        for s in countLogDf.filter(regex='_X').columns]
    feedDurationColumns = [s.replace(
        '_X', '_feedRevisedDuration_s') for s in countLogDf.filter(regex='_X').columns]
    cumVolColumns = [s.replace('_X', '_cumVol')
                     for s in countLogDf.filter(regex='_X').columns]
    countLogDfNew = countLogDf
    countLogDfNew.drop(list(countLogDfNew.filter(
        regex='_feedVol_pl')), axis=1, inplace=True)
    countLogDfNew.drop(list(countLogDfNew.filter(
        regex='_feedCount')), axis=1, inplace=True)
    countLogDfNew.drop(list(countLogDfNew.filter(
        regex='_feedRevisedDuration_s')), axis=1, inplace=True)
    countLogDfNew.drop(list(countLogDfNew.filter(
        regex='_cumVol')), axis=1, inplace=True)
    countLogDfNew = pd.concat([countLogDf, pd.DataFrame(
        0, index=countLogDf.index, columns=feedVolColumns + feedCountColumns + feedDurationColumns)], axis=1)
    print('putting feeds back into countlog...')
    locoUtilities.startProgressbar()
    for i in feedsRevisedDf.index:
        countLogID = feedsRevisedDf.loc[i, 'countLogID']
        if type(countLogID)== str:
            endFeedIdxRevised = feedsRevisedDf.loc[i, 'endFeedIdxRevised']
            countLogDfNew.loc[endFeedIdxRevised, countLogID +
                              '_feedVol_pl'] = feedsRevisedDf.loc[i, 'FeedVol_nl']*1000
            countLogDfNew.loc[endFeedIdxRevised, countLogID+'_feedCount'] = 1
            countLogDfNew.loc[endFeedIdxRevised, countLogID +
                              '_feedRevisedDuration_s'] = feedsRevisedDf.loc[i, 'revisedFeedDuration_s']
            # print(countLogDfNew.loc[endFeedIdxRevised])
            # print(feedsRevisedDf.loc[i, 'revisedFeedDuration_s'])
            # print(countLogDfNew.loc[endFeedIdxRevised, countLogID+'_feedRevisedDuration'])
            # plt.plot(countLogDfNew[countLogDfNew.filter('_feedRevisedDuration').columns].fillna(0), 'o')
            locoUtilities.drawProgressbar()
    locoUtilities.endProgressbar()

    durCols = countLogDfNew.filter('_feedRevisedDuration').columns
    countLogDfNew[durCols] = countLogDfNew[durCols].fillna(0)
    cumFeedVol = countLogDfNew.filter(regex='_feedVol').cumsum()
    # print(cumFeedVol.columns)
    # print(cumVolColumns)
    cumFeedVol.columns = cumVolColumns
    countLogDfNew = pd.concat([countLogDfNew, cumFeedVol], axis=1)
    maxSpeed = np.ceil(np.nanmax(feedResults[['MeanSpeed'+str(monitorWindow)+'sBeforeFeed_mm/s',
                                              'MeanSpeedDuringFeed_mm/s', 'MeanSpeed'+str(monitorWindow)+'sAfterFeed_mm/s']]))
    feedsRevisedDf.Status = feedsRevisedDf.Status.str.replace('Sibling', 'Ctrl')
    feedsRevisedDf.Status = feedsRevisedDf.Status.str.replace('Offspring', 'Test')
    feedsRevisedDf.Genotype = feedsRevisedDf.Genotype.str.lower()
    for c in feedResults.columns:
        if 'mm/s' not in c:
            if 'Ratio' not in c:
                if 'Gain' not in c:
                    feedResults[c].fillna(0, inplace=True)
    
    return feedsRevisedDf, countLogDfNew, feedResults, maxSpeed



# %% ../nbs/API/locoDataMunger.ipynb 8
def fallEvents(countLogDf, nstd=4, windowsize=1000, ewm1=12, ewm2=26, ewm3=9):
    """

    Calculates fall events

    Parameters
    ----------

    countLogDf : pandas dataframe
        contains all the countLog tables.
    nstd : int
        number of standards deviations for calculating speed threshold for fall detection, default value 4
    windowsize : int
        number of samples around the fall event for speed threshold to be calculated.
    ewm1: int
        moving average analysis parameter 1, default value 12.
    ewm2 : int
        moving average analysis parameter 2, default value 26.
    ewm3 : int
        moving average analysis parameter 3, default value 9.

    Returns
    -------
    `falls` : pandas series
        a list of timestamps where falls happened
    `newCountLog` : pandas dataframe
        contains updated countLog tables including newly calculated falls.

    """
    # added Jan 2022 to detect falls
    yy = countLogDf.filter(regex='_Y')
    vx = countLogDf.filter(regex='_vX')
    vy = countLogDf.filter(regex='_vY')
    omega = pd.DataFrame(data=np.arctan(vx.values/vy.values), index=vy.index,
                         columns=[c.split('_v')[0] + '_AV' for c in vy.columns])
    exp1 = vy.ewm(span=ewm1, adjust=False).mean()
    exp2 = vy.ewm(span=ewm2, adjust=False).mean()
    macd = exp1-exp2
    exp3 = macd.ewm(span=ewm3, adjust=False).mean()
    a = np.zeros(vy.shape)
    aa = np.zeros(vy.shape)
    b = []
    locoUtilities.startProgressbar()
    for i in range(0, macd.shape[1]):
#         print(i)
        a[:, i], b = labelStretches(macd.iloc[:, i]-exp3.iloc[:, i] < -0.025)
        n = 1
        for j in range(0, len(b)):
            segstart = b.currIdx[j]
            segend = b.currIdx[j]+b.inc[j]
            speedthreshold = - np.nanmean(np.abs(vy.iloc[segstart-windowsize:segend+windowsize, i]))-np.nanstd(
                np.abs(vy.iloc[segstart-windowsize:segend+windowsize, i]))*nstd
            if len(vy.iloc[segstart: segend+1, i]) > 0:
                if np.nanmin(vy.iloc[segstart: segend+1, i].values) < speedthreshold and np.nanmax(yy.iloc[segstart: segend+1, i].values) - np.nanmin(yy.iloc[segstart: segend, i].values) > 0.5:
                    aa[segstart:segend, i] = n
                    n = n + 1        
        if i % 10 == 0:
            locoUtilities.drawProgressbar()    
    locoUtilities.endProgressbar()
    falls = pd.DataFrame(data=aa, index=vy.index, columns=[
                         c.split('_v')[0] + '_Falls' for c in vy.columns])
    countLogDf.drop(list(countLogDf.filter(regex='_AV')), axis=1, inplace=True)
    countLogDf.drop(list(countLogDf.filter(regex='_Falls')),
                    axis=1, inplace=True)
    newCountLog = pd.concat(
        [countLogDf.iloc[:, [0, 1, 2]], omega, falls], axis=1)
    newCountLog = pd.concat([countLogDf, omega, falls], axis=1)
    return falls, newCountLog




# %% ../nbs/API/locoDataMunger.ipynb 9
def labelStretches(vector):
    vectorCopy = vector
    invVector = 1 - vector
    IVcumsum = invVector.cumsum()
    IVbin = np.bincount(IVcumsum)
    IVbinS = IVbin[IVbin > 1]
    IVbinSU = np.unique(IVbinS)
    idxMat = pd.DataFrame(columns=['sIdx', 'inc'])
    n = 0
    import time
        

    for j in range(0, len(IVbinSU)):
        startIdx = [i for i, ivb in enumerate(IVbin == IVbinSU[j]) if ivb]     
        for k in startIdx:
            idxMat.loc[n, ['sIdx', 'inc']] = [k, IVbinSU[j]]
            n = n+1
    idxMat = idxMat.astype(int)
    idxMat = idxMat.sort_values(by='sIdx').reset_index(drop=True)
#     print(idxMat)
    if len(idxMat) > 0:
        idxMat['inc'][1::] = idxMat['inc'][1::]-1
        idxMat['cumInc'] = idxMat['inc'].cumsum()
        curr = [idxMat.loc[i]['sIdx']+idxMat.loc[i-1]['cumInc']
                for i in idxMat.index[1::]]
        curr.append(idxMat.loc[0, 'sIdx'])
        curr.sort()
        idxMat['currIdx'] = curr

        for i in idxMat.index:
            # print(i)
            vectorCopy[idxMat.loc[i, 'currIdx']:idxMat.loc[i, 'currIdx']+idxMat.loc[i, 'inc']] = i+1
    else:
        vectorCopy = vector

    return vectorCopy, idxMat


# %% ../nbs/API/locoDataMunger.ipynb 10
def correctInPortData(countLogDf):
    for column in countLogDf.filter(regex='InLeftPort').columns:
        column
        x = countLogDf[column] > 0
        v, m = labelStretches(x)
        countLogDf[column] = v
    for column in countLogDf.filter(regex='InRightPort').columns:
        x = countLogDf[column] > 0
        v, m = labelStretches(x)
        countLogDf[column] = v
    return countLogDf


# %% ../nbs/API/locoDataMunger.ipynb 11
def intrapolateUnderThreshold(s, th):
    sOverTh = np.array([i for i, x in enumerate(s) if x != 'NaN' and x > th])
    # print('removed indices ' + str(sOverTh))
    s[sOverTh] = 'NaN'
    s = np.array(s, dtype=np.float64)
    nans, interpInd = np.isnan(s), lambda z: z.nonzero()[0]
    s[nans] = np.interp(interpInd(nans), interpInd(~nans), s[~nans])
    return s


# %% ../nbs/API/locoDataMunger.ipynb 12
def assignStatus(metaDataDf):
    if 'Status' not in metaDataDf.columns:
        metaDataDf.insert(1, 'Status', metaDataDf.Genotype, True)
        metaDataDfCopy = metaDataDf.copy()
        TestInd = [i for i, s in enumerate(
            metaDataDf.Genotype) if 'w1118' not in s]
        metaDataDfCopy['Status'] = 'Ctrl'
        metaDataDfCopy.loc[TestInd, 'Status'] = 'Test'
        metaDataDf = metaDataDfCopy
    return metaDataDf

