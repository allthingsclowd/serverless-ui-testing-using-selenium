document.getElementById('login').addEventListener('click', function() {
  AWS.config.region = 'AWS_REGION'; // Replace with your AWS region
  AWS.config.credentials = new AWS.CognitoIdentityCredentials({
      IdentityPoolId: 'Cognito_IDP_ID', // Replace with your Cognito Identity Pool ID
  });

  AWS.config.credentials.get(function(err) {
      if (err) {
          console.error("Error retrieving credentials: ", err);
          return;
      }
      fetchLastDynamoDBEntry();
  });
});

function fetchLastDynamoDBEntry() {
  var docClient = new AWS.DynamoDB.DocumentClient();
  var params = {
      TableName: "DDB_STATUS_TABLE", // Replace with your table name
      // Assuming 'testcaseid' can be used to get the latest entry
      KeyConditionExpression: "testrunid = :testrunid",
      ExpressionAttributeValues: {
          ":testrunid": "suit-d31c933c-f994-46c7-8076-9e347f4bf977" // Replace with your partition key value
      },
      ScanIndexForward: false, // This will sort the results in descending order
      Limit: 1 // We only want the latest (last) entry
  };

  docClient.query(params, function(err, data) {
      if (err) {
          console.error("Unable to query. Error:", JSON.stringify(err, null, 2));
      } else {
          populateTable(data.Items);
      }
  });
}

function populateTable(items) {
  var table = document.getElementById('resultsTable').getElementsByTagName('tbody')[0];
  // Assuming there's only one item since we're getting the last entry
  var item = items[0];
  if (item) {
      var row = table.insertRow();
      row.insertCell(0).innerText = item.testrunid;
      row.insertCell(1).innerText = item.testcaseid;

      var details = item.details;
      row.insertCell(2).innerText = details.EndTime.S;
      row.insertCell(3).innerText = details.ErrorMessage.S;
      row.insertCell(4).innerText = details.StartTime.S;
      row.insertCell(5).innerText = details.Status.S;
      row.insertCell(6).innerText = details.TimeTaken.S;
  }
}
