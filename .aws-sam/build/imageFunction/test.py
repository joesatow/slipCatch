import boto3
import requests
import os
import json
from datetime import datetime, timedelta
from dateutil.tz import UTC

url = "https://pbs.twimg.com/media/FOB0OU0X0AcBWOk.jpg"
r = requests.get(url, stream=True)
session = boto3.Session()
s3 = session.resource('s3')
bucket_name = 'www.josephsatow.com'
key = url.split("media/",1)[1]
bucket = s3.Bucket(bucket_name)
auth = 'Bearer ' + 'AAAAAAAAAAAAAAAAAAAAAN34TwEAAAAAkuxlMQnYmZ3kaltdD%2FvFg0PFdBs%3D3JX9VTB9Z0vmUb7uuNxeF3t3BP3L6j2bkAWujuZ5Rgj8ED1tD1'

# datetime object containing current date and time
#now = datetime.now(pytz.utc)
now = datetime.now()
now = now.astimezone(UTC)
d = now - timedelta(hours=72, minutes=1)
lastMinute = d.strftime("%Y-%m-%dT%H:%M:00Z")
print(lastMinute)

twitUrl = "https://api.twitter.com/2/tweets/search/recent?query=from:satowjoseph&start_time=" + lastMinute +  "&expansions=attachments.media_keys&media.fields=url"

payload={}
headers = {
  'Authorization':  auth,
  'Cookie': 'guest_id=v1%3A164748160617485457; guest_id_ads=v1%3A164748160617485457; guest_id_marketing=v1%3A164748160617485457; personalization_id="v1_PFHqkQhmwp141oUu4hPm9w=="'
}


response = requests.request("GET", twitUrl, headers=headers, data=payload)

python_obj = json.loads(response.text)
omitList = []
try:
    for item in python_obj['data']:
        print("Found new text tweet")
        print('id: ' + item['id'])
        print('text: ' + item['text'])

        try:
            for attachment in item['attachments']['media_keys']:
                omitList.append(attachment)
                print('Photo found: ' + attachment)
            print()
        except Exception as e:
            print('No attachments')
            #print(e)
            print()

    for item in python_obj['includes']['media']:
        if (item['type'] == 'photo'):
            #print(item['url'])
            if item['media_key'] not in omitList:
                print('New single photo.  media key: ' + item['media_key'])
                print()
                url = item['url']
                print("url: " + url)

except Exception as e:
    print("no results")
    print(e)

print(omitList)

def detect_text(photo,mediakey,data):

    client=boto3.client('rekognition')

    response=client.detect_text(Image={'S3Object':{'Bucket':'slipcatchphotos','Name':photo}})

    textDetections=response['TextDetections']
    for text in textDetections:
            if text['DetectedText'].lower() == "max":
                print('First word: ' + text['DetectedText'])
                word2 = textDetections[int(text['Id'])+1]['DetectedText']
                print('Following word: ' + word2)

                if word2.lower() == "wager":
                    print('Photo detection.  max bet found. media key: ' + mediakey)
                    for item in data['data']:
                        try:
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
                        except Exception as e:
                            #print(e)
                            print()

            if text['DetectedText'].lower() == "under":
                print('First word: ' + text['DetectedText'])
                word2 = textDetections[int(text['Id'])+1]['DetectedText']
                print('Following word: ' + word2)

                if word2.lower() == "review":
                    print('Photo detection.  under review found. media key: ' + mediakey)
                    for item in data['data']:
                        try:
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
                        except Exception as e:
                            #print(e)
                            print()
