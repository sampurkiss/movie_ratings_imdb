# -*- coding: utf-8 -*-
"""
Created on Fri May 24 19:40:02 2019

@author: Sam Purkiss
"""


import pandas as pd
import os

os.chdir("C:/Users/sam purkiss/Documents/Code/IMDB")

#############################################
#This sets up a comprehensive list of ratingsfor each tv show episode
#

all_titles = pd.read_csv('https://datasets.imdbws.com/title.basics.tsv.gz', sep='\t')
titles = all_titles 
episodes = pd.read_csv('https://datasets.imdbws.com/title.episode.tsv.gz', sep='\t')
ratings = pd.read_csv('https://datasets.imdbws.com/title.ratings.tsv.gz', sep = '\t')

#Restrict titles to only tv shows that have total ratings of 500 plus
#and create database of all the different shows
tv_show_names = titles[titles['titleType']=='tvSeries'].copy()
tv_show_min_ratings= ratings.loc[ratings['numVotes']>500]
tv_show_names = tv_show_names.merge(tv_show_min_ratings, how ='inner', on = 'tconst')
tv_show_names = tv_show_names[['tconst','primaryTitle','startYear']]
tv_show_names = tv_show_names.rename(columns = {'tconst':'tvshow_code',
                                                'primaryTitle':'show_name',
                                                'startYear':'show_premier_year'})

#Narrow titles database to just individual episodes
titles = titles.loc[titles['titleType']=='tvEpisode']
#Merge episode data on titles to get get the code for the tv show the episode is from
titles = titles.merge(episodes, how='left', left_on = 'tconst', right_on = 'tconst')

titles= titles.rename(columns = {'primaryTitle':'episode_name',
                                 'tconst':'episode_code',
                                 'parentTconst':'tvshow_code'})
#Merge tv show names on titles to get name of show
titles = titles.merge(tv_show_names, how = 'inner', on ='tvshow_code')

#Finally, merge ratings data to get the rating of each episode
titles = titles.merge(ratings, how = 'inner', left_on ='episode_code', right_on = 'tconst')

#Restrict to specific columns
titles = titles[['tvshow_code','show_name','show_premier_year',
                 'episode_code','episode_name','startYear', 'endYear',
                 'seasonNumber', 'episodeNumber',  
                 'averageRating','numVotes']]

#Filter out any columns in which season doesn't have a number ie '\\N' instead of a number
titles = titles.loc[titles['seasonNumber'] !='\\N']
titles['seasonNumber'] = titles['seasonNumber'].astype(int)

titles.to_csv('episode_rating_database.csv', index =False)
average_season_ratings = titles.groupby(by = ['tvshow_code', 'show_name','seasonNumber']).mean().reset_index()
average_season_ratings.to_csv('average_rating_by_season.csv', index=False)




##############################################
#Old method
#
#
#titles = pd.read_csv('tv_show_database.csv')
#titles = titles.loc[titles['numVotes']>2000]
#
#tv_ratings = pd.DataFrame()
#average_season_ratings = pd.DataFrame()
#length, width = titles.shape
#
#simpsons = 'tt0096697'
#
#show = get_tv_ratings(unique_code = simpsons , titles_data_frame = titles)
#titles[titles['tconst']==simpsons]
#
#
#for i in range(23, length):
#    tconst = titles['tconst'].iloc[i]
#    try:
#        show = get_tv_ratings(unique_code = tconst, titles_data_frame = titles)
#        data_table, averages = show.get_rating_data()
#        tv_ratings = tv_ratings.append(data_table)
#        average_season_ratings.append(averages)
#    except KeyError: 
#        pass
#    if i%50 == 0:
#        print('completed %d out %d' %(i+1, length))
#    
#
##
###############################
#Really old method to just set up a database for the dash app
#episodes = episodes[episodes['seasonNumber'] !='\\N']
#episodes['seasonNumber'] = episodes['seasonNumber'].astype(int)
#episodes = episodes.groupby(by = ['parentTconst'])['seasonNumber'].max().reset_index()
#titles = titles[['tconst','titleType','primaryTitle','originalTitle','startYear','endYear']]
###Narrow database down to only tvSeries
#titles = titles[titles['titleType']=='tvSeries']
#titles = pd.merge(titles, episodes, how='inner',left_on = 'tconst', right_on = 'parentTconst')
#titles = pd.merge(titles, ratings, how = 'left', on = 'tconst')
##Filter out any shows with no ratings from people
#titles = titles[titles['numVotes']>0]
#titles.to_csv(path_or_buf='tv_show_database.csv')
