import boto3
import requests
import os
import json
from datetime import datetime, timedelta
from dateutil.tz import UTC

auth = 'Bearer ' + 'AAAAAAAAAAAAAAAAAAAAAN34TwEAAAAAkuxlMQnYmZ3kaltdD%2FvFg0PFdBs%3D3JX9VTB9Z0vmUb7uuNxeF3t3BP3L6j2bkAWujuZ5Rgj8ED1tD1'
session = boto3.Session()
s3 = session.resource('s3')
bucket_name = 'slipcatchphotos'
bucket = s3.Bucket(bucket_name)

# datetime object containing current date and time
now = datetime.now()
now = now.astimezone(UTC)
d = now - timedelta(hours=0, minutes=1)
lastMinute = d.strftime("%Y-%m-%dT%H:%M:00Z")
#lastMinute = '2022-03-17T20:35:00Z'
queries = ["satowjoseph", "joesatow", "beaulwagner", "onlyparlays_", "themistermarcus", "portman7387", "j2110"]
#queries = ["satowjoseph", "joesatow"]

payload={}
headers = {
  'Authorization':  auth,
  'Cookie': 'guest_id=v1%3A164748160617485457; guest_id_ads=v1%3A164748160617485457; guest_id_marketing=v1%3A164748160617485457; personalization_id="v1_PFHqkQhmwp141oUu4hPm9w=="'
}

def checkJson(key,jsonContents):
    existsFlag = True if key in jsonContents else False
    return existsFlag

def detect_text(photo,mediakey,data):
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
                                print("id: " + item['id'])
                                json_object = {
                                            "id": item['id']
                                            }
                                s3 = boto3.client('s3')
                                s3.put_object(
                                    Body=json.dumps(json_object),
                                    Bucket='slipcatch',
                                    Key=item['id'] + '.json'
                                )
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
                                    print("id: " + item['id'])
                                    json_object = {
                                                "id": item['id']
                                                }
                                    s3 = boto3.client('s3')
                                    s3.put_object(
                                        Body=json.dumps(json_object),
                                        Bucket='slipcatch',
                                        Key=item['id'] + '.json'
                                    )
                                    omitList.append(mediakey)

    if found == False:
        print("Nothing found.")

for query in queries:
    twitUrl = "https://api.twitter.com/2/tweets/search/recent?query=from:" + query + "&start_time=" + lastMinute + "&expansions=attachments.media_keys&media.fields=url"
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
        errorTime = errorTime.strftime("%m-%d-%Y_%H:%M")
        s3 = boto3.client('s3')
        s3.put_object(
            Body=json.dumps(json_object),
            Bucket='slipcatcherrors',
            Key=str(errorTime) + '.json'
        )
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

                    s3 = boto3.client('s3')
                    s3.put_object(
                        Body=json.dumps(json_object),
                        Bucket='slipcatch',
                        Key=item['id'] + '.json'
                    )

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
                            print('New single photo from: ' + query + '. Media key: ' + item['media_key'] + ". Sending to scan...")
                            url = item['url']
                            r = requests.get(url, stream=True)
                            key = url.split("media/",1)[1]

                            bucket.upload_fileobj(r.raw,key)
                            detect_text(key,item['media_key'], python_obj)
                            print()
