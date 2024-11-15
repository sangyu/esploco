# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/API/locoPlotters.ipynb.

# %% auto 0
__all__ = ['font_dirs', 'font_files', 'espressoChamberStyling', 'espressoCreatePalette', 'espressoPlotTracking',
           'espressoPlotHeatmap', 'espressoPlotMeanHeatmaps', 'plotBoundedLine', 'putThingsInToChamberSubplot',
           'plotChamber', 'subplotRowColColor', 'plotPeriFeedDiagonal', 'plotPairedSpeeds', 'createWesAndersonPalette',
           'setAxesTicks']

# %% ../nbs/API/locoPlotters.ipynb 3
"""
Created on Mon Jul 27 14:30:12 2020

@author: Sanguyu Xu
xusangyu@gmail.com
"""

# 08/2021 changed sibling/offspring notation to ctrl/test notation
import matplotlib.pyplot as plt
import numpy as np
from . import locoUtilities
from matplotlib import colors
import dabest
from .plotTools import setFont
from . import plotTools
from matplotlib import font_manager
import matplotlib
font_dirs = ["/Users/sangyuxu/Library/Fonts"]
font_files = font_manager.findSystemFonts(fontpaths=font_dirs)
for font_file in font_files:
    font_manager.fontManager.addfont(font_file)
matplotlib.font_manager.findSystemFonts(fontpaths=None, fontext='ttf')
setFont('inter', 8)


# %% ../nbs/API/locoPlotters.ipynb 4
def espressoChamberStyling(ax, axisSwitch = 'off'):
    ax.set_aspect('equal')
    ax.spines['bottom'].set_color('gray')
    ax.spines['top'].set_color('gray')
    ax.spines['right'].set_color('gray')
    ax.spines['left'].set_color('gray')
    ax.axis(axisSwitch)
    ax.set_xlim(0, 13)
    ax.set_ylim(-2, 18)



# %% ../nbs/API/locoPlotters.ipynb 5
def espressoCreatePalette(items, testColor = 'orangered'):
    import numpy as np
    keys = np.sort(np.unique(items))[::-1]
    colorPalette = {}
    if 'chrimson' in ''.join(keys):
        testColor = 'orangered'
    elif 'acr' in "".join(keys):
        testColor = 'seagreen'
        
    n=0
    ctrlColor = {'orangered':'peachpuff', 'seagreen':'mediumaquamarine'}
    for i in range(len(keys)):
        if 'gal4' in keys[i]:
            if 'w1118' in keys[i]:
                colorPalette[keys[i]] = 'k'
                continue
            if 'acr' in keys[i]:
                if 'Off' in keys[i]:
                    colorPalette[keys[i]] = 'mediumaquamarine'
                else:
                    colorPalette[keys[i]] = 'seagreen'
                continue
            if 'chrimson' in keys[i]:
                if 'Off' in keys[i]:
                    colorPalette[keys[i]] = 'peachpuff'
                else:
                    colorPalette[keys[i]] = 'orangered'
                continue
            if 'tetx' in keys[i]:
                colorPalette[keys[i]] = 'violet'
                continue            
        if 'ms' in keys[i]:
            if 'w1118' in keys[i]:
                colorPalette[keys[i]] = 'k'
                continue
            if 'cas' in keys[i]:
                colorPalette[keys[i]] = 'seagreen'
                continue
        elif 'Ctrl' in keys[i]:
            if 'Off' in keys[i]:
                colorPalette[keys[i]] = 'lightgray'
            else:
                colorPalette[keys[i]] = 'k'
            continue
        elif 'Test' in keys[i]:
            if 'Off' in keys[i]:
                colorPalette[keys[i]] = ctrlColor[testColor]
            else:
                colorPalette[keys[i]] = testColor 
            continue
        elif 'Light On' in keys[i]:
            colorPalette[keys[i]] = testColor
            continue
        elif 'Light Off' in keys[i]:
            colorPalette[keys[i]] = 'k'
            continue
        elif keys[i] == 'F':
            colorPalette[keys[i]] = 'pink'
            continue
        elif keys[i] == 'M':
            colorPalette[keys[i]] = 'steelblue'
            continue
        elif keys[i] == 'VF':
            colorPalette[keys[i]] = 'violet'
            continue
        else:
            colorPalette[keys[i]] = 'lightgray'
            n += 1
        
    return colorPalette


# %% ../nbs/API/locoPlotters.ipynb 6
def espressoPlotTracking(X, Y, flyName, colorPalette):
    plt.plot(X, Y, linewidth = 0.5, color = colorPalette[flyName])
    # plt.plot([7, 7], [0, 19], linewidth = 0.5, color = 'r')
    # plt.plot([0, 15], [12, 12], linewidth = 0.5, color = 'r')



# %% ../nbs/API/locoPlotters.ipynb 7
def espressoPlotHeatmap(X, Y, flyGenotype, colorPalette):
    import matplotlib.colors as mcolors
    # plt.hist2d(X[~np.isnan(X)],Y[~np.isnan(Y)], bins=[12, 20],cmap=plt.cm.bone, range=np.array([(0, 13), (-1, 18)]), norm=mcolors.PowerNorm(0.6))
    plt.hist2d(X[~np.isnan(X)],Y[~np.isnan(Y)], bins=[12, 20],cmap=plt.cm.bone, range=np.array([(0, 13), (-1, 18)]))


# %% ../nbs/API/locoPlotters.ipynb 8
def espressoPlotMeanHeatmaps(espLocoObj, binSize,row, col, reverseRows, reverseCols, verbose, heatmapCMap, smooth, plotZScore, vmin = None, vmax = None):
    font_dirs = ["/Users/sangyuxu/Library/Fonts"]
    font_files = font_manager.findSystemFonts(fontpaths=font_dirs)
    for font_file in font_files:
        font_manager.fontManager.addfont(font_file)
    matplotlib.font_manager.findSystemFonts(fontpaths=None, fontext='ttf')
    setFont('inter', 8)    
    from mpl_toolkits.axes_grid1.inset_locator import inset_axes
    from astropy.convolution import convolve, Gaussian2DKernel

    XX = espLocoObj.countLogDf.filter(regex = '_X')
    YY = espLocoObj.countLogDf.filter(regex = '_Y')
    XXCorrected = np.zeros(XX.shape)
    YYCorrected = np.zeros(YY.shape)
    meanLPX = np.mean(espLocoObj.portLocationsDf['LeftPortXConv'])
    meanLPY = np.mean(espLocoObj.portLocationsDf['LeftPortYConv'])

    for i in range(XX.shape[1]):
        XXCorrected[:, i]=XX.iloc[:, i]-espLocoObj.portLocationsDf['LeftPortXConvDev'].iloc[i]
        YYCorrected[:, i]=YY.iloc[:, i]-espLocoObj.portLocationsDf['LeftPortYConvDev'].iloc[i]    
    H = []
    xCeil = np.ceil(np.max(np.max(XX)))
    xFloor = np.floor(np.min(np.min(XX)))
    yCeil = np.ceil(np.max(np.max(YY)))
    yFloor = np.floor(np.min(np.min(YY)))
    xedges = np.arange(xFloor, xCeil, binSize)
    yedges = np.arange(yFloor, yCeil, binSize)
    numlist = list(range(0, len(espLocoObj.metaDataDf)))
    smallHeatmapFigs = plt.figure (num = 1, figsize = [5, np.ceil((len(numlist)+1)/5)*0.8])
    n = 1
    for j in numlist:
    #        plotFunc(X.iloc[:, j-1], Y.iloc[:, j-1], flyGenotype, colorPalette)
        # print(str(j) + ' ' + espLocoObj.metaDataDf.Genotype[j])
        X = XXCorrected[:, j]
        Y = YYCorrected[:, j]
        h, xedges, yedges = np.histogram2d(X[~np.isnan(X)], Y[~np.isnan(Y)], bins = [xedges, yedges])
        extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]
        if verbose:
            plt.subplot(np.ceil((len(numlist)+1)/5), 5, n)
            plt.imshow(h.T, extent=extent, origin='lower', cmap = heatmapCMap)
        n += 1
        H.append(h)
    Hall = np.dstack(H)
    Hall = Hall/20 #originally resampled at 50ms, to convert to seconds
    Hall_z = (Hall - Hall.mean())/Hall.std() # compute z-score for each run with whole experiment mean and std
    listOfPlots, gp, custom_palette = subplotRowColColor(espLocoObj.metaDataDf, None, row, col, reverseRows, reverseCols)
    nr, nc = listOfPlots[-1][0][0:2]
    meanHeatmapFig, axes = plt.subplots(nrows=nr + 1, ncols=nc + 1, figsize = (3 * (nc + 1), 4 * (nr + 1)), squeeze = False)
    images = []
    for i in range(0, len(listOfPlots)):
        # print(listOfPlots[i])
        ro, co = listOfPlots[i][0][0:2]
        # print(listOfPlots[i][0][0:2])
        name = listOfPlots[i][1]
        # print(name)
        ind = gp[name]
        Hmean = np.mean(Hall[:, :, ind], axis = 2)
        Hmean_z = np.mean(Hall_z[:, :, ind], axis = 2)
        if plotZScore:
            H = Hmean_z
        else:
            H = Hmean
        if smooth:
            images.append(axes[ro, co].imshow(convolve(H.T, Gaussian2DKernel(x_stddev=smooth, y_stddev=smooth)), extent=extent, origin='lower', cmap = heatmapCMap))
        else:
            images.append(axes[ro, co].imshow(H.T, extent=extent, origin='lower', cmap = heatmapCMap))
        axes[ro, co].set_title(name[0]+ '\n' + name[1])
        axes[ro, co].label_outer()
        setAxesTicks(axes[ro, co], False)
        axes[ro, co].plot([meanLPX-1.5 , meanLPX+1.5], [meanLPY, meanLPY], color = 'y', linewidth = 2)
    # plt.text(10, 16.5, '2 mm', color = 'w', ha = 'center')
    plt.plot([9, 11], [yFloor+0.5, yFloor+0.5], color = 'w', linewidth = 2)
    # left = np.sum(np.sum(Hall[4:9, 21:25, :], axis = 0), axis = 0)
    # right = np.sum(np.sum(Hall[10:15, 21:25, :], axis = 0), axis = 0)
    # bottom = np.sum(np.sum(Hall[4:15, 4:7, :], axis = 0), axis = 0)
    # resultsDf = espLocoObj.resultsDf

    # resultsDf['left'] = left
    # resultsDf['right'] = right
    # resultsDf['bottom'] = bottom
    # resultsDf['LR Preference'] = (resultsDf['left']- resultsDf['right'])/ (resultsDf['right']+resultsDf['left'])
    # resultsDf['TB Preference'] = (resultsDf['right'] + resultsDf['left'] - resultsDf['bottom'])/ (resultsDf['bottom']+resultsDf['right']+resultsDf['left'])
    if vmin == None:
        vmin = min(image.get_array().min() for image in images)
    if vmax == None:
        vmax = max(image.get_array().max() for image in images)
#     norm = colors.Normalize(vmin=vmin, vmax=vmax)
#     for im in images:
#         im.set_norm(norm)
    # axins = inset_axes(axes[-1, -1],
    #                width="5%",  # width = 5% of parent_bbox width
    #                height="100%",  # height : 50%
    #                location = 'left',  
    #                # orientation = 'horizontal',
    #                # bbox_to_anchor=(1.05, 0., 1, 1),
    #                # bbox_transform=axes[-1, -1].transAxes,
    #                borderpad=0,
    #                )
    # from mpl_toolkits.axes_grid1 import make_axes_locatable

    # divider = make_axes_locatable(axes[-1, -1])
    # cax = divider.new_vertical(size='5%', pad=0.1, pack_start = True)
    # meanHeatmapFig.add_axes(cax)
    cax = meanHeatmapFig.add_axes([axes[0, 0].get_position().x0, 0.08, axes[-1, -1].get_position().x1-axes[0, 0].get_position().x0, 0.02])
    # meanHeatmapFig.colorbar(images[-1], cax=axins, ticks=[0, 5, 10, 15, 20])
    class ImageFollower(object):
        'update image in response to changes in clim or cmap on another image'

        def __init__(self, follower):
            self.follower = follower

        def __call__(self, leader):
            self.follower.set_cmap(leader.get_cmap())
            self.follower.set_clim(leader.get_clim())

    norm = colors.Normalize(vmin=vmin, vmax=vmax)
    for i, im in enumerate(images):
        im.set_norm(norm)
        if i > 0:
            images[0].callbacksSM.connect('changed', ImageFollower(im))
    meanHeatmapFig.colorbar(images[-1], cax=cax, orientation = 'horizontal')
    plt.show()
    meanHeatmapFileName = 'meanHeatmapFig'+ '_' + str(col) + '_' + str(row) + str(espLocoObj.startMin) + '-' + str(espLocoObj.endMin) + 'min'
    locoUtilities.espressoSaveFig(meanHeatmapFig, meanHeatmapFileName, espLocoObj.metaDataDf.Date[0], espLocoObj.outputFolder)
    # locoUtilities.espressoWriteDictToCSV(espLocoObj.outputFolder+meanHeatmapFileName+'_ConditionsTable.csv', gp)
    if verbose:
        return meanHeatmapFig, H, images, smallHeatmapFigs
    else:
        return meanHeatmapFig, H, images


# %% ../nbs/API/locoPlotters.ipynb 9
def plotBoundedLine(x, Y, ax=None, c = 'k', resamplePeriod = '200s', aggMethod = 'mean', label = ''):
    font_dirs = ["/Users/sangyuxu/Library/Fonts"]
    font_files = font_manager.findSystemFonts(fontpaths=font_dirs)
    for font_file in font_files:
        font_manager.fontManager.addfont(font_file)
    matplotlib.font_manager.findSystemFonts(fontpaths=None, fontext='ttf')
    setFont('inter', 8)    
    if ax is None:
        ax = plt.gca()
    if resamplePeriod:
        if aggMethod == 'mean':
            Y = Y.resample(resamplePeriod).agg(np.mean)
        elif aggMethod == 'sum':
            Y = Y.resample(resamplePeriod).agg(np.sum)
        x = x.resample(resamplePeriod).agg(np.mean)
    y = np.nanmean(Y, axis = 1)
    ci = np.nanstd(Y, axis = 1)/(np.sqrt(Y.shape[1]))*1.96
    ax.meanLine = ax.plot(x, y, color = c, label = label)
    ax.ciBound =  ax.fill_between(x, y+ci,  y-ci, color = c, alpha=0.2, label='_nolegend_')
    setAxesTicks(ax, True, gridState = False)
    return(ax)



# %% ../nbs/API/locoPlotters.ipynb 10
def putThingsInToChamberSubplot(countLogDf, metaDataDf, portLocationsDf, customPalette, ncol, plotFunc = espressoPlotTracking,   showID = False):
    noOfRows=int(np.ceil(len(metaDataDf)/ncol))
    chamberSmalls, axarr = plt.subplots(noOfRows, ncol, figsize = [ncol/1.5, noOfRows])
    metaDataDf = metaDataDf.reset_index()
    portLocationsDf = portLocationsDf.reset_index()
    
    for j in metaDataDf.index:
        id = metaDataDf.loc[j, 'ID']
        col = np.mod(id-1, ncol)
        row = int((id - col)/ncol)
        chamberSmalls.sca(axarr[row, col])
        if customPalette:
            colorPalette = customPalette
        else:
            colorPalette = espressoCreatePalette(metaDataDf['Genotype'])
        flyGenotype = metaDataDf['Genotype'][j]
        X = countLogDf.filter(regex = '_X')
        Y = countLogDf.filter(regex = '_Y')
#        plotFunc(X.iloc[:, j-1], Y.iloc[:, j-1], flyGenotype, colorPalette)
        # print(colorPalette)
        plotFunc(X.iloc[:, j], Y.iloc[:, j], flyGenotype, colorPalette)
#        axarr[row, col].set_title(flyGenotype)
        plotChamber(portLocationsDf.iloc[j], axarr[row, col])
        if showID:
            plt.title(metaDataDf.loc[j, 'ID'])
    chamberSmalls.suptitle(metaDataDf.loc[0, 'Date'] + ' ' + str(metaDataDf.loc[0, 'Temperature']) )
    chamberSmalls.tight_layout()
    chamberSmalls.subplots_adjust(
                    wspace=0.02, 
                    hspace=0.0001)

    for row in range(0, axarr.shape[0]):
        for col in range(0, axarr.shape[1]):
            espressoChamberStyling(axarr[row, col])
    return chamberSmalls
#


# %% ../nbs/API/locoPlotters.ipynb 11
def plotChamber(ploc, ax):
    chamberLeft = ploc.ChamberLeftConv        
    chamberRight = ploc.ChamberRightConv                      
    chamberTop = ploc.ChamberTopConv                      
    chamberBottom = ploc.ChamberBottomConv                      
    leftPortX = ploc.LeftPortXConv
    leftPortY = ploc.LeftPortYConv
    rightPortX = ploc.RightPortXConv
    rightPortY = ploc.RightPortYConv
    rectangle = [(chamberLeft, chamberTop), (chamberRight, chamberTop), (chamberRight, chamberBottom), (chamberLeft, chamberBottom)]
    ax.plot(*zip(*(rectangle+rectangle[:1])), 'lightgray', linewidth = 0.2)
    ax.axis('equal')
    if ploc.LeftPortEnabled:
        ll, = ax.plot([leftPortX - 1.5, leftPortX + 1.5], [leftPortY, leftPortY], 'seagreen', linewidth = 0.3, alpha = 0.3, )
        ll.set_solid_capstyle('round')

    if ploc.RightPortEnabled:
        lr, = ax.plot([rightPortX - 1.5, rightPortX + 1.5], [rightPortY, rightPortY], 'seagreen', linewidth = 0.3, alpha = 0.3, )
        lr.set_solid_capstyle('round')
    # return ax, ((leftPortX, leftPortY), (rightPortX, rightPortY))
    return 



# %% ../nbs/API/locoPlotters.ipynb 12
def subplotRowColColor(metaDataDf, colorBy, row, col, reverseRows, reverseCols):
    m = metaDataDf
    m = m.applymap(str)
    if row == None:
        m['row'] = ' '
        row = 'row'
    if col == None:
        m['col'] = ' '
        col = 'col'
    if colorBy == None:
        m['colorBy'] = ' '
        colorBy = 'colorBy'
    gp = m.groupby([row, col, colorBy]).groups
    testGenotypeColor = 'lakeblue'
    if m.Status.str.contains('Test').sum()>0:
        testGenotypeName = np.unique(m.loc[m['Status'] == 'Test', 'Genotype'])[0]
        if 'chrimson' in testGenotypeName or 'csch' in testGenotypeName:
            testGenotypeColor = 'crimson'
        elif 'acr' in testGenotypeName:
            testGenotypeColor = 'cyan'
        elif 'tetx' in testGenotypeName:
            testGenotypeColor = 'eggplant'
        elif 'cas' and 'ms' in testGenotypeName:
            testGenotypeColor = 'cyan'
    custom_palette = espressoCreatePalette(m[colorBy], testColor = testGenotypeColor)
    if row == 'Temperature':
        uniqueRows = np.sort(np.unique(m[row]))
    else:
        uniqueRows = np.sort(np.unique(m[row]))[::-1]
    w1118InUniqueRows = ['w1118' not in uniqueRows[i] for i in range(len(uniqueRows))]
    newind = np.argsort(w1118InUniqueRows)
    uniqueRows = uniqueRows[newind]
    if col == 'Temperature':
        uniqueCols = np.sort(np.unique(m[col]))
    else:
        uniqueCols = np.sort(np.unique(m[col]))[::-1]

    w1118InUniqueCols = ['w1118' not in uniqueCols[i] for i in range(len(uniqueCols))]
    newind = np.argsort(w1118InUniqueCols)
    uniqueCols = uniqueCols[newind]
    if colorBy == 'Temperature':
        uniqueColors = np.sort(np.unique(m[colorBy]))
    else:
        uniqueColors = np.sort(np.unique(m[colorBy]))[::-1]
    w1118InUniqueColors = ['w1118' not in uniqueColors[i] for i in range(len(uniqueColors))]
    newind = np.argsort(w1118InUniqueColors)
    uniqueColors = uniqueColors[newind]
    if reverseRows:
        uniqueRows = uniqueRows[::-1]
    if reverseCols:
        uniqueCols = uniqueCols[::-1]

    listOfPlotsUnfiltered = [((i, j, k), (r, c, cl)) for i, r in enumerate(uniqueRows) for j, c in enumerate(uniqueCols) for k, cl in enumerate(uniqueColors)]
    listOfPlots = [i for i in listOfPlotsUnfiltered if i[1] in gp.keys()]
    return listOfPlots, gp, custom_palette

# %% ../nbs/API/locoPlotters.ipynb 13
def plotPeriFeedDiagonal(locoObj, monitorWindow):
    print('plotting PeriFeedDiagonal')

    PeriFeedDiagonal = plt.figure(figsize=(5, 5))
    plt.plot([0, locoObj.maxSpeed], [0, locoObj.maxSpeed], 'lightgray')
    plt.plot(locoObj.meanPeriSpeed['MeanSpeed'+str(monitorWindow)+'sBeforeFeed_mm/s'],
             locoObj.meanPeriSpeed['MeanSpeedDuringFeed_mm/s'], '.', c='steelblue', label='Speed during feed')
    plt.plot(locoObj.meanPeriSpeed['MeanSpeed'+str(monitorWindow)+'sBeforeFeed_mm/s'], locoObj.meanPeriSpeed['MeanSpeed'+str(monitorWindow)+'sAfterFeed_mm/s'], '.', c='orangered', label='Speed ' + locoObj.monitorMin + ' after feed')
    plt.xlabel('Speed Before Feed (mm/s)')
    plt.xlim(0, locoObj.maxSpeed)
    plt.ylim(0, locoObj.maxSpeed)
    plt.legend()
    locoUtilities.espressoSaveFig(
        PeriFeedDiagonal, locoObj.monitorMin+'PeriFeedDiagonal', locoObj.metaDataDf.Date[0], locoObj.outputFolder)
    return PeriFeedDiagonal


# %% ../nbs/API/locoPlotters.ipynb 14
def plotPairedSpeeds(locoObj, monitorWindow):
    print('plotting pairedSpeedPlots')

    speedMatrix = locoObj.resultsDf[['ChamberID', 'Genotype', 'Status', 'Temperature',
                                     'MeanSpeed'+str(monitorWindow)+'sBeforeFeed_mm/s', 
                                     'MeanSpeedDuringFeed_mm/s', 'MeanSpeed'+str(monitorWindow)+'sAfterFeed_mm/s']]
    speedMatrix = speedMatrix.rename(columns={'MeanSpeed'+str(monitorWindow)+'sBeforeFeed_mm/s': "Before",
                  'MeanSpeedDuringFeed_mm/s': "During", 'MeanSpeed'+str(monitorWindow)+'sAfterFeed_mm/s': 'After'})
    
    speedMatrixMelted = speedMatrix.melt(id_vars=['ChamberID', 'Genotype', 'Status', 'Temperature'],
                value_vars=[
     'Before', 'During', 'After'],
     var_name='SpeedEpoch', value_name='Speed')
    noOfGenotypes = len(speedMatrix.Genotype.unique())
    noOfTemperature = len(speedMatrix.Temperature.unique())
    dabestVersion = locoUtilities.checkDabestVersion()
    if dabestVersion <= 0.39:
        _speedCompareFig, _axes = plt.subplots(noOfTemperature, noOfGenotypes*2)
        speedCompare = np.empty((noOfTemperature, noOfGenotypes*2), dtype=object)
        for i in range(0, noOfTemperature):
            for j in range(0, noOfGenotypes):
                geno = speedMatrix.Genotype.unique()[j]
                temp = speedMatrix.Temperature.unique()[i]
                speedMatrix1 = speedMatrix.loc[(speedMatrix.Genotype == geno) & (speedMatrix.Temperature == temp)]
                
                speedCompare[i, 2*j] = dabest.load(speedMatrix1, idx=('Before', 'During'),
                                                        paired=True, id_col='ChamberID')
                speedCompare[i, 2*j].mean_diff.plot(ax = _axes[i, 2*j],
                    swarm_label=('Average Speed (mm/s)'), float_contrast = False)
                speedCompare[i, 2*j+1] = dabest.load(speedMatrix1, idx=('Before', 'After'),
                                                        paired=True, id_col='ChamberID')
                speedCompare[i, 2*j+1].mean_diff.plot(ax = _axes[i, 2*j+1],
                    swarm_label=('Average Speed (mm/s)'), float_contrast = False)

    else:
        _speedCompareFig, _axes = plt.subplots(noOfTemperature, noOfGenotypes)
        speedCompare = np.empty((noOfTemperature, noOfGenotypes), dtype=object)
        for i in range(0, noOfTemperature):
            for j in range(0, noOfGenotypes):
                geno = speedMatrixMelted.Genotype.unique()[j]
                temp = speedMatrixMelted.Temperature.unique()[i]
                speedMatrix1 = speedMatrixMelted.loc[(speedMatrixMelted.Genotype == geno) & (speedMatrixMelted.Temperature == temp)]
                speedCompare[i, j] = dabest.load(data=speedMatrix1,
                                                id_col='ChamberID',
                                                y='Speed',
                                                x='SpeedEpoch',
                                                idx=tuple(
                                                    speedMatrix1['SpeedEpoch'].unique()),
                                                paired='baseline')
                speedCompare[i, j].mean_diff.plot(ax=_axes[i, j])
    swarmRange = [_axes[i, j].get_ylim()
                    for i in range(0, len(_axes)) for j in range(0, len(_axes[0]))]
    contrastRange = [_axes[i, j].contrast_axes.get_ylim(
              ) for i in range(0, len(_axes)) for j in range(0, len(_axes[0]))]
    plt.close()
    
    speedCompareFig, axes = plt.subplots(len(_axes), len(_axes[0]))

    for i in range(0, len(_axes)):
        for j in range(0, len(_axes[0])):
            speedCompare[i, j].mean_diff.plot(ax=axes[i, j], swarm_ylim=(np.min(swarmRange), np.max(swarmRange)),
                                         contrast_ylim=(np.min(contrastRange), np.max(contrastRange)),color_col = 'Temperature', float_contrast = False)
            if dabestVersion <=0.39:
                if np.mod(j, 2)==0:
                    axes[i, j].set_title(speedMatrix.Genotype.unique()[int(np.floor(j/2))-1])

            else:    
                axes[i, j].set_title(speedMatrix.Genotype.unique()[j])
            if j != len(axes[0])-1:
                axes[i, j].get_legend().remove()
    if dabestVersion <= 0.39:
        speedCompareFig.set_size_inches(8*(i+1), 2*(j+1))
    else:
        speedCompareFig.set_size_inches(7*(i+1), 4*(j+1))
    locoUtilities.espressoSaveFig(speedCompareFig, locoObj.monitorMin +
                                      'periFeedPairedSpeed', locoObj.metaDataDf.Date[0], locoObj.outputFolder)

    return speedCompareFig, speedCompare
        
        #return speedMatrix, speedCompare, speedCompareFig
 #       speedMatrix, speedCompare, speedCompareFig = plotPerifeedSpeed(
    #        locoObj)
     #   return locoObj.meanPeriSpeed, speedMatrix, speedCompare, speedCompareFig

    
    
    

# %% ../nbs/API/locoPlotters.ipynb 15
def createWesAndersonPalette():
        
    import seaborn as sns
    import numpy as np

    wes_colors = {}
    wes_colors['lightgray'] = np.divide([110, 100, 102], 255)
    wes_colors['orange'] = np.divide([230, 82,  15], 255)
    wes_colors['cyan'] = np.divide([73, 186,  186], 255)
    wes_colors['crimson'] = np.divide([173, 9,  16], 255)
    wes_colors['ocre'] = np.divide([249, 166,  0], 255)
    wes_colors['darkgray'] = np.divide([55, 57,  61], 255)
    wes_colors['hotpink'] = np.divide([210, 78, 130], 255)
    wes_colors['lakeblue'] = np.divide([82, 150, 228], 255)
    wes_colors['eggplant'] = np.divide([120, 43, 102], 255)
    wes_colors['verde'] = np.divide([74, 104, 41], 255)
    wes_colors['chocolate'] = np.divide([65, 20, 17], 255)
    wes_colors['midnight'] = np.divide([10, 42,  87], 255)
    wes_colors['brick'] = np.divide([235, 59, 32], 255)
    wes_colors['black'] = np.divide([12, 13, 24], 255)
    wes_palette = tuple(map(tuple, wes_colors.values()))
    # sns.palplot(wes_palette)
    return wes_palette, wes_colors

# %% ../nbs/API/locoPlotters.ipynb 16
def setAxesTicks(ax, axesState, gridState = False):
    if axesState == False:
        ax.set_xticks([])
        ax.set_xticklabels([])
        ax.set_yticks([])
        ax.set_yticklabels([])
    
    if gridState == False:
        ax.grid(None)

