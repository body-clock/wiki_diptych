import requests
import wikipedia
import tweepy
from io import BytesIO
from PIL import Image
import boto3
import os
import uuid


aws_access_key_id = os.environ['AWS_ACCESS']
aws_secret_access_key = os.environ['AWS_SECRET']


# defining our twitter api
def twitter_api():
    twitter_api_key = os.environ["TWITTER_API_KEY"]
    twitter_api_secret = os.environ["TWITTER_API_SECRET"]

    twitter_access_token = os.environ["TWITTER_ACCESS_TOKEN"]
    twitter_access_secret = os.environ["TWITTER_ACCESS_SECRET"]

    auth = tweepy.OAuthHandler(twitter_api_key, twitter_api_secret)
    auth.set_access_token(twitter_access_token, twitter_access_secret)

    api = tweepy.API(auth)
    return api


def get_page_with_at_least_two_jpegs():
    # start the count at 0
    count_of_jpegs = 0
    while count_of_jpegs < 2:
        try:
            # getting one random wiki page
            random_page = wikipedia.page(wikipedia.random(1))
            image_urls = random_page.images

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
                    count_of_jpegs += 1
                    jpeg_url = url
        except wikipedia.exceptions.DisambiguationError:
            print('DisambiguationError')
            continue
        except wikipedia.exceptions.PageError:
            print('PageError')
            continue

    # return the title & url of page with more than 2 jpegs
    return random_page.title, jpeg_url


def prepare_image_path(pair):
    # this function will take in an array [title, image_url]
    # store image data in memory
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/39.0.2171.95 Safari/537.36'}
    response = requests.get(pair[1], headers=headers)
    img = BytesIO(response.content)
    # connect to s3 bucket
    bucket = 'wiki-diptych-bucket'
    s3 = boto3.client('s3',
                      aws_access_key_id=aws_access_key_id,
                      aws_secret_access_key=aws_secret_access_key)
    # upload image to s3
    img_name = f'{uuid.uuid4().hex}.jpg'
    s3.upload_fileobj(img, bucket, img_name)
    # download into lambda tmp directory
    s3_resource = boto3.resource('s3',
                                 aws_access_key_id=aws_access_key_id,
                                 aws_secret_access_key=aws_secret_access_key)
    s3_resource.Bucket(bucket).download_file(f'{img_name}', f'/tmp/{img_name}')
    # delete from s3
    s3.delete_object(Bucket=bucket, Key=img_name)
    # test and downscale that image in tmp if too large
    return [pair[0], test_image_and_downscale_if_too_large(f'/tmp/{img_name}')]
    # return array [title, image_path]


# reads inputs from the title & url pairs of 2 pages
def assemble_tweet(first_pair, second_pair):
    success = False
    while not success:
        try:
            # download the image and store it locally
            img1_path = first_pair[1]
            img2_path = second_pair[1]

            # upload our images to twitter & update our media_ids
            filenames = [img1_path, img2_path]
            media_ids = []
            for filename in filenames:
                try:
                    res = twitter_api().media_upload(filename)
                    media_ids.append(res.media_id)
                except tweepy.error.TweepError as e:
                    print(e)
                    continue

            # tweet names of articles & pictures
            twitter_api().update_status(status=first_pair[0] + ', ' + second_pair[0], media_ids=media_ids)
            success = True

        # error handling
        except tweepy.error.TweepError as e:
            print(e)


# test if our image is too large for tweepy to send it
def test_image_and_downscale_if_too_large(filepath):
    # if the image is < 2000kb, return image
    image_size = os.stat(filepath).st_size
    success = False
    while not success:
        if image_size < 2000000:
            success = True
            return filepath
        # if the image is > 2000kb, return resized image and replace file
        else:
            original_image = Image.open(filepath)
            original_image.save(filepath, quality=20, optimized=True)
            return filepath


# main loop
def lambda_handler(event, context):
    first_pair = get_page_with_at_least_two_jpegs()
    second_pair = get_page_with_at_least_two_jpegs()
    print(first_pair)
    print(second_pair)
    assemble_tweet(prepare_image_path(first_pair), prepare_image_path(second_pair))
