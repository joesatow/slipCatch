/*
  Copyright 2020 Amazon.com, Inc. or its affiliates. All Rights Reserved.
  Permission is hereby granted, free of charge, to any person obtaining a copy of this
  software and associated documentation files (the "Software"), to deal in the Software
  without restriction, including without limitation the rights to use, copy, modify,
  merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
  permit persons to whom the Software is furnished to do so.
  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
  INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
  PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
  HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
  OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
  SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
*/

const { lambdaHandler } = require('./app')

// For local testing
process.env.ApplicationId = '7c3982138a614bf1b44b71568a119f60'
process.env.APIkey = 'AAAAAAAAAAAAAAAAAAAAAN34TwEAAAAAkuxlMQnYmZ3kaltdD%2FvFg0PFdBs%3D3JX9VTB9Z0vmUb7uuNxeF3t3BP3L6j2bkAWujuZ5Rgj8ED1tD1'

// Mock event
const event = {
  "Records": [
    {
      "eventVersion": "2.1",
      "eventSource": "aws:s3",
      "awsRegion": "us-east-1",
      "eventTime": "2022-03-18T03:51:28.628Z",
      "eventName": "ObjectCreated:Put",
      "userIdentity": {
        "principalId": "AWS:728866571318:joe"
      },
      "requestParameters": {
        "sourceIPAddress": "68.49.137.139"
      },
      "responseElements": {
        "x-amz-request-id": "GQTNK80D6NR5EC9Y",
        "x-amz-id-2": "EzEReDa+f7ZOC1zC5Du1IBAL6QYFC0k06AJ/RD1bdzmTxJiMDFTAA5gFEpkvy5SJbFmZHimtucoxkk+lW4LqSnjAH1kGhG2i"
      },
      "s3": {
        "s3SchemaVersion": "1.0",
        "configurationId": "6443891f-1e52-4f55-8d5a-bf4fff37ec28",
        "bucket": {
          "name": "slipcatch",
          "ownerIdentity": {
            "principalId": "AGRGXNAWT16XJ"
          },
          "arn": "arn:aws:s3:::testbucketjsatow"
        },
        "object": {
          "key": "1505013602016763905.json",
          "size": 106027,
          "eTag": "a2e00abc5815c5ef0af639cc2e06f52e",
          "sequencer": "00623401C09057E241"
        }
      }
    }
  ]
}

const main = async () => {
  await lambdaHandler(event)
}

main()
