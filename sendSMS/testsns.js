console.log("Loading function");
const AWS = require("aws-sdk");
const s3 = new AWS.S3();
AWS.config.update({region: 'us-east-1'});

    var params = {
        Message: "one",
        TopicArn: "arn:aws:sns:us-east-1:728866571318:testtopic"
    };
    var params2 = {
        Message: "two",
        TopicArn: "arn:aws:sns:us-east-1:728866571318:testtopic"
    };
    var params3 = {
        Message: "three",
        TopicArn: "arn:aws:sns:us-east-1:728866571318:testtopic"
    };
    var params4 = {
        Message: "four",
        TopicArn: "arn:aws:sns:us-east-1:728866571318:testtopic"
    };

    // Create promise and SNS service object
    var publishTextPromise = new AWS.SNS({apiVersion: '2010-03-31'}).publish(params).promise();
    var publishTextPromise2 = new AWS.SNS({apiVersion: '2010-03-31'}).publish(params2).promise();
    var publishTextPromise3 = new AWS.SNS({apiVersion: '2010-03-31'}).publish(params3).promise();
    var publishTextPromise4 = new AWS.SNS({apiVersion: '2010-03-31'}).publish(params4).promise();

    // Handle promise's fulfilled/rejected states
    publishTextPromise.then(
      function(data) {
        console.log(`Message ${params.Message} sent to the topic ${params.TopicArn}`);
        console.log("MessageID is " + data.MessageId);
      }).catch(
        function(err) {
        console.error(err, err.stack);
      });

      publishTextPromise2.then(
        function(data) {
          console.log(`Message ${params2.Message} sent to the topic ${params2.TopicArn}`);
          console.log("MessageID is " + data.MessageId);
        }).catch(
          function(err) {
          console.error(err, err.stack);
        });

        publishTextPromise3.then(
          function(data) {
            console.log(`Message ${params3.Message} sent to the topic ${params3.TopicArn}`);
            console.log("MessageID is " + data.MessageId);
          }).catch(
            function(err) {
            console.error(err, err.stack);
          });

          publishTextPromise4.then(
            function(data) {
              console.log(`Message ${params4.Message} sent to the topic ${params4.TopicArn}`);
              console.log("MessageID is " + data.MessageId);
            }).catch(
              function(err) {
              console.error(err, err.stack);
            });
