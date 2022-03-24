import boto3
import os
import requests
import json
from datetime import datetime, timedelta
from dateutil.tz import UTC

session = boto3.Session()
s3 = session.resource('s3')
bucket_name = 'slipcatchphotos'
bucket = s3.Bucket(bucket_name)
auth = 'Bearer ' + os.environ['APIkey']

# datetime object containing current date and time
now = datetime.now()
now = now.astimezone(UTC)
d = now - timedelta(hours=0, minutes=1)
lastMinute = d.strftime("%Y-%m-%dT%H:%M:00Z")
lastMinute = '2022-03-17T16:35:00Z'
queries = ["satowjoseph", "joesatow"]

payload={}
headers = {
  'Authorization':  auth,
  'Cookie': 'guest_id=v1%3A164748160617485457; guest_id_ads=v1%3A164748160617485457; guest_id_marketing=v1%3A164748160617485457; personalization_id="v1_PFHqkQhmwp141oUu4hPm9w=="'
}

def lambdaHandler(event, context):

    for query in queries:

        twitUrl = "https://api.twitter.com/2/tweets/search/recent?query=from:" + query + "&start_time=" + lastMinute +  "&expansions=attachments.media_keys&media.fields=url"

        omitList = []
        response = requests.request("GET", twitUrl, headers=headers, data=payload)
        python_obj = json.loads(response.text)

        try:
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

                    try:
                        for attachment in item['attachments']['media_keys']:
                            omitList.append(attachment)
                            print('Photo found. media key: ' + attachment)
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
                        url = item['url']
                        #print("url: " + url)
                        r = requests.get(url, stream=True)
                        key = url.split("media/",1)[1]

                        #print("key: " + key)
                        bucket.upload_fileobj(r.raw,key)
                        detect_text(key,item['media_key'], python_obj)
                        #s3 = session.resource('s3')
                        #s3.Object('slipcatchphotos', key).delete()
        except Exception as e:
            print("json empty")
            print(e)

def detect_text(photo,mediakey,data):
    omitList = []
    client=boto3.client('rekognition')

    response=client.detect_text(Image={'S3Object':{'Bucket':'slipcatchphotos','Name':photo}})

    textDetections=response['TextDetections']
    for text in textDetections:
            if text['DetectedText'].lower() == "max":
                #print('First word: ' + text['DetectedText'])
                word2 = textDetections[int(text['Id'])+1]['DetectedText']
                #print('Following word: ' + word2)
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
            if mediakey not in omitList:
                if text['DetectedText'].lower() == "under":
                    word2 = textDetections[int(text['Id'])+1]['DetectedText']
                    if word2.lower() == "review...":
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
                                        omitList.append(mediakey)
                            except Exception as e:
                                #print(e)
                                print()
