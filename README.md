# movie_ratings_imdb
Scrapes IMDB ratings data. There are a lot of functions built in for scraping. For example the "get_tv_show_ratings" webscraping component offers many other possibilities if you're curious about individual episodes of any season.

For example, show ratings can be gathered and returned as a data frame as so:  
```
show = get_tv_ratings(show_name= "seinfeld", titles_data_frame = titles)
data_table, averages = show.get_rating_data()
show.get_ratings(data_table, averages)
```
