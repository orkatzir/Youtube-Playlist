import random
import logging
import requests
import pandas as pd
import time
# from config_file import config
from prefect.blocks.system import JSON
from pprint import pformat
import json

from datetime import datetime

def fetch_playlist_name(google_api_key,youtube_playlist_id, page_token=None):
    response=requests.get("https://www.googleapis.com/youtube/v3/playlists", params={
        "key": google_api_key, 
        "id": youtube_playlist_id,
        "part": "snippet,contentDetails,status,id",
        "pageToken":page_token,
        })
    playlist_name=json.loads(response.text)['items'][0]['snippet']['title']
    return playlist_name

def fetch_playlist_items_page(google_api_key,youtube_playlist_id, page_token=None):

    response = requests.get("https://www.googleapis.com/youtube/v3/playlistItems", params={
        "key": google_api_key, 
        "playlistId": youtube_playlist_id,
        "part": "snippet,contentDetails,status,id",
        "pageToken":page_token,
        })
    
    payload = json.loads(response.text)
    logging.debug("GOT %s", pformat(payload))
   
    return payload

def fetch_videos_page(google_api_key,video_id, page_token=None):

    response = requests.get("https://www.googleapis.com/youtube/v3/videos", params={
        "key": google_api_key, 
        "id": video_id,
        "part": "snippet,contentDetails,statistics,id",
        "pageToken":page_token,
        })
    
    payload = json.loads(response.text)
    #logging.debug("GOT %s", pformat(payload))

    return payload

def fetch_playlist_items(google_api_key, youtube_playlist_id, page_token=None):
    #fetch one page
    payload = fetch_playlist_items_page(google_api_key, youtube_playlist_id, page_token)

    #serve up items from that page
    yield from payload["items"]
    
    
    #if there are more pages next
    next_page_token = payload.get("nextPageToken")

    if next_page_token is not None:
        yield from fetch_playlist_items(google_api_key,youtube_playlist_id,next_page_token)
        #carry on from there

def fetch_videos(google_api_key, youtube_playlist_id, page_token=None):
    #fetch one page
    payload = fetch_videos_page(google_api_key, youtube_playlist_id, page_token)

    #serve up items from that page
    yield from payload["items"]
    
    #if there are more pages next
    next_page_token = payload.get("nextPageToken")

    if next_page_token is not None:
        yield from fetch_videos(google_api_key,youtube_playlist_id,next_page_token)
        #carry on from there
def get_video_info_list(video:dict)-> dict:
    row = [
        video["snippet"]["title"],
        video['id'],
        video['snippet']['thumbnails']['default']['url'],
        int(video["snippet"].get('position',int(0))),
        int(video['statistics'].get('commentCount',int(0))), 
        int(video['statistics'].get('favoriteCount',int(0))), 
        int(video['statistics'].get('likeCount',int(0))), 
        int(video['statistics'].get('viewCount',int(0))),
        video['snippet']['publishedAt'],
        video['snippet']['channelTitle'],
        video['snippet']['description']     
    ]

    return row


def on_delivery(err,record):
    pass

def main(youtube_playlist_id):
    logging.info("START")

    google_api_key = JSON.load("google-api-key").value['google_api_key']

    playlist_first_page = fetch_playlist_items_page(google_api_key,youtube_playlist_id, page_token=None)
    playlist_name = fetch_playlist_name(google_api_key,youtube_playlist_id, page_token=None)

    #initiate video's stats dictionary:
    data_videos = []

    #start looping in each video of playlist
    for video_item in fetch_playlist_items(google_api_key,youtube_playlist_id):
        video_id = video_item["contentDetails"]["videoId"]
        #logging.debug("GOT %s", video_id)
        for video in fetch_videos(google_api_key, video_id):
            logging.debug("GOT %s", video)

            video_row = get_video_info_list(video)
            data_videos.append(video_row)
    
    # create the dataframe from the data list and add column names
    df = pd.DataFrame(data_videos, columns=['video_name','videoid','thumbnail','playlist_possition', 'commentCount', 'favoriteCount', 'likeCount', 'viewCount', 'publishedAt', 'channelTitle','description'])

    logging.info("GOT %s", df.head())
    return df,playlist_name
    #sent messages to kafka
    

if __name__== "__main__":
    logging.basicConfig(level=logging.INFO)
    #PL3MmuxUbc_hJed7dXYoJw8DoCuVHhGEQb is the playlist id of DTC data engneering course

    youtube_playlist_id = 'PLJYIzyhJUEpjw6p-8iJS_iDlCbbeE_qb2'
    df,playlist_name = main(youtube_playlist_id)
    print(playlist_name)
    #sys.exit(main())