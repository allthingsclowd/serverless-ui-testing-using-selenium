// Initialize the Amazon Cognito credentials provider
AWS.config.region = 'AWS_REGION'; // Region
AWS.config.credentials = new AWS.CognitoIdentityCredentials({
    IdentityPoolId: 'Cognito_IDP_ID',
});

// Function to authenticate with Cognito
function authenticate() {
    AWS.config.credentials.get(function(err) {
        if (err) {
            alert("Error: " + err);
            return;
        }
        console.log("Cognito Identity Id: " + AWS.config.credentials.identityId);
        listDynamoDBRecords();
    });
}

// Function to list records from DynamoDB
function listDynamoDBRecords() {
    const docClient = new AWS.DynamoDB.DocumentClient();
    const params = {
        TableName: 'DDB_STATUS_TABLE',
    };

    docClient.scan(params, function(err, data) {
        if (err) {
            console.error("Unable to scan the table. Error JSON:", JSON.stringify(err, null, 2));
        } else {
            populateTable(data.Items);
        }
    });
}

// Function to populate the HTML table with DynamoDB data
function populateTable(items) {
    const tableBody = document.getElementById('dynamodbTable').getElementsByTagName('tbody')[0];

    // Clear the table before populating it
    while(tableBody.firstChild) {
        tableBody.removeChild(tableBody.firstChild);
    }

    items.forEach(function(item) {
        let row = tableBody.insertRow();
        row.insertCell(0).textContent = item.testrunid;
        row.insertCell(1).textContent = item.testcaseid;
        row.insertCell(2).textContent = item.details.EndTime.S;
        row.insertCell(3).textContent = item.details.ErrorMessage.S;
        row.insertCell(4).textContent = item.details.StartTime.S;
        row.insertCell(5).textContent = item.details.Status.S;
        row.insertCell(6).textContent = item.details.TimeTaken.S;
    });
}

// Attach event listener to login button
document.getElementById('login').addEventListener('click', authenticate);
