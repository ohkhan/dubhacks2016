# Uses beautifulsoup4, urllib, json
# Before every commit, do "git pull --rebase"

'''first, get track ids from genre list

create dictionary with key( genre) and value( list of track ids )

for each track, get id, user_id, genre, tag_list
    for the user in the track:
        id, uri, permalink_url, country'''

from bs4 import BeautifulSoup
import urllib.request
import json
import csv as csv

page_url = "http://www.soundcloud.com/charts"
page_html = urllib.request.urlopen( page_url ).read()

page_beautifulsoup_object = BeautifulSoup( page_html, "html.parser" )

page_html_file = open( "html_saved_prettified.html", "w" )
page_html_file.write( page_beautifulsoup_object.body.div.find_all( "noscript" )[ 1 ].section.section.find_all( "article" )[ 1 ].ul.prettify() )

page_beautifulsoup_genres_array = page_beautifulsoup_object.body.div.find_all( "noscript" )[ 1 ].section.section.find_all( "article" )[ 1 ].ul

genre_song_list_length_limit = 100

api_url_chunk_1 = "https://api-v2.soundcloud.com/charts?kind=top&genre=soundcloud%3Agenres%3A"
api_url_chunk_2 = "&client_id=02gUJC0hH2ct1EGOcYXQIzRFU91c72Ea&limit=" + str( genre_song_list_length_limit ) + "&offset=0&linked_partitioning=1&app_version=1476434302"

genre_list = []

iterator = 0
for value in page_beautifulsoup_genres_array:
    if iterator > 3 and iterator % 2 == 1:
        # Reverse search through the HTML to find the first and last indices of the genre name
        genre_string_start_index = repr( value ).rfind( "=" ) + 1
        genre_string_end_index = repr( value ).rfind( "\"" )
        genre_string = repr( value )[ genre_string_start_index : genre_string_end_index ]
        genre_list.append( genre_string )
    iterator = iterator + 1

#f = open("tracks.csv","w")
#f1 = csv.writer(f)
for genre in genre_list:
    json_data = urllib.request.urlopen( api_url_chunk_1 + genre + api_url_chunk_2 ).read().decode( "utf-8" )
    json_object = json.loads( json_data ).get( "collection" )
    
    for song_dict in json_object:
        
        print([song_dict["track"]["id"],song_dict["track"]["title"],genre,song_dict["track"]["playback_count"],song_dict["track"]["likes_count"]])
#f1.writerow([song_dict["track"]["id"],song_dict["track"]["title"],genre,song_dict["track"]["download_count"],song_dict["track"]["playback_count"],song_dict["track"]["likes_count"]])

#f.close()
