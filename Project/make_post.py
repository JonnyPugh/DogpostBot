#!/usr/bin/env python

from extensions import *
from random import choice
from sets import Set
from PIL import Image
from imagehash import average_hash
from requests import post
import os

error_log = open("error.log", "a+")

def main():
    # Form a set of the hashes of all posted photos to check for duplicates
    hashes = Set([post_info["hash"] for post_info in execute_query("select hash from Posts")])

    # Choose an image to post
    while True:
        try:
            # Choose a random source and image from that source
            source = choice(os.listdir(images_directory))
            source_directory = images_directory+source
            files = os.listdir(source_directory)
            if not files:
                continue
            filename = choice(files)
            filepath = source_directory+"/"+filename
            file_hash = str(average_hash(Image.open(filepath)))
            if file_hash not in hashes:
                break
            write_to_log(error_log, "Deleting photo that has already been posted with hash: "+file_hash)
        except:
            write_to_log(error_log, "Deleting unopenable photo: "+filepath)

        # Delete this photo if it is a duplicate of another
        # one that has already been posted or if it is unopenable
        os.remove(filepath)
    
    # Post the photo, insert its data into the database, delete it, and log it
    data = get_request_params({
        "tags[]": [] if source == "no_source" else [{"tag_uid": source}]
    })
    files = {
        "source": open(filepath, "rb")
    }
    r = post(graph_url+page_id+"/photos", data=data, files=files)
    r.raise_for_status()
    post_id = r.json()["id"]
    execute_query("insert into Posts (hash, filename, source, id) values (%s, %s, %s, %s)", (file_hash, filename, "NULL" if source == "no_source" else source, post_id))
    os.remove(filepath)
    write_to_log(open("posts.log", "a+"), "Finished making post with id: "+post_id)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        write_to_log(error_log, "Unexpected error caught while making a post: "+str(e))
