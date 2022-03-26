console.log("Loading function");
const AWS = require("aws-sdk");
var moment = require('moment');
const s3 = new AWS.S3();
AWS.config.update({region: 'us-east-1'});

exports.lambdaHandler = function(event, context) {
  const day = moment().format('MM-DD-YYYY');

  var params = {
   Bucket: 'slipcatcherrors',
   Prefix: day
  }

  s3.listObjects(params, function (err, data) {
    if(err)throw err;
    data['Contents'].forEach(element => {
      console.log("Error event detected");
      var params = {
        Bucket: 'slipcatcherrors',
        Key: element['Key']
      }
      getObject(params);
    });
  });
};

async function getObject(p){
  const data = JSON.parse((await (s3.getObject(p).promise())).Body.toString('utf-8'))
  var params = {
      Message: "Error found for user: " + data['user'] + ".  Error message: " + data['error'],
      TopicArn: "arn:aws:sns:us-east-1:728866571318:testtopic",
      MessageAttributes: {
        'AWS.SNS.SMS.SMSType': {
          DataType: 'String',
          StringValue: 'Promotional'
        }
      }
  }
  sendSNSmessage(params);
}

function sendSNSmessage(parameters){
  // Create promise and SNS service object
  var publishTextPromise = new AWS.SNS({apiVersion: '2010-03-31'}).publish(parameters).promise();

  // Handle promise's fulfilled/rejected states
  publishTextPromise.then(
    function(data) {
      console.log(`Message ${parameters.Message} sent to the topic ${parameters.TopicArn}`);
      console.log("MessageID is " + data.MessageId);
    }).catch(
      function(err) {
        console.error(err, err.stack);
        console.log(err)
    });
}
