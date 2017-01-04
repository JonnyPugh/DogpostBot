#!/usr/bin/env python

from extensions import *
from requests import get
from urllib import urlretrieve
from dateutil import parser
from tzlocal import get_localzone
import os

downloads_log = open("downloads.log", "a+")

def get_request_json(url, extra_params):
	request = get(url, params=get_request_params(extra_params))
	request.raise_for_status()
	return request.json()

def get_photo(photo_id, directory, reactions, time_last_checked):
	# Get the reactions info of the picture to decide whether to download it
	if get_request_json(graph_url+photo_id+"/reactions", {"summary": "total_count"})["summary"]["total_count"] > reactions:
		# Get the picture url to download it
		url = get_request_json(graph_url+photo_id, {"fields": "images"})["images"][0]["source"]

		# Attempt to download the photo and if there 
		# are any problems, keep retrying
		while True:
			try:
				urlretrieve(url, directory+photo_id+".jpg")
				break
			except:
				write_to_log(downloads_log, "Error downloading photo: "+photo_id+", retrying...")

def loop_through_json(json, time_last_checked, function, arg2, arg3):
	# Loop through all of the data in the json and call the specified function
	while json["data"]:
		for info in json["data"]:
			if parser.parse(info["created_time"]) > time_last_checked.replace(tzinfo=get_localzone()):
				function(info["id"], arg2, arg3, time_last_checked)
			else:
				break
		if not "next" in json["paging"]:
			break
		json = get_request_json(json["paging"]["next"], {})

def get_page_images(page_id, source_id, reactions, time_last_checked):
	# Create the directory to store the photos if it doesn't exist
	directory = images_directory+source_id+"/"
	if not os.path.exists(directory):
		os.makedirs(directory)

	# Go through all photos and download them if they match the criteria
	loop_through_json(get_request_json(graph_url+page_id+"/photos", {"type": "uploaded"}), time_last_checked, get_photo, directory, reactions)

def get_group_images(group_id, time_last_checked):
	# Go through all albums and download images
	loop_through_json(get_request_json(graph_url+group_id+"/albums", {}), time_last_checked, get_page_images, group_id, 25)

def get_reactions_threshold(page_id):
	# Use a threshold of 2% of the total likes on the page
	return get_request_json(graph_url+page_id, {"fields": "fan_count"})["fan_count"] / 50

def main():
	# Get new photos from the sources
	for page in execute_query("select* from Sources"):
		page_id = page["id"]
		time_last_checked = page["time"]
		page_type = page["type"]
		if page_type == "page":
			get_page_images(page_id, page_id, get_reactions_threshold(page_id), time_last_checked)
		else:
			get_group_images(page_id, time_last_checked)
		execute_query("update Sources set time = current_timestamp where id = %s", (page_id,))
		write_to_log(downloads_log, "Finished downloading new images from "+page_type+": "+page_id)
	write_to_log(downloads_log, "Finished downloading new images from all sources")

if __name__ == "__main__":
	try:
		main()
	except Exception as e:
		write_to_log(downloads_log, "Unexpected error caught while downloading photos: "+str(e))
