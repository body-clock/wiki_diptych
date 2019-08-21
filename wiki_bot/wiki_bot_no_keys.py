import wikipedia
import tweepy
import random
import urllib.request
from PIL import Image
import os

# defining our twitter api
def twitter_api():

    #removed keys
    TWITTER_CONSUMER_KEY = os.environ.get('TWITTER_CONSUMER_KEY')
    TWITTER_CONSUMER_SECRET = os.environ.get('TWITTER_CONSUMER_SECRET')

    TWITTER_ACCESS_TOKEN = os.environ.get('TWITTER_ACCESS_TOKEN')
    TWITTER_ACCESS_SECRET = os.environ.get('TWITTER_ACCESS_SECRET')

    auth = tweepy.OAuthHandler(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
    auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET)
    api = tweepy.API(auth)
    return api

def get_page_with_at_least_two_jpegs():

    #start the count at 0
    count_of_jpegs = 0
    while count_of_jpegs < 2:
        try:
            # getting one random wiki page
            random_page = wikipedia.page(wikipedia.random(1))

            # count the images on the page
            image_count = len(random_page.images)

            # my reasoning is that pages with more images will tend to have better
            # quality .jpgs, could improve this part
            if image_count > 3:
                image_urls = random_page.images
            else:
                image_urls = []

            # reset jpg count for when we examine the second page
            count_of_jpegs = 0

            # count jpg images from urls
            for url in image_urls:
                if url[-4:] == '.jpg':
                    count_of_jpegs+=1
                    jpeg_url = url
        except wikipedia.exceptions.DisambiguationError:
            print('DisambiguationError')
            continue
        except wikipedia.exceptions.PageError:
            print('PageError')
            continue

    # return the title & url of page with more than 2 jpegs
    return random_page.title, jpeg_url

# reads inputs from the title & url pairs of 2 pages
def assemble_tweet(first_pair, second_pair):

    success = False
    while not success:
        try:
            # download the image and store it locally
            urllib.request.urlretrieve(first_pair[1], '/home/pi/wiki_diptych/wiki_bot/first_image.jpg')
            urllib.request.urlretrieve(second_pair[1], '/home/pi/wiki_diptych/wiki_bot/second_image.jpg')

            #upload our images to twitter & update our media_ids
            filenames = ['/home/pi/wiki_diptych/wiki_bot/first_image.jpg','/home/pi/wiki_diptych/wiki_bot/second_image.jpg']
            media_ids = []
            for filename in filenames:
                #test size of images, return appropraite file
                test_image_and_downscale_if_too_large(filename)
                try:
                    res = twitter_api().media_upload(filename)
                    media_ids.append(res.media_id)
                except tweepy.error.TweepError:
                    print(tweepy.error.TweepError)
                    continue

            # tweet names of articles & pictures
            twitter_api().update_status(status = first_pair[0] + ', ' + second_pair[0], media_ids=media_ids)
            success = True

        #error handling
        except tweepy.error.TweepError:
            print(tweepy.error.TweepError)


# test if our image is too large for tweepy to send it
def test_image_and_downscale_if_too_large(filepath):

    #if the image is < 2000kb, return image
    image_size = os.stat(filepath).st_size
    success = False
    while not success:
        if image_size < 2000000:
            success = True
            return filepath
        #if the image is > 2000kb, return resized image and replace file
        else:
            original_image = Image.open(filepath)
            original_image.save(filepath, quality=20, optimized=True)
            return filepath

#main loop
first_pair = get_page_with_at_least_two_jpegs()
second_pair = get_page_with_at_least_two_jpegs()
print(first_pair)
print(second_pair)
assemble_tweet(first_pair,second_pair)

