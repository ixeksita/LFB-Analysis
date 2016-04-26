# -*- coding: utf-8 -*-
"""
Created on Mon Apr 25 18:08:03 2016

@author: mbgnkts2
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mpl_colors
from mpl_toolkits.basemap import Basemap
from matplotlib.patches import Rectangle
import brewer2mpl as b2mpl
import numpy as np
from scipy.stats import itemfreq

#Create a dataframe to save the position of the fires
BNG=pd.DataFrame()
BNG['East']= fire.Easting_rounded
BNG['North']=fire.Northing_rounded
BNG.to_csv('BNG.csv', sep=',', lineterminator='\n', index=None, low_memory=True)


#now need to convert those BNG to latitude and longitude
execfile('BNGlatlon.py')

#Import data LFB
dateparse = (lambda x: pd.to_datetime(x, format='%d-%b-%y'))
fire=pd.read_csv('LFB.csv', parse_dates=['DateOfCall'], 
               date_parser=dateparse)
               
#Import csv file with the coordinates in latitude and longitude
coord=pd.read_csv('BNGandLAtLon.csv')

#Add the coordinates to the fire DataFrame
fire['Y']=coord.Lat
fire['X']=coord.Lon

#remove any outliers
fire= fire[fire.X>-2]
fire=fire[fire.Y<51.8]

#find mapping boundaries
maxLon=fire.Y.max()
minLon=fire.Y.min()
maxLat=fire.X.max()
minLat=fire.X.min()

#Obtaining the map
def get_map():
    map_extent = [minLat, minLon, maxLat, maxLon]
    map_extent= [50.96, -2.36, 52.16, 0.9022]
    m = Basemap(llcrnrlon=map_extent[1], llcrnrlat=map_extent[0],
                urcrnrlon=map_extent[3], urcrnrlat=map_extent[2],
                resolution='f', epsg=4269)
    return m


def generate_plots(df, m, bin_size, min_bins):
    # Map-related info
    longitudes = np.arange(minLon, maxLon, 0.25)
    latitudes = np.arange(minLat, maxLat, 0.1)

    #some relevant quatities
    
    categs = pd.Series(sorted(df['PropertyType'].unique()))
    n_categs = len(categs)
    n_samples = 1. * len(fire)

    # Posterior mean estimate of category probabilities using Dirichlet prior.
    categ_priors = (df.groupby(['PropertyType']).size() + 1) / (
    n_samples + n_categs)

    # Create the x and y bin edges over which we'll smooth positions.
    # Better approach might be to find optimal bin size through
    # cross validation based approach.
    bin_edges_x = np.arange(np.min(df['X']) - bin_size / 2,
                            np.max(df['X']) + bin_size / 2,
                            bin_size)
    bin_edges_y = np.arange(np.min(df['Y']) - bin_size / 2,
                            np.max(df['Y']) + bin_size / 2,
                            bin_size)
    overall_hist, yedges, xedges, Img = plt.hist2d(
        df.Y.values, df.X.values, bins=(bin_edges_y, bin_edges_x))   
    # We'll assume that fires really only occurs at a location
    # at which we have seen at least one crime over the period comprising 2012-2015.
    
    # This will help with the plotting
    mask = overall_hist == 0
    n_bins = np.sum(overall_hist > 0)
    
    # Obtain the class condition probabilities p(x|y).
    # Essentially we are computing the quantity: given the type of affected property,
    # what is the probability that the fire occurred in a given xy bin.
    # Because a single fire can happen in only one location, we are
    # treating the class conditional densities as multinomial.
    groups = df.groupby(['PropertyType'])
    px_y = np.zeros([len(bin_edges_y) - 1, len(bin_edges_x) - 1, n_categs])
    px_y_ma = np.ma.masked_where(np.tile(np.atleast_3d(mask), [1, 1, n_categs]), px_y)
    for i, (name, group) in enumerate(groups):
        group_hist, yedges, xedges,Img = plt.hist2d(group.Y.values, group.X.values, 
                                                    bins=(bin_edges_y, bin_edges_x))
        group_hist_ma = np.ma.masked_where(mask, group_hist)

        # Posterior mean estimates of class conditonal probabilities
        # using Dirichlet prior.
        px_y_ma[:, :, i] = (group_hist_ma + 1.0) / (
            np.sum(group_hist_ma) + n_bins)
            
    # Put the category prior into the right shape for easy broadcasting.
    p_y = np.atleast_3d(categ_priors.as_matrix()).reshape(1, 1, n_categs)
    p_y = np.tile(p_y, [len(bin_edges_y) - 1, len(bin_edges_x) - 1, 1])
    p_y_ma = np.ma.masked_where(
        np.tile(np.atleast_3d(mask), [1, 1, n_categs]), p_y)

    # Obtain the posterior probabilites of each property type,
    # given that the fire occurred in a known xy location
    py_x_ma = (p_y_ma * px_y_ma) / np.atleast_3d(
        np.sum(p_y_ma * px_y_ma, axis=2))

    # Compute entropy of posterior distribution
    hy = -np.sum(categ_priors * np.log2(categ_priors))
    hy_x = -np.sum(py_x_ma * np.log2(py_x_ma), axis=2)
    entropy_diff = hy - hy_x

    X, Y = np.meshgrid(bin_edges_x, bin_edges_y)

    # Get the property type that maximized the posterior probability.
    winner = np.argmax(py_x_ma, axis=2)
    winner_ma = np.ma.masked_where(mask, winner)

    # How many time does each fire(property type) prove to be the most likely?
    counts = itemfreq(winner_ma[winner_ma.mask == False])

    # Sort the counts and take only those types which have
    # at least min_pop_bins bins in which they were the winner
    sorted_counts = counts[np.argsort(counts[:, 1])[::-1], :]
    top_counts = sorted_counts[sorted_counts[:, 1] >= min_bins, :]
    top_counts_less = top_counts[1:, :]
    
    ####### Plotting preferences  
    
    # m.arcgisimage(service='Canvas/World_Dark_Gray_Base', xpixels=1500)
    plt.figure(figsize=(16,18))    
    m.drawmapboundary(fill_color='aqua')
    m.fillcontinents(color=(0.25, 0.25, 0.25), zorder=0)
    m.drawparallels(latitudes, color='white', labels=[1, 0, 0, 0],
                    dashes=[5, 5], linewidth=.25)
    m.drawmeridians(longitudes, color='white', labels=[0, 0, 0, 1],
                    dashes=[5, 5], linewidth=.25)
                    
    n_colors = top_counts_less.shape[0]
    colors = b2mpl.get_map('BuPu', 'Sequential', n_colors).mpl_colors
    recoded = np.zeros(winner.shape)
    for i, categ_num in enumerate(top_counts[:, 0]):
        recoded[winner == categ_num] = i

    winner_ma = np.ma.masked_where(recoded == 0, recoded)
    m.pcolormesh(X, Y, winner_ma,
                 cmap=mpl_colors.ListedColormap(colors))

    winner_ma = np.ma.masked_where(
        np.logical_or(mask, winner != 16), winner)
    m.pcolormesh(X, Y, winner_ma, cmap='Greys', alpha=0.75, edgecolor='None')

    legend_labels = [categs[i] for i in top_counts[:, 0]]

    # separate way of doing legend for the most common crime, which is not
    # part of the colormap
    legend_markers = []
    legend_markers.append(
        Rectangle((0, 0), 1, 1, fc='white', ec='white'))

    # now the other types
    legend_edgecolors = colors
    legend_facecolors = colors
    for i in range(len(top_counts_less)):
        legend_markers.append(
            Rectangle((0, 0), 1, 1,
                      fc=legend_facecolors[i], ec=legend_edgecolors[i]))
    legend = plt.legend(legend_markers, legend_labels, labelspacing=.075,
                        handlelength=.5, handletextpad=.1,
                        fancybox=True, frameon=1, loc='upper left')
    frame = legend.get_frame()
    frame.set_facecolor('black')

    texts = legend.get_texts()
    texts[0].set_fontsize(10)
    texts[0].set_color('white')
    for t, c in zip(texts[1:], legend_edgecolors):
        t.set_fontsize(14)
        t.set_color(c)

    plt.title("Most likely fire (specified by affected property type) \n"
              "given knowledge of location only,\n"
              "taking into account the prior fire probability\n",
              fontsize=14)
    plt.savefig('Type_output.png')

    #### Entropy difference plot
    plt.figure(figsize=(16,18))

    entropy_diff_ma = np.ma.masked_where(mask, entropy_diff)
    max_diff = np.max(entropy_diff_ma)
    min_diff = np.min(entropy_diff_ma)
    max_abs = np.max([max_diff, np.abs(min_diff)])
    #m.pcolormesh(X, Y, entropy_diff_ma, cmap='BuPu', alpha=0.75,
                 #edgecolor='None', vmin=-max_abs, vmax=max_abs)
    
    #plt.draw()

    # m.arcgisimage(service='Canvas/World_Dark_Gray_Base', xpixels=1500)
    m.drawmapboundary(fill_color='aqua')
    m.fillcontinents(color=(0.25, 0.25, 0.25), zorder=0)
    m.drawparallels(latitudes, color='white', labels=[1, 0, 0, 0],
                    dashes=[5, 5], linewidth=.25)
    m.drawmeridians(longitudes, color='white', labels=[0, 0, 0, 1],
                    dashes=[5, 5], linewidth=.25)
    #m.scatter(fire.X, fire.Y)
    m.pcolormesh(X, Y, entropy_diff_ma, cmap='BuPu', alpha=0.75,
                 edgecolor='None', vmin=-max_abs, vmax=max_abs)
    cbar = plt.colorbar(shrink=0.25)
    cbar.solids.set_edgecolor("face")

    plt.title('Entropy of prior distribution minus entropy of posterior distribution:\n'
              'positive values indicate less uncertainty about fire type '
              'after observing location', fontsize=14)
    plt.savefig('Entropy.png')
