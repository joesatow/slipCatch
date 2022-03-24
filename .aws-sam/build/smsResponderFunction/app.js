console.log("Loading function");
const AWS = require("aws-sdk");
const s3 = new AWS.S3();
AWS.config.update({region: 'us-east-1'});

exports.lambdaHandler = function(event, context) {
    var eventText = JSON.stringify(event, null, 2);
    eventText = JSON.parse(eventText);
    var objectKey = eventText["Records"][0]["s3"]["object"]["key"];
    console.log("Received event:", objectKey);

    var params = {
        Bucket: 'slipcatch',
        Key: objectKey,
    };

    tweeturl = objectKey.split(".")
    tweeturl = "https://twitter.com/b/status/" + tweeturl[0];
    console.log(tweeturl);

    var params = {
        Message: "New tweet found!  " + tweeturl,
        TopicArn: "arn:aws:sns:us-east-1:728866571318:testtopic"
    };

    // Create promise and SNS service object
    var publishTextPromise = new AWS.SNS({apiVersion: '2010-03-31'}).publish(params).promise();

    // Handle promise's fulfilled/rejected states
    publishTextPromise.then(
      function(data) {
        console.log(`Message ${params.Message} sent to the topic ${params.TopicArn}`);
        console.log("MessageID is " + data.MessageId);
      }).catch(
        function(err) {
          console.log("promise catch" + tweeturl);
        console.error(err, err.stack);
        console.log(err)
      });
};
