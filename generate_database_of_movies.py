# -*- coding: utf-8 -*-
"""
Created on Mon Mar 11 10:53:53 2019

@author: Sam Purkiss
"""

import pandas as pd
import os
os.chdir("C:/Users/sam purkiss/Documents/Code/IMDB")
from get_rating_data import get_rating_data, generate_imdb_master_list

""""This program generates a full list of movies
"""


#Get imdb titles database 
movie_master_list =generate_imdb_master_list(min_no_of_votes = 2500, film_type = 'movie')
#Generate database to hold imdb data
movie_database = pd.DataFrame()

for i in movie_master_list['tconst'].iloc[0:len(movie_master_list)-1]:
    identifier = i
    print('Now on %s' %movie_master_list[movie_master_list['tconst']== identifier]['primaryTitle'].iloc[0])   
    row = get_rating_data(identifier, movie_master_list, no_of_ratings_threshold = 0)
    movie_database = pd.concat([movie_database, row], join = 'outer', sort= False)
    print('Only %d left to go.' %(len(movie_master_list)-len(movie_database)-1))
  
    
#Add additional columns to database    
movie_database['gender_ratings'] = movie_database['no_of_male_ratings']+movie_database['no_of_female_ratings']
movie_database['ratings_differential'] = movie_database['males']- movie_database['females']

movie_database = pd.merge(movie_database, movie_master_list, how = 'left', left_on = 'id', right_on= 'tconst')