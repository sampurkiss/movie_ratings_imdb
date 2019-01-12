# -*- coding: utf-8 -*-
"""
Created on Fri Jan  4 16:44:10 2019

@author: Sam Purkiss
"""
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import urllib
import re

def generate_imdb_master_list(min_no_of_votes = 250000, film_type = None, release_year = 1940):
    """
    Generates combined data frame of name and rating data from IMDB.
    Paramaters:
        min_no_of_votes: restricts the list of films to only those with
        at least this many votes.
        film_type: restrict the database to only include entries of this type.
        possible options include: 'short', 'movie', 'tvMovie', 'tvSeries', 
            'tvEpisode', 'tvShort', 'tvMiniSeries','tvSpecial', 'video', 'videoGame'
        
        Returns:
            a dataframe with a list of all imdb entry types. Columns are: 'tconst', 
                'titleType', 'primaryTitle', 'originalTitle', 'isAdult',
                'startYear', 'endYear', 'runtimeMinutes', 'genres', 'averageRating',
                'numVotes'
            """
    titles = pd.read_csv('https://datasets.imdbws.com/title.basics.tsv.gz', sep='\t')
    ratings_database = pd.read_csv('https://datasets.imdbws.com/title.ratings.tsv.gz', sep = '\t')
    
    #Add in ratings data
    master_list = pd.merge(titles, ratings_database, how = 'left', on = 'tconst')
    
 
    #Refine list of movies
    if film_type != None:
            movie_master_list = master_list[master_list['titleType'] == film_type]
    movie_master_list = movie_master_list[movie_master_list['numVotes']>max_no_of_votes]

    return movie_master_list

def get_rating_data(identifier, imdb_master_list, no_of_ratings_threshold = 0):
    """
    Create a dataframe with rating data from IMDB. Includes number of ratings
    and average rating by age group and gender.
    
    Parameters:
        identifier: Unique code from IMDB for each movie/show
        imdb_master_list: a dataframe from IMDB that has names and IDs
            see here for downloads: https://datasets.imdbws.com/
        no_of_ratings_threshold: optional parameter. If included it will
        only return items with a total number of ratings higher than the
        threshold.
        
    Returns:
        movie_row: a single row for the film identified with the following columns:
            ['id', 'name', 'genre', 'year', 'rating', 'no_of_ratings', 'gross_usa',
           'gross_worldwide', 'imdb_users', 'imdb_users_no_of_ratings',
           'aged_under_18', 'aged_under_18_no_of_ratings', 'aged_18_29',
           'aged_18_29_no_of_ratings', 'aged_30_44', 'aged_30_44_no_of_ratings',
           'aged_45_plus', 'aged_45_plus_no_of_ratings', 'males',
           'males_no_of_ratings', 'males_aged_under_18',
           'males_aged_under_18_no_of_ratings', 'males_aged_18_29',
           'males_aged_18_29_no_of_ratings', 'males_aged_30_44',
           'males_aged_30_44_no_of_ratings', 'males_aged_45_plus',
           'males_aged_45_plus_no_of_ratings', 'females', 'females_no_of_ratings',
           'females_aged_under_18', 'females_aged_under_18_no_of_ratings',
           'females_aged_18_29', 'females_aged_18_29_no_of_ratings',
           'females_aged_30_44', 'females_aged_30_44_no_of_ratings',
           'females_aged_45_plus', 'females_aged_45_plus_no_of_ratings',
           'top_1000_voters', 'top_1000_voters_no_of_ratings', 'us_users',
           'us_users_no_of_ratings', 'non_us_users', 'non_us_users_no_of_ratings',
           'no_of_male_ratings', 'no_of_female_ratings', 'male_rating_10',
           'male_rating_9', 'male_rating_8', 'male_rating_7', 'male_rating_6',
           'male_rating_5', 'male_rating_4', 'male_rating_3', 'male_rating_2',
           'male_rating_1', 'female_rating_10', 'female_rating_9',
           'female_rating_8', 'female_rating_7', 'female_rating_6',
           'female_rating_5', 'female_rating_4', 'female_rating_3',
           'female_rating_2', 'female_rating_1']
            
    Example:
        import pandas as pd
        
        identifier = tt5463162 #identifier for Deadpool2
        title_list = pd.read_csv('https://datasets.imdbws.com/title.basics.tsv.gz', sep='\t')
        rating_list = pd.read_csv('https://datasets.imdbws.com/title.ratings.tsv.gz', sep = '\t')
        imdb_master_list = pd.merge(title_list, 
                                    rating_list, 
                                    how = 'left', on = 'tconst')
        movie_row = get_rating_data(identifier, imdb_master_list)
        movie_row.iloc[0]
        
    """
      
    #Generate a temporary dataframe to hold the movie data in a row
    movie_row = pd.DataFrame()
    
    #Initialize the required urls with the given identifier    
    main_page_url = 'https://www.imdb.com/title/%s/?ref_=nv_mv_dflt_2' %(identifier)
    ratings_page_url = 'https://www.imdb.com/title/%s/ratings?ref_=tt_ov_rt' %(identifier)
    ratings_page_male_url = 'https://www.imdb.com/title/%s/ratings?demo=males' %(identifier)
    ratings_page_female_url = 'https://www.imdb.com/title/%s/ratings?demo=females' %(identifier)
    
    movie_row['id'] = [identifier]
    #From IMDB database, if provided, get additional data

    movie_row['name'] = [imdb_master_list[imdb_master_list['tconst'] == identifier]['primaryTitle'].iloc[0]]
    movie_row['genre'] = [imdb_master_list[imdb_master_list['tconst'] == identifier]['genres'].iloc[0]]
    movie_row['year'] = [imdb_master_list[imdb_master_list['tconst'] == identifier]['startYear'].iloc[0]]
    movie_row['rating'] = [imdb_master_list['averageRating']] 
    
    ###################################################
    #Get information from movie's main IMDB page
    ###################################################
    main_page = urllib.request.urlopen(main_page_url)    
    main_page_html = BeautifulSoup(main_page, 'html.parser')
    
   # Get number of people who have rated the movie.
   # Occasionally there is no rating value leading to an IndexError. In that case
   # make the value 0.
    try:
        no_of_ratings = int(main_page_html.find_all(itemprop="ratingCount")[0].text.replace(',',''))
    except IndexError:
        no_of_ratings = 0
    movie_row['no_of_ratings'] = [no_of_ratings]
    #Threshold is included to cut out running function on movies without enough data
    #This saves time by not making the function run through movies that 
    #don't have enough useful data
    #Alternatively, you can filter the IMDB dataset so you only pass IDs with desired
    #number of ratings
    if no_of_ratings > no_of_ratings_threshold:   
        #Selects the box from the IMDB page that has box office amounts, etc...              
        text_box = main_page_html.select('div .txt-block')
        all_text = []
        for i in text_box:
            all_text.append(i.text)
            
        box_office = []
        location = []
        for i in range(0, len(all_text)-1):
            if re.findall('Gross USA|Cumulative Worldwide',
                          all_text[i]) !=[]:
                location0 = re.findall('\D+(?<=:)', 
                                       all_text[i])
                location.append(location0[0])
                value = re.findall('(?<=[$])\S+', 
                                   all_text[i])
                value = int(value[0].replace(',',''))
                box_office.append(value)
        try:        
            movie_row['gross_usa'] = [box_office[0]]
        except IndexError:
            movie_row['gross_usa'] = [np.nan]
        
        try:
            movie_row['gross_worldwide'] = [box_office[1]]      
        except IndexError:
            movie_row['gross_worldwide'] = [np.nan]
        
        ###################################################
        #Get information from movie's rating page
        ###################################################            
        ratings_page = urllib.request.urlopen(ratings_page_url)
        ratings_page_html = BeautifulSoup(ratings_page, 'html.parser')
        
        #From the ratings webpage, select all html from the table
        ratings = ratings_page_html.select('.ratingTable')
        #From the table select the specific element that holds the rating 
        #value and add it to list.
        ratings_list = []
        for line in ratings:
            try:
                ratings_list.append(float(line.select('.bigcell')[0].text))
            except:
                #Need this exception because occasionally no rating exists, 
                #just a dash
                pass
        
        #From the link in each reference, get the rating type
        rating_type =[]
        for line in ratings:
            try:
                rating_type.append(line.a['href'])
            except TypeError:
                #in above case where no rating is provided, 
                #there also isn't an href to refer to
                pass
            
        no_of_ratings = []
        for line in ratings:
            try:
                if line.a != None: #Make sure line isn't blank
                    no_of_ratings.append(
                            int(line.a.text.replace(',',''))
                            )
            except TypeError:
                #in above case where no rating is provided, 
                #there also isn't an href to refer to
                pass
                
        # From the link, get only the rating type text.
        # This is the classification of age and gender combos.
        rating_type = [re.findall('(?<=demo=).+',line)[0] for line in rating_type]
        
        #Add the rating data and colnames to the row dataframe
        for i in range(0,len(ratings_list)):
            try:
                movie_row[rating_type[i]] = [ratings_list[i]]
                movie_row[rating_type[i]+'_no_of_ratings'] = [no_of_ratings[i]]
            except IndexError:
                #In cases where rating isn't provided, the value will be set to 
                #NaN but there will be no column title to refer to. As a result
                #we just need to pass
                pass
        ###################################################
        #Get number of ratings by gender
        no_of_male_ratings = ratings_page_html.find('a', 
                                                    href=('/title/%s/ratings?demo=males'%identifier))
        no_of_female_ratings = ratings_page_html.find('a', 
                                                      href=('/title/%s/ratings?demo=females'%identifier))
        #For cases where rating info does not exist, do not add column.
        #Value will return None if the data isn't found.        
        #Note that sometimes data will exist for one gender and not the other.
        if no_of_male_ratings != None:
            movie_row['no_of_male_ratings'] =[int(no_of_male_ratings.text.replace(',',''))]
        if no_of_female_ratings != None:
            movie_row['no_of_female_ratings'] =[int(no_of_female_ratings.text.replace(',',''))]
        
        ###################################################
        #Now get rating data by gender
        #Get MALE rating distribution
        ratings_male = urllib.request.urlopen(ratings_page_male_url)
        ratings_male_html = BeautifulSoup(ratings_male, 
                                          'html.parser')
        
        ratings_dist = ratings_male_html.find_all('div', 
                                                  class_='leftAligned')
        ratings_male_dist = []
        for line in ratings_dist:
            if re.match('\d+',line.text) !=None:
                ratings_male_dist.append(int(line.text.replace(',','')))
        #Get column names
        rating_range = range(10,0,-1)
        for i in rating_range:
            movie_row['male_rating_'+str(i)] = [ratings_male_dist[10-i]]
        
        #Get FEMALE rating distribution
        ratings_female = urllib.request.urlopen(ratings_page_female_url)
        ratings_female_html = BeautifulSoup(ratings_female, 'html.parser')
        
        ratings_dist = ratings_female_html.find_all('div', 
                                                    class_='leftAligned')
        ratings_female_dist = []
        for line in ratings_dist:
            if re.match('\d+',line.text) !=None:
                ratings_female_dist.append(int(line.text.replace(',','')))
        #Get column names
        rating_range = range(10,0,-1)
        for i in rating_range:
            movie_row['female_rating_'+str(i)] = [ratings_female_dist[10-i]]
        
            
    return movie_row