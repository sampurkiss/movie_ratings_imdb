# -*- coding: utf-8 -*-/
"""
Created on Wed Jan  2 18:33:20 2019

@author: Sam Purkiss
"""

import pandas as pd
import os
import plotly
import plotly.plotly as py
import plotly.graph_objs as go
import dash
import dash_core_components as dcc
import dash_html_components as html

os.chdir("C:/Users/sam purkiss/Documents/Code/IMDB")
from get_tv_show_ratings import get_tv_ratings

#############################################
#Set up list of tv series
#titles = pd.read_csv('https://datasets.imdbws.com/title.basics.tsv.gz', sep='\t')
#episodes = pd.read_csv('https://datasets.imdbws.com/title.episode.tsv.gz', sep='\t')
#ratings = pd.read_csv('https://datasets.imdbws.com/title.ratings.tsv.gz', sep = '\t')
##Ensure there's actually 1 or more seasons. Avoids cases where 
##only a pilot was released
#episodes = episodes[episodes['seasonNumber'] !='\\N'].groupby(['parentTconst'])['seasonNumber'].max().reset_index()
#titles = titles[['tconst','titleType','primaryTitle','originalTitle','startYear','endYear']]
##Narrow database down to only tvSeries
#titles = titles[titles['titleType']=='tvSeries']
#titles = pd.merge(titles, episodes, how='inner',left_on = 'tconst', right_on = 'parentTconst')
#titles = pd.merge(titles, ratings, how = 'left', on = 'tconst')
#Filter out any shows with no ratings from people
#titles = titles[titles['numVotes']>0]
#titles.to_csv(path_or_buf='tv_show_database.csv')
##############################################

titles = pd.read_csv('tv_show_database.csv')
show = get_tv_ratings(show_name= "Seinfeld", titles_data_frame = titles)
data_table, averages = show.get_rating_data()
list_text = titles[['primaryTitle','startYear','tconst']].sort_values(by='primaryTitle')
#show.plot_ratings()


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"})


app.layout = html.Div([
    html.Div([html.Label('Dropdown menu'),
                dcc.Dropdown(id='show-identifier',
                    options = [
                        {'label': list_text['primaryTitle'].iloc[i].title()+', '+list_text['startYear'].iloc[i],
                         'value': list_text['tconst'].iloc[i]} for i in range(0,len(titles)-1)],
                            value= 'tt1856010')]),
    dcc.Graph(
    id='tv-show-ratings')    
    ])

######################################
#Change layout given dropdown value
######################################
@app.callback(
        dash.dependencies.Output('tv-show-ratings','figure'),
        [dash.dependencies.Input('show-identifier','value')]
        )

def update_graph(show_identifier_value):
    tv_show = get_tv_ratings(unique_code = show_identifier_value, titles_data_frame = titles)
    data_table, averages = tv_show.get_rating_data()
    show_name = list_text[list_text['tconst']==show_identifier_value]['primaryTitle'].iloc[0]
    hover_text = []
    for i in range(0,len(data_table)):
        hover_text.append(
                ('{episode_number}<br>'+
                '{name}').format(episode_number = data_table['episode_number'].iloc[i],
                                 name = data_table['episode_name'].iloc[i]))            
    
    return {'data': [go.Scatter(
                    x=data_table['season'],
                    y=data_table['ratings'],
                    text=hover_text,
                    mode='markers',
                    opacity=0.7,
                    marker={
                        'size': 7,
                        'line': {'width': 0.5, 
                                 'color': 'white'}
                    },
                    name='Episode'), 
                go.Scatter(
                    x=averages['season'],
                    y=averages['average_rating'],
                    text='Average',
                    mode='lines',
                    opacity=0.7,
                    line={'width':2,
                          'dash': 'longdash',
                        'color': 'red'
                    },
                    name='Average Season Rating')],
                
            'layout': go.Layout(
                    title=show_name.title()+' Episode Ratings',
                xaxis={'title': 'Season',
                       'tickformat':',d'},
                yaxis={'title': 'Rating', 'range':[0,10]},
                showlegend=True,
                hovermode='closest',
            )
        }
    

if __name__ == '__main__':
    app.run_server(debug=True)




