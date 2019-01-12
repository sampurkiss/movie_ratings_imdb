# -*- coding: utf-8 -*-
"""
Created on Thu Jan  3 11:50:07 2019

@author: Sam Purkiss
"""



import pandas as pd
from bs4 import BeautifulSoup
import plotly.plotly as py
import plotly.graph_objs as go
import urllib
import re



titles = pd.read_csv('https://datasets.imdbws.com/title.basics.tsv.gz', sep='\t')
ratings_database = pd.read_csv('https://datasets.imdbws.com/title.ratings.tsv.gz', sep = '\t')

#Add in ratings data
master_list = pd.merge(titles, ratings_database, how = 'left', on = 'tconst')

#Generate database to hold imdb data
movie_database = pd.DataFrame()

for colname in colnames:
    movie_database[colname] = []

different_genres = []
for genre in movie_database['genre']:
    if genre not in different_genres:
        different_genres.append(genre)

#Open previous database
movie_database = pd.read_csv('C:/Users/sam purkiss/Documents/Code/IMDB/movie_ratings.csv')


#Refine list of movies
movie_master_list = master_list[master_list['titleType'] == 'movie']
movie_master_list = movie_master_list[movie_master_list['numVotes']>100000][movie_master_list['numVotes']<250000]

for i in movie_master_list['tconst'].iloc[0:len(movie_master_list)-1]:
    identifier = i
    print('Now on %s' %movie_master_list[movie_master_list['tconst']== identifier]['primaryTitle'].iloc[0])   
    row = get_movie_rating_data(identifier, movie_master_list, no_of_ratings_threshold = 0)
    movie_database = pd.concat([movie_database, row], join = 'outer', sort= False)
    print('Only %d left to go.' %(len(movie_master_list)-len(movie_database)-1))
    
movie_database['gender_ratings'] = movie_database['no_of_male_ratings']+movie_database['no_of_female_ratings']
    
#Save database
movie_database.to_csv(path_or_buf = 'C:/Users/sam purkiss/Documents/Code/IMDB/movie_ratings.csv')


movie_graph_data = movie_database[pd.to_numeric(movie_database['year'])>1940]
#Plotly, x-values are mens rating, y-values are womans ratings
traces =[]
for i in range(1,11):
    trace0 =go.Scatter(x = movie_graph_data['male_rating_'+str(i)]/movie_graph_data['no_of_male_ratings'],
                   y = movie_graph_data['female_rating_'+str(i)]/movie_graph_data['no_of_female_ratings'],
                   mode = 'markers',
                   text = movie_graph_data['name'],
                   name = str(i)+' stars')
    traces.append(trace0)


dissecting_line = go.Scatter(x =[0,10],
                            y = [0,10],
                            mode = 'lines',
                            marker = dict(color = 'rgba(106,114,119,0.5)'))
traces.append(dissecting_line)

layout = go.Layout(title = 'Movie Ratings by Gender',
                   hovermode = 'closest',
                   showlegend = False,
                   xaxis = dict(title = 'Males',
                                range=[0, 10]),
                   yaxis = dict(title = 'Females',
                                range=[0, 10]))
fig = go.Figure(data = traces, layout = layout)

py.iplot(fig, filename='movie-ratings')





def get_movie_rating_data(identifier, movie_master_list=[], no_of_ratings_threshold = 0):
    #Generate a temporary dataframe to hold the movie data in a row
    movie_row = pd.DataFrame()
    
    #Initialize the required urls with the given identifier    
    main_page_url = 'https://www.imdb.com/title/%s/?ref_=nv_mv_dflt_2' %(identifier)
    ratings_page_url = 'https://www.imdb.com/title/%s/ratings?ref_=tt_ov_rt' %(identifier)
    ratings_page_male_url = 'https://www.imdb.com/title/%s/ratings?demo=males' %(identifier)
    ratings_page_female_url = 'https://www.imdb.com/title/%s/ratings?demo=females' %(identifier)
    
    movie_row['id'] = [identifier]
    #From IMDB database, if provided, get additional data
    if movie_master_list != []:
        movie_row['name'] = [movie_master_list[movie_master_list['tconst'] == identifier]['primaryTitle'].iloc[0]]
        movie_row['genre'] = [movie_master_list[movie_master_list['tconst'] == identifier]['genres'].iloc[0]]
        movie_row['year'] = [movie_master_list[movie_master_list['tconst'] == identifier]['startYear'].iloc[0]]
        
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
    if no_of_ratings > no_of_ratings_threshold:    
             
        text_box = main_page_html.select('div .txt-block')
        all_text = []
        for i in text_box:
            all_text.append(i.text)
            
        box_office = []
        location = []
        for i in range(0, len(all_text)-1):
            if re.findall('Gross USA|Cumulative Worldwide',all_text[i]) !=[]:
                location0 = re.findall('\D+(?<=:)', all_text[i])
                location.append(location0[0])
                value = re.findall('(?<=[$])\S+', all_text[i])
                value = int(value[0].replace(',',''))
                box_office.append(value)
        try:        
            movie_row['gross_usa'] = [box_office[0]]
        except IndexError:
            movie_row['gross_usa'] = ['NaN']
        
        try:
            movie_row['gross_worldwide'] = [box_office[1]]      
        except IndexError:
            movie_row['gross_worldwide'] = ['NaN']
        
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
                    no_of_ratings.append(int(line.a.text.replace(',','')))
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
        #Get number of ratings by gender
        no_of_male_ratings = ratings_page_html.find('a', href=('/title/%s/ratings?demo=males'%identifier))
        no_of_female_ratings = ratings_page_html.find('a', href=('/title/%s/ratings?demo=females'%identifier))
        #For cases where rating info does not exist, do not add column.
        #Value will return None if the data isn't found.        
        #Note that sometimes data will exist for one gender and not the other.
        if no_of_male_ratings != None:
            movie_row['no_of_male_ratings'] =[int(no_of_male_ratings.text.replace(',',''))]
        if no_of_female_ratings != None:
            movie_row['no_of_female_ratings'] =[int(no_of_female_ratings.text.replace(',',''))]
        
        #Now get rating data by gender
        #Male rating distribution
        ratings_male = urllib.request.urlopen(ratings_page_male_url)
        ratings_male_html = BeautifulSoup(ratings_male, 'html.parser')
        
        ratings_dist = ratings_male_html.find_all('div', class_='leftAligned')
        ratings_male_dist = []
        for line in ratings_dist:
            if re.match('\d+',line.text) !=None:
                ratings_male_dist.append(int(line.text.replace(',','')))
        #Get column names
        rating_range = range(10,0,-1)
        for i in rating_range:
            movie_row['male_rating_'+str(i)] = [ratings_male_dist[10-i]]
        
        #Female rating distribution
        ratings_female = urllib.request.urlopen(ratings_page_female_url)
        ratings_female_html = BeautifulSoup(ratings_female, 'html.parser')
        
        ratings_dist = ratings_female_html.find_all('div', class_='leftAligned')
        ratings_female_dist = []
        for line in ratings_dist:
            if re.match('\d+',line.text) !=None:
                ratings_female_dist.append(int(line.text.replace(',','')))
        #Get column names
        rating_range = range(10,0,-1)
        for i in rating_range:
            movie_row['female_rating_'+str(i)] = [ratings_female_dist[10-i]]
        
            
    return movie_row




