# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/API/esploco.ipynb.

# %% auto 0
__all__ = ['font_dirs', 'font_files', 'esploco']

# %% ../nbs/API/esploco.ipynb 3
"""
Created on Wed Mar 18 17:59:42 2020
@author: Sanguyu Xu
xusangyu@gmail.com
"""
import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from . import locoDataMunger
from . import locoUtilities
from . import locoPlotters
from . import plotTools as pt
import dabest
from .plotTools import setFont

from matplotlib import font_manager
import matplotlib
font_dirs = ["/Users/sangyuxu/Library/Fonts"]
font_files = font_manager.findSystemFonts(fontpaths=font_dirs)
for font_file in font_files:
    font_manager.fontManager.addfont(font_file)
matplotlib.font_manager.findSystemFonts(fontpaths=None, fontext='ttf')
setFont('inter', 8)


# %% ../nbs/API/esploco.ipynb 4
class esploco(object):
    
    """
    Class for calculating and plotting espresso locomotion data.
    """

    def __init__(self, dataFolder, startMin = 0, endMin = 120, companionEspObj=None, initialResamplePeriod=50, smoothing=True, longForm=False):
        """

        Reads and stores information from countLogs produced by Critta espresso plugin

        Parameters
        ----------
        dataFolder : str
            path to the directory containing all output files of espresso assay
        startMin : int, default 0
            starting minute for analysis
        endMin : int, default 120
            ending minute for analysis
        companionEspObj : object, default None
            from the espresso analysis package
        initialResamplePeriod : int, defualt 50
            period of sample in ms (initialResamplePeriod = 50 ms, sampling frequency = 1000/50 = 20 Hz), default 50
        smoothing : boolean, defult True
            whether or not to smooth the trajectories, default True
        longForm : boolean, default False
            whether or not the data input is the same set of flies but over many days.


        Returns
        -------
        `esploco` object 
            `esploco.resultsDf` : contains relevant output metrics 
            `esploco.resultsDf.ID` : from metadata
            `esploco.resultsDf.Status` : 'Test' or 'Ctrl'
            `esploco.resultsDf.Genotype` : genotype
            `esploco.resultsDf.Sex` : from metadata
            `esploco.resultsDf.MinimumAge` : from metadata
            `esploco.resultsDf.MaximumAge` : from metadata 
            `esploco.resultsDf.Food1` : from metadata
            `esploco.resultsDf.Food2` : from metadata 
            `esploco.resultsDf.Temperature` : from metadata 
            `esploco.resultsDf.#Flies` : from metadata 
            `esploco.resultsDf.Starvedhrs` : from metadata 
            `esploco.resultsDf.Date` : date of feedlog
            `esploco.resultsDf.averageSpeed_mm/s` : instantaneous speed of the fly 
            `esploco.resultsDf.xPosition_mm` : instantaneous x position of the fly 
            `esploco.resultsDf.yPosition_mm` : instantaneous y position of the fly 
            `esploco.resultsDf.inLeftPort` : proportion of time the fly was in left port
            `esploco.resultsDf.inRightPort` : proportion of time the fly was in right port 
            `esploco.resultsDf.countLogDate` : date from countlog
            `esploco.resultsDf.feedLogDate` : date from feedlog
           
        """
        
        self.cm = 1/2.54
        if dataFolder[-1] != '/':
            dataFolder = dataFolder+'/'
        self.metaDataDf, self.countLogDf, self.portLocationsDf, self.experimentSummary = locoDataMunger.readMetaAndCount(
            dataFolder, companionEspObj, startMin, endMin, initialResamplePeriod, smoothing, longForm)
        outputDir = locoUtilities.makeOutputFolders(dataFolder)
        self.dataFolder = dataFolder
        self.outputFolder = outputDir
        self.startMin = startMin
        self.endMin = endMin
        self.resultsDf = self.metaDataDf
        self.resultsDf['averageSpeed_mm/s'] = np.nanmean(
            self.countLogDf.filter(regex='_V'), axis=0)
        self.resultsDf['xPosition_mm'] = np.nanmean(
            self.countLogDf.filter(regex='_X'), axis=0)
        self.resultsDf['yPosition_mm'] = np.nanmean(
            self.countLogDf.filter(regex='_Y'), axis=0)
        self.resultsDf['inLeftPort'] = np.nanmean(
            100*(self.countLogDf.filter(regex='LeftPort') > 0), axis=0)
        self.resultsDf['inRightPort'] = np.nanmean(
            100*(self.countLogDf.filter(regex='RightPort') > 0), axis=0)
        if any(self.experimentSummary.countLogDate.str.contains(self.resultsDf.Date[0])):
            self.resultsDf['countLogDate'] = self.resultsDf['Date']
            self.resultsDf['feedLogDate'] = [self.experimentSummary.loc[self.experimentSummary['countLogDate']
                                                                        == d]['feedLogDate'].iloc[0] for d in self.resultsDf['Date']]
        else:
            self.resultsDf['feedLogDate'] = self.resultsDf['Date']
            self.resultsDf['countLogDate'] = [self.experimentSummary.loc[self.experimentSummary['feedLogDate']
                                                                         == d]['countLogDate'].iloc[0] for d in self.resultsDf['Date']]
#     show_doc(__init__)
    def versionNotes(self):
        print('version notes 0.1.1: added portlocations')
        print('version notes 0.1.2: added gaussian smoothing of x y locations')
        print('version notes 0.1.3: added detection of fall events')
        print('version notes 0.1.4: bugfix setfont and moved colorbar on heatmap to bottom')
        print('version notes 0.1.5: added handling of dabest 0.3.9999')
        print('version notes 0.2.0: major refactoring')
        print('version notes 23.04.21: nbdev')
        print('version notes 23.10.22: updated to account for new pandas')
        print('version notes 23.12.11: updated to fix experimental end time')

 
    def plotChamberSmallMultiples(self, ncol=15, customPalette=None, setNumber=None):
        """

        Plots trajectories and or heatmaps in the arrangement of the chambers for each dataset

        Parameters
        ----------
        ncol : int, default 15.
            number of columns for the plots.
        customPalette : dict, default None
            user can supply a dict for use as a custom palette.
        setNumber : int, default None
            user specfied set to plot.

        Returns
        -------
        `chamberSmallsTrack`
            figure object.
            
        `chamberSmallsHeat` 
            figure object.

        """
        
        dates = self.metaDataDf.Date.unique()
        chamberSmallsTrack = np.empty(len(dates), dtype=object)
        axarrT = np.empty(len(dates), dtype=object)
        chamberSmallsHeat = np.empty(len(dates), dtype=object)
        axarrH = np.empty(len(dates), dtype=object)
        print('Espresso Runs found:\n')
        print(dates)
        if setNumber is not None:
            dates = [dates[setNumber]]
        for i in range(0, len(dates)):
            print('\n\n plotting ' + dates[i] + '...')
            portFile = self.experimentSummary.loc[self.experimentSummary['metaDataFile']
                                                  == 'MetaData_'+dates[i] + '.csv']['portLocationsFile'].iloc[0]
            portDate = locoDataMunger.extractDateStr(portFile)[0]
            submeta = self.metaDataDf.loc[self.metaDataDf.Date == dates[i]]
            subcount = self.countLogDf.filter(regex=dates[i])
            subport = self.portLocationsDf.loc[self.portLocationsDf.Date == portDate]
            chamberSmallsTrack[i] = locoPlotters.putThingsInToChamberSubplot(
                subcount, submeta, subport, customPalette, ncol)
            chamberSmallsHeat[i] = locoPlotters.putThingsInToChamberSubplot(
                subcount, submeta, subport, customPalette, ncol, locoPlotters.espressoPlotHeatmap)
            outputDir = self.outputFolder + 'chamberPlots/'
            locoUtilities.espressoSaveFig(
                chamberSmallsTrack[i], 'chamberSmallsTrack', dates[i], outputDir, pngDPI=200)
            locoUtilities.espressoSaveFig(
                chamberSmallsHeat[i], 'chamberSmallsHeat', dates[i], outputDir, pngDPI=200)
        self.chamberSmallsTrack = chamberSmallsTrack
        self.chamberSmallsHeat = chamberSmallsHeat
        return chamberSmallsTrack, chamberSmallsHeat
#     show_doc(plotChamberSmallMultiples)
    
    def plotMeanHeatMaps(self, binSize=0.2, row=None, col=None, reverseRows=False, reverseCols=False, 
                         verbose=False, heatmapCMap='RdYlBu_r', smooth=2, plotZScore = False, vmin = None, vmax = None):
        """

        Plots heatmap of mean duration stayed at each location throughout the chamber grouped by criteria

        Parameters
        ----------
        binSize : int, default 0.2
            the size of the pixel in the heatmap
        row : str, default None
            a column name or independent variable to use for grouping the rows
        col : str, default None
            a column name or independent variable to use for grouping the columns
        reverseRows : boolean, default False
            to reverse the order of the rows 
        reverseCols : boolean, default False
            to reverse the order of the columns 
        verbose : boolean, defult False
            to produce output
        heatmapCMap : cmap, default 'RdYlBu_r'
            colormap used for the heatmap
        smooth : int, default 2
            this defines how much smoothing happenes in with the Gaussian Kernel. 
        plotZScore : boolean, defult False. 
            this toggles between plotting raw heatmap in seconds and z-score
        vmin : float, default None
            this forces the vmin on the heatmap color scale
        vmax : float, default None
            this forces the vmax on the heatmap color scale


        Returns
        -------
        `meanHeatmapFig`   
            figure object.
            
        `Hall` 
            heatmap matrix. this the raw matrix when plotZScore is False and it is the z-score matrix when plotZScore is True.
            
        `images` 
        """
        

        heatMapOutputDir = self.outputFolder
        if verbose:
            meanHeatmapFig,  Hall, images, smallHeatmapFigs = locoPlotters.espressoPlotMeanHeatmaps(
                self, binSize, None, None, False, False, verbose, heatmapCMap, smooth, plotZScore, vmin, vmax)
            locoUtilities.espressoSaveFig(
                smallHeatmapFigs, 'smallHeatmapFigs', self.metaDataDf.Date[0], heatMapOutputDir, pngDPI=200)
        else:
            meanHeatmapFig, Hall, images = locoPlotters.espressoPlotMeanHeatmaps(
                self, binSize, row, col, reverseRows, reverseCols, verbose, heatmapCMap, smooth, plotZScore, vmin, vmax)
        # self.resultsDf = resultsDf
        self.heatmapMatrix = Hall
        self.meanHeatmapFig = meanHeatmapFig
        self.heatmapImages = images
    
#     show_doc(plotMeanHeatMaps)
    
    def plotBoundedLines(self,  colorBy, locoSuffix='V', row=None, col=None, rp='300s', YLim=[], customPalette={}, reverseRows=False,
                         reverseCol=False, xUnit='min'):
        """

        Plots ribbon plots of time series data such as speed, y-position, x-position, proportion of time in left port and right port

        Parameters
        ----------
        colorBy : str
            column name for coloring the plots by
        locoSuffix : str, default 'V'
            'V': Speed of the fly, Y label is 'Average Speed (mm/s)', 
            'X': X position of the fly, Y label is 'X Position (mm)', 
            'Y': Y position of the fly, Y label is 'Y Position (mm)',
            'InLeftPort': 'Percent time in Left Port',  
            'InRightPort': 'Percent time in Right Port'
        row : str, default None
            a column name or independent variable to use for grouping the rows
        col : str, default None
            a column name or independent variable to use for grouping the columns
        rp : str, default '300s'
            resample rate
        YLim : list, default []
            custom y-lim for the plot
        customPalette : str, default None
            a column name or independent variable to use for grouping the columns             
        reverseRows : boolean, default False
            to reverse the order of the rows 
        reverseCols : boolean, default False
            to reverse the order of the columns 
        xUnit : str, defult 's'

        Returns
        -------
        `figure`   
            figure object.
        `axes`  
            axes handle for the axes.
        `meanLines`  
            array of values that are the plotted meanlines.
        `ciBounds`  
            array of values that are the plotted ci.

        """
        
        font_dirs = ["/Users/sangyuxu/Library/Fonts"]
        font_files = font_manager.findSystemFonts(fontpaths=font_dirs)
        for font_file in font_files:
            font_manager.fontManager.addfont(font_file)
        matplotlib.font_manager.findSystemFonts(fontpaths=None, fontext='ttf')
        setFont('inter', 8)
        if xUnit == 'hour':
            T = self.countLogDf.iloc[:, 0]/3600
        else:
            T = self.countLogDf.iloc[:, 0]/60

        if 'Port' in locoSuffix:
            metric = 100*(self.countLogDf.filter(regex='_' + locoSuffix) > 0)
        else:
            metric = self.countLogDf.filter(regex='_' + locoSuffix)

        listOfPlots, gp, cPalette = locoPlotters.subplotRowColColor(
            self.metaDataDf, colorBy, row, col, reverseRows, reverseCol)
        if customPalette:
            cPalette = customPalette
        nr, nc = listOfPlots[-1][0][0:2]
        figure, axes = plt.subplots(
            nrows=nr + 1, ncols=nc + 1, squeeze=False, figsize=(3 * (nc + 1), 3 * (nr + 1)))
        plotNames = [0]*len(listOfPlots)
        meanLines = [0]*len(listOfPlots)
        ciBounds = [0]*len(listOfPlots)

        yl = {'V': 'Average Speed (mm/s)', 'X': 'X Position (mm)', 'Y': 'Y Position (mm)',
              'InLeftPort': 'Percent time in Left Port',  'InRightPort': 'Percent time in Right Port'}
        for i in range(0, len(listOfPlots)):
            # print(listOfPlots[i])
            ro, co = listOfPlots[i][0][0:2]
            name = listOfPlots[i][1]
            ind = gp[name]
            locoPlotters.plotBoundedLine(
                T, metric.iloc[:, ind], ax=axes[ro, co], c=cPalette[name[-1]], resamplePeriod=rp)
            meanLines[i] = axes[ro, co].meanLine[0]
            ciBounds[i] = axes[ro, co].ciBound
            if co == 0:
                axes[ro, co].set_ylabel(yl[locoSuffix])
            if ro == axes.shape[0]:
                axes[ro, co].set_xlabel('Time (hour)')
            axes[ro, co].set_title(name[0] + ' ' + name[1])
            axes[ro, co]. spines["right"].set_visible(False)
            axes[ro, co]. spines["top"].set_visible(False)
            plotNames[i] = name[-1]
        ylims = [ax.get_ylim() for ax in axes.flatten()]
        for i in range(0, len(listOfPlots)):
            ro, co = listOfPlots[i][0][0:2]
            if len(YLim) > 0:
                axes[ro, co].set_ylim(YLim)
            else:
                axes[ro, co].set_ylim([np.min(ylims), np.max(ylims)])
            locoPlotters.setAxesTicks(axes[ro, co], True, gridState=False)

        axes[ro, co].legend(plotNames, loc='upper right', fontsize = 10)

        locoUtilities.espressoSaveFig(
            figure, 'boundedTS_' + locoSuffix + '_', self.metaDataDf.Date[0], self.outputFolder)

        return figure, axes, meanLines, ciBounds
#     show_doc(plotBoundedLines)

    def calculatePeriFeedSpeed(self, companionEspObj, monitorWindow=120, startSeconds=0, maxDuration_s = None, maxFeedSpeed_nl_s = None, plotDiagonal = True, plotContrast = True):
        """

        Calculates speed of the fly around a feed

        Parameters
        ----------
        companionEspObj : object, default None
            from the espresso analysis package
        monitorWindow : int, default 120
            size of the window in seconds before and after the feed to monitor speed in
        startSeconds : int, default 0 seconds
            lower range of data to analyse, deprecated in v.23.12.11
        plotDiagonal : boolean, default True
            whether or not to plot the diagonal speed plot 
        plotContrast : boolean, default True
            whether or not to plot the contrast plots 

        Returns
        -------
        `esploco.feedsRevisedDf`   
            pandas dataframe that contains individual feeds and info about them in a time series.
        `esploco.resultsDf`  
            updated to contain information about feed and perifeed metrics
            `esploco.resultsDf.ChamberID` : from feedlog metadata
            `esploco.resultsDf.Starved hrs` : from feedlog metadata 
            `esploco.resultsDf.MealSizePerFly_µL` : mean volume per meal per fly in µL
            `esploco.resultsDf.AverageFeedSpeedPerFly_µl/s` : mean feed speed per fly over all µL/s
            `esploco.resultsDf.MeanSpeed120sBeforeFeed_mm/s` : mean speed before feed mm/s
            `esploco.resultsDf.MeanSpeedDuringFeed_mm/s` : mean speed during feed mm/s 
            `esploco.resultsDf.MeanSpeed120sAfterFeed_mm/s`' : mean speed 120s after feed mm/s
            `esploco.resultsDf.MeanMealDurationPerFly_s` : mean meal duration per fly s 
            `esploco.resultsDf.Tube1` : food in Tube 1
            `esploco.resultsDf.AverageFeedVolumePerFly_µl` : total volume per fly µL 
            `esploco.resultsDf.AverageFeedCountPerFly` : total count per fly
            `esploco.resultsDf.AverageFeedDurationPerFly_min` : total feed duration per fly
            `esploco.resultsDf.FeedVol_pl` : total feed volume in pico liter
            `esploco.resultsDf.Latency_min` : latency to first feed in min
            `esploco.resultsDf.duringBeforeSpeedRatio` : ratio between during feed speed and before feed speed 
            `esploco.resultsDf.afterBeforeSpeedRatio` : ratio between after feed speed and before feed speed.

        """
        
        
        self.feedsRevisedDf, self.countLogDf, self.meanPeriSpeed, self.maxSpeed= locoDataMunger.calculatePeriFeedLoco(
            self.countLogDf, self.portLocationsDf, companionEspObj, self.experimentSummary, monitorWindow,maxDuration_s = maxDuration_s,  maxFeedSpeed_nl_s = maxFeedSpeed_nl_s, startMin = self.startMin, endMin = self.endMin)
        self.resultsDf['ChamberID'] = self.resultsDf['feedLogDate'] + '_Chamber' + self.resultsDf['ID'].astype(str)
        nonFeeders = list(set(self.resultsDf.ChamberID.unique())-set(self.feedsRevisedDf.ChamberID.unique()))
        nonFeederDf = self.resultsDf.loc[self.resultsDf['ChamberID'].isin(nonFeeders)][['ChamberID', 'Genotype', 'Temperature', 'Status']]
        self.feedsRevisedDf = pd.merge(self.feedsRevisedDf, nonFeederDf, how = 'outer', on = ['ChamberID', 'Genotype', 'Temperature', 'Status'])
        self.feedsRevisedDf['FeedVol_pl'] = self.feedsRevisedDf['FeedVol_nl']*1000
        if 'MeanSpeed'+str(monitorWindow)+'sBeforeFeed_mm/s' in self.resultsDf.columns:
            self.resultsDf[['ChamberID', 'MeanSpeed'+str(monitorWindow)+'sBeforeFeed_mm/s', 
                            'MeanSpeedDuringFeed_mm/s','MeanSpeed'+str(monitorWindow)+'sAfterFeed_mm/s']] = self.meanPeriSpeed[['ChamberID', 'MeanSpeed'+str(monitorWindow)+'sBeforeFeed_mm/s', 
                                                                                  'MeanSpeedDuringFeed_mm/s',  'MeanSpeed'+str(monitorWindow)+'sAfterFeed_mm/s']]
        else:
            self.resultsDf = pd.merge(self.meanPeriSpeed, self.resultsDf, how="outer", on='ChamberID')
        for s in ['AverageFeedVolumePerFly_µl', 'MealSizePerFly_µL', 'AverageFeedCountPerFly',
                 'MeanMealDurationPerFly_s', 'AverageFeedDurationPerFly_min', 'AverageFeedSpeedPerFly_µl/s',
                 ]:
            self.resultsDf[s] = self.resultsDf[s].fillna(0)
        self.resultsDf['Latency_min'] = self.resultsDf['Latency_min'].fillna(120)
        self.monitorMin = str(int(monitorWindow/60))+' min'
        self.outputPrefix = self.outputFolder+self.monitorMin
        if plotDiagonal:
            PeriFeedDiagonal = locoPlotters.plotPeriFeedDiagonal(self, monitorWindow)
        if plotContrast:
            pairedSpeedPlots = locoPlotters.plotPairedSpeeds(self, monitorWindow)
    
#     show_doc(calculatePeriFeedSpeed)
    
    def plotStacked(self, endMin = 120, metricsToStack = ['Volume', 'Speed'], colorBy = 'Genotype', plotTitle = '', 
                    customPalette = None, figsize = None, plotNonFeeders = True, dotratio = 20, dotbase = 5, dotalpha = 0.4, bubbleYLabelSize = 12,
                    ylimPresets = None, showRasterYticks = False, ribbonLegend = False, bubbleLegend = True):
        """

        Plots a raster of feeds stacked with a selection of other metrics in a ribbon

        Parameters
        ----------
        endMin : int, in min, default 120
            the upper range of data to plot
        metricsToStack : list, default ['Volume', 'Speed']
            metrics to plot in ribbons under the raster
        colorBy : str, default 'Genotype'
            the data column to use for coloring the plots 
        customPalette : dict, default None
            custom palette 
        figsize : list of two elements, default None
            figure size in cm, e.g. [10, 10]
        dotratio : int, default 20
            scaling factor of dot to feed size
        dotbase : int, default 5
            constant component for dot to feed size conversion
        plotNonFeeders : boolean, default True
        ylimPresets : an array of two element arrays, default None
            e.g. if there are 2 ribbon plots, ylimPresets can be [[0, 1], [1, 2]]
        showRasterYticks : boolean, default False         
            when True, leaves the yticklabels on the raster plot for chamberID

        Returns
        -------
        `stackedFig`   
            the figure.
        `feeds_sorted`  
            the sorted feeds plotted.
        `colorBy`  
            the final groupings for the coloring.

        """
        font_dirs = ["/Users/sangyuxu/Library/Fonts"]
        font_files = font_manager.findSystemFonts(fontpaths=font_dirs)
        for font_file in font_files:
            font_manager.fontManager.addfont(font_file)
        matplotlib.font_manager.findSystemFonts(fontpaths=None, fontext='ttf')
        setFont('inter', 8)
        if figsize == None:
            figsize = [15*self.cm, (12+len(metricsToStack)*4)*self.cm]                    
        feeds = self.feedsRevisedDf.loc[self.feedsRevisedDf['RelativeTime_s']<=endMin*60]
        if plotNonFeeders:
            nonFeeders = list(set(self.resultsDf.ChamberID.unique())-set(feeds.ChamberID.unique()))
            nonFeederDf = self.resultsDf.loc[self.resultsDf['ChamberID'].isin(nonFeeders)][['ChamberID', 'Genotype', 'Temperature', 'Status']]
            feeds = pd.merge(feeds, nonFeederDf, how = 'outer', on = ['ChamberID', 'Genotype', 'Temperature', 'Status'])
            nonFeederindex = feeds.loc[feeds['AviFile'].isna()].index
            feeds.iloc[nonFeederindex, list(feeds.columns).index('RelativeTime_s')] = endMin*60
            feeds.iloc[nonFeederindex, list(feeds.columns).index('FeedVol_nl')] = 0
        else:
            feeds = feeds.loc[~feeds['AviFile'].isna()]
        if type(colorBy) == list and len(colorBy)>1:
            self.metaDataDf[''.join(colorBy)] = self.metaDataDf[colorBy].agg('-'.join, axis=1)
            feeds[''.join(colorBy)] = feeds[colorBy].agg('-'.join, axis=1)
            colorBy = ''.join(colorBy)
        keys = self.metaDataDf[colorBy].unique()
        shortkeys = [''] * len(keys)
        for k in range(len(keys)):
            if 'Red Light' in keys[k]:
                shortkeys[k] = keys[k].replace('-Red Light', '')
            elif 'Green Light' in keys[k]:
                shortkeys[k] = keys[k].replace('-Green Light', '')
            else:
                shortkeys = keys
        feeds_sorted = feeds.sort_values(by=[colorBy, 'RelativeTime_s']).dropna()
        feeds_sorted['Starvedhrs'] = feeds_sorted['Starvedhrs'].astype(float).astype('int').astype('str')
        chord = feeds_sorted.ChamberID.reset_index(drop = True)
        _, idx = np.unique(chord, return_index=True)
        chamberLabels = chord[np.sort(idx)]
        chord_catType = pd.CategoricalDtype(categories = chamberLabels, ordered = True)
        feeds_sorted['ChamberID'] = feeds_sorted['ChamberID'].astype(chord_catType)
        feeds_sorted['time'] = pd.to_datetime(feeds_sorted['RelativeTime_s'], unit='s')
        idx = pd.date_range(feeds_sorted.iloc[0]['time'], feeds_sorted.iloc[-1]['time'], freq = 'ms')
        plColumns = self.countLogDf.filter(regex = '_feedVol_pl').columns
        nlColumns = self.countLogDf.filter(regex = '_feedVol_nl').columns
        if len(nlColumns)==0:
            nlColumns = [s.replace('_feedVol_pl', '_feedVol_nl') for s in plColumns]
            nlDf = self.countLogDf[plColumns].div(1000)
            nlDf.columns = nlColumns
            self.countLogDf = pd.concat([self.countLogDf, nlDf], axis = 1)
        metricDict = {'Volume': '_feedVol_nl', 
                      'Count': '_feedCount', 
                      'Duration': '_feedRevisedDuration_s',  
                     'Speed': '_V', 
                     'Y': '_Y'}
        metricYLabelsDict = {'Volume': 'Feed \nVolume (nL)', 
                      'Count': 'Feed Count', 
                      'Duration': 'Feed \nDuration (s)',  
                     'Speed': 'Speed (mm/s)', 
                     'Y': 'Height (mm)'}
        if customPalette == None:
            palette = locoPlotters.espressoCreatePalette(keys)
        else:
            palette = customPalette
        colorByKeys = {k: self.metaDataDf.loc[self.metaDataDf[colorBy] == k].index for k in keys}
        stackedFig, stackedAxes = plt.subplots(nrows = len(metricsToStack)+3, ncols = 1, tight_layout = True)
        gs = stackedAxes[1].get_gridspec()
        
        for ax in stackedAxes[0:3]:
            ax.remove()
        axbig = stackedFig.add_subplot(gs[0:3])
#         axbig.set_ylabel('Fly ID', fontweight = 'semibold')
        axbig.plot(feeds_sorted['RelativeTime_s'], feeds_sorted['ChamberID'], 'w.')
        axbig.invert_yaxis()
        axbig.spines['top'].set_visible(False)
        axbig.spines['right'].set_visible(False)
        axbig.set_xlim(-endMin*0.02, endMin*1.05)
        for i in range(len(feeds_sorted.index)):
            feed = feeds_sorted.iloc[i, :]
            if feed['Valid']==True:
                axbig.plot(feed['RelativeTime_s']/60, feed['ChamberID'], '.', 
                           color = palette[feed[colorBy]], 
                           markersize = dotbase+dotratio*feed['FeedVol_nl']/feeds_sorted['FeedVol_nl'].max(),
                           alpha = dotalpha)
            else:
                if plotNonFeeders:
                    axbig.plot(feed['RelativeTime_s']/60, feed['ChamberID'], '.', 
                       color = None, markersize = dotbase)
        for k in range(len(keys)):
            lineIdx = feeds_sorted.loc[feeds_sorted[colorBy] == keys[k]]['ChamberID']
            uniqueLineIdx = lineIdx.values.unique()
#             plt.plot([-endMin*0.05, -endMin*0.05], [uniqueLineIdx[0], uniqueLineIdx[-1]], color = palette[keys[k]])
            plt.text(-endMin*0.03, uniqueLineIdx[round(len(uniqueLineIdx)/2)], shortkeys[k], ha = 'right', 
                     color = palette[keys[k]], fontsize = bubbleYLabelSize, fontweight = 'semibold', verticalalignment = 'center', fontname = 'inter')
        keyDots =[ 0.05, 0.1, 0.2, 0.4]
        keyDotsLabels =[i*1000 for i in keyDots]
        height = np.array(axbig.get_ylim()).max()
        keyDotsY =[height*0.15, height*0.10,height*0.05,0]
        if bubbleLegend:
            for i in range(len(keyDots)):
                plt.plot(endMin*1.04, keyDotsY[i], '.', markersize = dotbase+dotratio*keyDots[i], c = 'k', alpha = dotalpha)
                plt.text(endMin*1.06, keyDotsY[i], str("%.0f" % keyDotsLabels[i])+' pL', c = 'k', verticalalignment = 'center', fontname = 'inter')
        s = [lab.get_text().split('ber')[-1] for lab in axbig.get_yticklabels()]
        axbig.tick_params(
            axis='y',          # changes apply to the x-axis
            which='both',      # both major and minor ticks are affected
            left=False,      # ticks along the bottom edge are off
            top=False)
        countLogDfRange = self.countLogDf.loc[self.countLogDf.iloc[:, 0]<endMin*60]
        def ribbonMetric(countLog, metric, colorBy, palette, colorByKeys, ax = None):
            for k in range(len(keys)):
                if metric in ['_feedVol_nl', '_feedCount', '_feedRevisedDuration_s']:
                    aggMethod = 'sum'
                else: 
                    aggMethod = 'mean'
                locoPlotters.plotBoundedLine(countLogDfRange.iloc[:, 0]/60, 
                                             countLogDfRange.filter(regex = metric).iloc[:, colorByKeys[keys[k]]], 
                                             ax = ax, c = palette[keys[k]],  resamplePeriod = '60s', aggMethod = aggMethod, label = shortkeys[k])
        for [m, mm]  in enumerate(metricsToStack):
            ribbonMetric(countLogDfRange,  metricDict[mm], colorBy = colorBy,palette = palette, colorByKeys = colorByKeys, 
                         ax = stackedAxes[m+3])
            stackedAxes[m+3].set_ylabel(metricYLabelsDict[mm], fontweight = 'semibold')
            if ribbonLegend == False:
                if stackedAxes[m+3].get_legend():
                    stackedAxes[m+3].get_legend().remove()    
                else:
                    stackedAxes[m+3].get_legend()            
            stackedAxes[m+3].set_xlim(-endMin*0.02, endMin*1.05)
            stackedAxes[m+3].spines[[ 'top']].set_visible(False)
            stackedAxes[m+3].spines[['right']].set_visible(False)
#             stackedAxes[m+3].grid(None)
            if ylimPresets:
                stackedAxes[m+3].set_ylim(ylimPresets[m])            
            else:
                stackedAxes[m+3].set_ylim(0-stackedAxes[m+3].get_ylim()[1]*0.05, stackedAxes[m+3].get_ylim()[1])
            if m !=len(metricsToStack)-1:
                stackedAxes[m+3].set_xticklabels('')
        stackedAxes[-1].set_xlabel('Time (min)', fontname = 'inter', fontweight = 'semibold')
        s = [lab.get_text().split('ber')[-1] for lab in axbig.get_yticklabels()]
        if showRasterYticks:
            axbig.set_yticklabels(s, fontsize = 5, fontname = 'inter')
        else: 
            axbig.set_yticklabels('')
        axbig.set_xticklabels('')
        stackedFig.set_size_inches(figsize[0], figsize[1])
        stackedFig.suptitle(plotTitle, x = 0.1, y = 0.96, horizontalalignment='left', 
                            verticalalignment='top', fontsize = 20, fontname="inter", fontweight = 'semibold')
        locoUtilities.espressoSaveFig(
            stackedFig, 'TimeAligned' + ''.join(metricsToStack), self.metaDataDf.Date[0], self.outputFolder)

        return stackedFig, feeds_sorted, colorBy
#     show_doc(plotStacked)
    
    def calculateFallEvents(self, nstd=4, windowsize=1000, ewm1=12, ewm2=26, ewm3=9):
        """

        Detects fall events

        Parameters
        ----------
        nstd : int, default 4
            parameter in macd analysis
        windowsize : int, default 1000
            window size in macd analysis
        ewm1 : int, default 12
            parameter in macd analysis
        ewm2 : int, default 26
            parameter in macd analysis
        ewm3 : int, default 9
            parameter in macd analysis

        Returns
        -------
        `self.resultsDf`   
            updated to include `falls`

        """

        # added Jan 2022 to detect falls
        print('Detecting Fall Events...')
        falls, newCountLog = locoDataMunger.fallEvents(
            self.countLogDf, nstd, windowsize, ewm1, ewm2, ewm3)
        self.resultsDf['falls'] = np.nanmax(falls, axis=0)
        self.countLogDf = newCountLog
        print('Done')
#     show_doc(calculateFallEvents) 
        
        
        
        
