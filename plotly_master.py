# -*- coding: utf-8 -*-
"""
Created on Thu Jan  3 11:50:07 2019

@author: Sam Purkiss
"""



import pandas as pd
import numpy as np
import plotly.plotly as py
import plotly.graph_objs as go
from scipy import stats

import os
#os.chdir("C:/Users/sam purkiss/Documents/Code/IMDB")
from get_rating_data import get_rating_data, generate_imdb_master_list

#Get imdb titles database
movie_master_list =generate_imdb_master_list(min_no_of_votes = 250000, film_type = 'movie', release_year = 1940)
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

movie_database = pd.merge(movie_database, ratings_database, how = 'left', left_on = 'id', right_on= 'tconst')

#Save database
movie_database.to_csv(path_or_buf = 'C:/Users/sam purkiss/Documents/Code/IMDB/movie_ratings.csv')

###############################################
#Plotly Charts
###############################################
#Get graph showing movie ratings by proportion all in a cluster
#x-values are mens rating, y-values are womans ratings
###############################################

hover_text =[]
for i in range(0,len(movie_graph_data)):
    hover_text.append(('Movie: {movie}<br>'+
                       'Release date: {date}<br>'+
                       'Genre: {genre}').format(
                               movie = movie_graph_data['name'].iloc[i],
                               date = movie_graph_data['year'].iloc[i],
                               genre=movie_graph_data['genre'].iloc[i]))


traces =[]
for i in range(1,11):
    trace0 =go.Scatter(x = movie_graph_data['male_rating_'+str(i)]/movie_graph_data['no_of_male_ratings'],
                   y = movie_graph_data['female_rating_'+str(i)]/movie_graph_data['no_of_female_ratings'],
                   mode = 'markers',
                   text = hover_text,
                   name = str(i)+' stars')
    traces.append(trace0)


?pd.read_excel

dissecting_line = go.Scatter(x =[0,2],
                            y = [0,2],
                            mode = 'lines',
                            name = 'Intersecting Line',
                            marker = dict(color = 'rgba(106,114,119,0.5)'))
traces.append(dissecting_line)

layout = go.Layout(title = 'Movie Ratings by Gender Proportion',
                   hovermode = 'closest',
                   showlegend = True,
                   xaxis = dict(title = 'Males',
                                range=[0, 1]),
                   yaxis = dict(title = 'Females',
                                range=[0, 1]))
fig = go.Figure(data = traces, layout = layout)

py.iplot(fig, filename='movie-ratings-by-gender')


###############################################
#Given proportion of male raters, what's the average rating?

slope, intercept, rvalue, pvalue, stdderr = stats.linregress(movie_graph_data['no_of_female_ratings']/movie_graph_data['gender_ratings'],
                  movie_graph_data['averageRating'])
xvalues = np.linspace(0,1,4)
yvalues = intercept + slope*xvalues

size = movie_graph_data['gross_worldwide'].replace('NaN', 0)

hover_text =[]
for i in range(0, len(movie_graph_data)):
    hover_text.append(('Movie: {movie}<br>'+
                       'Release date: {date}<br>'+
                       'Worldwide gross: {worldwide_gross}'
                       ).format(movie = movie_graph_data['name'].iloc[i],
                                  date = movie_graph_data['year'].iloc[i],
                                 worldwide_gross = (size.iloc[i] if size.iloc[i] !=0 else 'N/A')))

trace_prop = go.Scatter(x = movie_graph_data['no_of_female_ratings']/movie_graph_data['no_of_male_ratings'],
                    y = movie_graph_data['females'],
                    mode = 'markers',
                    text = hover_text,
                    marker = dict(size = size,
                                  sizemode ='area',
                                  sizeref = 2.*max(size)/(40.**2),
                                  sizemin = 4,
                                  line = dict(color='rgba(0,43,87)')),
                    name = 'Female Ratings')
                    

#trace_reg = go.Scatter(x = xvalues,
#                       y = yvalues,
#                       name = 'Trend Line',
#                       mode = 'lines')

layout = go.Layout(title = 'Movie Ratings by Gender Proportion',
                   hovermode = 'closest',
                   showlegend = False,
                   xaxis = dict(title = 'Proportion of Total Female Ratings to Total Male Ratings',
                                range=[0, 2]),
                   yaxis = dict(title = 'Rating',
                                range=[0, 10]))



fig = go.Figure(data = [trace_prop], layout = layout)

py.iplot(fig, filename = 'movie-ratings-by-gender-proportions')



###########################################################
#Test to see a negative relationship between rating women give and rating men give
###########################################################


trace =[]
for i in range(1, 11):
    trace0 = go.Scatter(x = movie_graph_data['male_rating_'+str(i)]/movie_graph_data['no_of_male_ratings'],
                        y = movie_graph_data['female_rating_'+str(11-i)]/movie_graph_data['no_of_female_ratings'],
                        text= movie_graph_data['name'],
                        mode = 'markers',
                        name = ('Male rating: %d<br> Female rating %d' %(i, 11-i)))
    trace.append(trace0)
    
layout = go.Layout(title = 'Inverse Movie Ratings by Gender Proportion',
                   hovermode = 'closest',
                   showlegend = True,
                   xaxis = dict(title = 'Male Rating',
                                range=[0, 1]),
                   yaxis = dict(title = 'Female Rating',
                                range=[0, 1]))

fig = go.Figure(data = trace, layout = layout)
py.iplot(fig, filename = 'inverse-ratings-by-gender')


###########################################################
#Distribution of women rating movies vs. men
###########################################################

x0 = movie_graph_data['no_of_female_ratings']/movie_graph_data['gender_ratings']
data = go.Histogram(x = x0)

layout = go.Layout(xaxis = dict(title = 'Proportion of Female Raters',
                                range = [0,1]))

fig = go.Figure(data = [data], layout = layout)

py.iplot(fig, filename='proportion-of-female-raters')

###########################################################
#Rating differentials between women and men
###########################################################


test = movie_graph_data[['no_of_female_ratings','gender_ratings','ratings_differential']]
test['proportion'] = (test['no_of_female_ratings']/test['gender_ratings']/5).round(2)*5
test = test.groupby(['proportion'])[['proportion','ratings_differential']].agg(['mean','count'])
test['films'] = ['Number of films: ' + str(test['proportion']['count'].iloc[i]) for i in range(0,len(test))]

trace = go.Scatter(x = test['proportion']['mean'],
                   y = test['ratings_differential']['mean'],
                   mode = 'lines',
                   text = test['films'],
                   name = '')

layout = go.Layout(title = 'Ratings differential by proportion of female raters',
                   showlegend = False,
                    xaxis = dict(title = 'Proportion of Female Raters',
                                 range=[0, .75]),
                       yaxis = dict(title = 'Ratings differential',
                    range=[-2, 2]))
                    
fig= go.Figure(data = [trace], layout = layout)

py.iplot(fig, filename = 'ratings-differentials-female')


###########################################################
#Box office returns for female rated movies
###########################################################


trace = go.Scatter(x = movie_graph_data['no_of_female_ratings']/movie_graph_data['gender_ratings'],
                   y = movie_graph_data['gross_worldwide'],
                   mode = 'markers',
                   text = movie_graph_data['name'],
                   name = '')

layout = go.Layout(title = 'Ratings differential by proportion of female raters',
                   showlegend = False,
                   hovermode = 'closest',
                    xaxis = dict(title = 'Proportion of Female Raters',
                                 range=[0, .75]),
                       yaxis = dict(title = 'Ratings differential'))
                    
fig= go.Figure(data = [trace], layout = layout)

py.iplot(fig, filename = 'box-office-revenue-female')


###########################################################
#Ratings histogram
###########################################################

ratings = movie_graph_data[['male_rating_10', 'male_rating_9', 'male_rating_8', 'male_rating_7',
       'male_rating_6', 'male_rating_5', 'male_rating_4', 'male_rating_3',
       'male_rating_2', 'male_rating_1', 'female_rating_10', 'female_rating_9',
       'female_rating_8', 'female_rating_7', 'female_rating_6',
       'female_rating_5', 'female_rating_4', 'female_rating_3',
       'female_rating_2', 'female_rating_1']].aggregate(sum)
ratings = pd.DataFrame(ratings)
ratings.reset_index( inplace=True)
ratings = ratings.rename(columns={'index':'type',0:'number'})

rating_range = []
for i in range(10, 0, -1):
    rating_range.append(i)

trace = go.Bar(x = rating_range,
                     y = ratings['number'].iloc[0:9]/sum(ratings['number'].iloc[0:9]),
                     name = "Mens")
trace2 = go.Bar(x = rating_range,
                     y = ratings['number'].iloc[10:19]/sum(ratings['number'].iloc[10:19]),
                     name = "Womens")
    
layout = go.Layout(title='Ratings distribution by gender') 
    
fig = go.Figure(data = [trace, trace2], layout=layout)
py.iplot(fig, filename = 'rating-distribution')


















