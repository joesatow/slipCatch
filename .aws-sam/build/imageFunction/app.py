import boto3
import os
import requests
import json
from datetime import datetime, timedelta

def lambdaHandler(event, context):
    # ititialize S3 session
    s3 = boto3.resource('s3')

    # Twitter API bearer token
    auth = 'Bearer ' + os.environ['APIkey']

    # datetime object containing current date and time
    now = datetime.now()
    d1 = now - timedelta(hours=0, minutes=2)
    d2 = now - timedelta(hours=0, minutes=1)
    earliestMinute = d1.strftime("%Y-%m-%dT%H:%M:00Z")
    latestMinute = d2.strftime("%Y-%m-%dT%H:%M:00Z")
    #lastMinute = '2022-03-17T20:35:00Z'
    queries = ["satowjoseph", "joesatow", "beaulwagner", "onlyparlays_", "themistermarcus", "portman7387", "j2110"]

    payload={}
    headers = {
      'Authorization':  auth,
      'Cookie': 'guest_id=v1%3A164748160617485457; guest_id_ads=v1%3A164748160617485457; guest_id_marketing=v1%3A164748160617485457; personalization_id="v1_PFHqkQhmwp141oUu4hPm9w=="'
    }

    print("earliestMinute: " + earliestMinute)
    print("latestMinute: " + latestMinute)
    for query in queries:

        # Prod URL
        twitUrl = "https://api.twitter.com/2/tweets/search/recent?query=from:" + query + "&start_time=" + earliestMinute + "&end_time=" + latestMinute + "&expansions=attachments.media_keys&media.fields=url"

        # Test URL
        #twitUrl = "https://api.twitter.com/2/tweets/search/recent?query=from:" + query + "&start_time=" + (now - timedelta(hours=0, minutes=1)).strftime("%Y-%m-%dT%H:%M:00Z") + "&expansions=attachments.media_keys&media.fields=url"
        omitList = []
        response = requests.request("GET", twitUrl, headers=headers, data=payload)
        python_obj = json.loads(response.text)

        if checkJson("errors",python_obj):
            print()
            print("errors found in API call for user: " + query)
            print("error message: " + python_obj['errors'][0]['message'])
            print()

            json_object = {
                        "user": query,
                        "error": python_obj['errors'][0]['message']
                        }

            errorTime = now - timedelta(hours=5, minutes=0)
            errorTime = errorTime.strftime("%m-%d-%Y")

            uploadJSONtoS3(json.dumps(json_object),'slipcatcherrors',str(errorTime) + "_" + query + '.json')
        else:
            resultCount = python_obj['meta']['result_count']
            if resultCount == 0:
                print("no tweets from user: " + query)
            else:
                for item in python_obj['data']:
                    if "maxbet" in item['text'].lower().replace(" ", ""):
                        print("Found new text tweet")
                        print('id: ' + item['id'])
                        print('text: ' + item['text'])
                        json_object = {
                                    "id": item['id'],
                                    "text": item['text']
                                    }

                        uploadJSONtoS3(json.dumps(json_object),'slipcatch',item['id'] + '.json')

                        if checkJson('attachments',item):
                            print("attachments here - max result in text. Omitting photo scan...")
                            for attachment in item['attachments']['media_keys']:
                                print('Media found. media key: ' + attachment)
                                omitList.append(attachment)
                                print()
                        else:
                            print("no attachments here")
                            print()

                if checkJson('includes',python_obj):
                    for item in python_obj['includes']['media']:
                        if (item['type'] == 'photo'):
                            if item['media_key'] not in omitList:
                                print('New single photo from: ' + query + '. Media key: ' + item['media_key'] + ". Scanning photo...")
                                url = item['url']
                                key = url.split("media/",1)[1]
                                r = requests.get(url, stream=True)
                                uploadPhotoToS3(url,key)
                                if not detect_text(key,item['media_key'],python_obj,url):
                                    print("Nothing found. Deleting photo: " + item['media_key'] + "...")
                                    s3.Object('slipcatchphotos', key).delete()
                                print()

def checkJson(key,jsonContents):
    existsFlag = True if key in jsonContents else False
    return existsFlag

def detect_text(photo,mediakey,data,url):
    print("Beginning scan for: " + mediakey)
    omitList = []
    client=boto3.client('rekognition')
    response=client.detect_text(Image={'S3Object':{'Bucket':'slipcatchphotos','Name':photo}})
    textDetections=response['TextDetections']
    found = False

    print("Checking for key words...")
    for text in textDetections:
        if text['DetectedText'].lower() == "max":
            #print('First word: ' + text['DetectedText'])
            word2 = textDetections[int(text['Id'])+1]['DetectedText']
            #print('Following word: ' + word2)
            if word2.lower() == "wager":
                print('Photo detection.  max bet found. media key: ' + mediakey)
                found = True
                for item in data['data']:
                    if checkJson('attachments',item):
                        for attachment in item['attachments']['media_keys']:
                            if attachment == mediakey:
                                json_object = {
                                            "id": item['id']
                                            }
                                uploadJSONtoS3(json.dumps(json_object),'slipcatch',item['id'] + '.json')
                                print("Uploading photo... Media key: " + mediakey + ". Photo id: " + photo)
                                uploadPhotoToS3(url,photo)
                                return True
        elif mediakey not in omitList:
            if text['DetectedText'].lower() == "under":
                word2 = textDetections[int(text['Id'])+1]['DetectedText']
                if word2.lower() == "review...":
                    print('Photo detection.  under review found. media key: ' + mediakey)
                    found = True
                    for item in data['data']:
                        if checkJson('attachments',item):
                            for attachment in item['attachments']['media_keys']:
                                if attachment == mediakey:
                                    json_object = {
                                                "id": item['id']
                                                }
                                    uploadJSONtoS3(json.dumps(json_object),'slipcatch',item['id'] + '.json')
                                    omitList.append(mediakey)
                                    print("Uploading photo... Media key: " + mediakey + ". Photo id: " + photo)
                                    uploadPhotoToS3(url,photo)
                                    return True

    if found == False:
        return False

def uploadPhotoToS3(url,key):
    session = boto3.Session()
    s3 = session.resource('s3')
    bucket_name = 'slipcatchphotos'
    bucket = s3.Bucket(bucket_name)

    r = requests.get(url, stream=True)
    bucket.upload_fileobj(r.raw,key)

def uploadJSONtoS3(body,bucket,key):
    s3 = boto3.client('s3')
    s3.put_object(
        Body=body,
        Bucket=bucket,
        Key=key
    )
