# Uses beautifulsoup4, urllib, json
# Before every commit, do "git pull --rebase"

# Create CSV file with tag in first column, and list of comma separated track ID numbers in the second column

from bs4 import BeautifulSoup
import urllib.request
import json
import time
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

# master_dictionary is a dictionary with key = track_id, and value = an array of tags from tag_list
master_dictionary = {}

maximum_tag_length = 150
maximum_title_length = 0

for genre in genre_list:
    time.sleep( 0.5 )
    json_data = urllib.request.urlopen( api_url_chunk_1 + genre + api_url_chunk_2 ).read().decode( "utf-8" )
    json_object = json.loads( json_data ).get( "collection" )
    for song_dict in json_object:
        # Take the tag_list value, a string, and turn it into an array of tags
        if len( song_dict["track"]["title"] ) > maximum_title_length:
            maximum_title_length = len( song_dict["track"]["title"] )
        if song_dict["track"]["tag_list"].strip() != "":
            tag_array = []
            # Split the tag_list by quotation marks
            # Then, if an array element is succeeded by an item that starts with an empty space or an empty string, then that element is a tag itself. Trim its whitespace and add it to the new tag array.
            # Otherwise, it is a series of independent tags that should be split with a space, trimmed, and added to the new tag array.
            iterator = 0
            tag_list_array_quote_split = song_dict["track"]["tag_list"].split( "\"" )
            tag_list_array_quote_split_length = len( song_dict["track"]["tag_list"].split( "\"" ) )
            for value in tag_list_array_quote_split:
                # First check to make sure the item isn't empty
                if str( value ).strip() != "":
                    # If it's the last item in the array and isn't empty then it must be a series of tags.
                    if iterator + 1 >= tag_list_array_quote_split_length:
                        # Series of tags.
                        series_of_tags_array = value.split(" ")
                        for testable_tag in series_of_tags_array:
                            if testable_tag.strip() != "":
                                for comma_separated_tag in testable_tag.strip().split( "," ):
                                    if len( comma_separated_tag ) < maximum_tag_length:
                                        tag_array.append( comma_separated_tag.lower() )
                    # Now that the "end of array list of tags" use case is done, then we can test for the other 2 conditions.
                    # 
                    # First, we'll check to see if this value is a "tag in quotations"
                    if iterator + 1 < tag_list_array_quote_split_length:
                        if tag_list_array_quote_split[ iterator + 1 ] == "" or tag_list_array_quote_split[ iterator + 1 ].index( ' ' ) == 0:
                            # This value is a tag in quotations, so add its trimmed version to the master tag list
                            for comma_separated_tag in tag_list_array_quote_split[ iterator ].strip().split( "," ):
                                if len( comma_separated_tag ) < maximum_tag_length:
                                    tag_array.append( comma_separated_tag.lower() )
                    # Okay, so this array element MUST be a series of whitespace-separated tags.
                    # Use the "string.split()" function without parameters to split the string into individual tags, and add each 
                    # to the master tag list.
                    for individual_tag in tag_list_array_quote_split[ iterator ].split():
                        for comma_separated_tag in individual_tag.strip().split( "," ):
                            if len( comma_separated_tag ) < maximum_tag_length:
                                tag_array.append( comma_separated_tag.lower() )
                iterator = iterator + 1
            master_dictionary[ song_dict["track"]["id"] ] = tag_array


with open( "Tags.csv", "w" ) as tags_csv_file:
    csv_data_writer = csv.writer( tags_csv_file, dialect = "excel" )
    for root_key, root_value in master_dictionary.items():
        for node_value in root_value:
            new_row_array = [ root_key, node_value ]
            csv_data_writer.writerow( new_row_array )