// Initialize the Amazon Cognito credentials provider
AWS.config.region = 'eu-west-2'; // Region
AWS.config.credentials = new AWS.CognitoIdentityCredentials({
    IdentityPoolId: 'eu-west-2:0886abc9-4307-4e8b-a155-54624a27e0cf',
});

// Function to authenticate with Cognito
function authenticate() {
    AWS.config.credentials.get(function(err) {
        if (err) {
            alert("Error: " + err);
            return;
        }
        console.log("Cognito Identity Id: " + AWS.config.credentials.identityId);
        populateTestRunIdDropdown();
    });
}

// Function to populate the testrunid dropdown
function populateTestRunIdDropdown() {
    const docClient = new AWS.DynamoDB.DocumentClient();
    const params = {
        TableName: 'StatusTable-bananas',
        ProjectionExpression: 'testrunid'
    };

    docClient.scan(params, function(err, data) {
        if (err) {
            console.error("Unable to scan the table. Error JSON:", JSON.stringify(err, null, 2));
        } else {
            const uniqueTestRunIds = Array.from(new Set(data.Items.map(item => item.testrunid)));
            const dropdown = document.getElementById('testRunIdDropdown');
            uniqueTestRunIds.forEach(testrunid => {
                let option = new Option(testrunid, testrunid);
                dropdown.add(option);
            });
        }
    });
}

// Function to update the table based on selected testrunid
function updateTableForTestRunId(testrunid) {
    const docClient = new AWS.DynamoDB.DocumentClient();
    const params = {
        TableName: 'StatusTable-bananas',
        FilterExpression: 'testrunid = :testrunid',
        ExpressionAttributeValues: { ':testrunid': testrunid }
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

// Attach event listeners
document.getElementById('testRunIdDropdown').addEventListener('change', function() {
    const selectedTestRunId = this.value;
    if (selectedTestRunId) {
        updateTableForTestRunId(selectedTestRunId);
    }
});

authenticate(); // Call authenticate when the script loads
