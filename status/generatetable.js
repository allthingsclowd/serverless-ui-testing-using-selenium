// Initialize the Amazon Cognito credentials provider
AWS.config.region = 'eu-west-2'; // Region
AWS.config.credentials = new AWS.CognitoIdentityCredentials({
    IdentityPoolId: 'eu-west-2:dc4a3199-d9c7-47b1-b5e2-e1667cfab2a7',
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
        TableName: 'StatusTable-finaltest',
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
        TableName: 'StatusTable-finaltest',
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
        // Add a new cell for status
        let statusCell = row.insertCell(0);
        // Check the status and add the appropriate icon
        if (item.details.Status === 'Passed') {
            statusCell.innerHTML = '<i class="bi bi-check-circle-fill text-success"></i>'; // Bootstrap check icon
        } else {
            statusCell.innerHTML = '<i class="bi bi-x-circle-fill text-danger"></i>'; // Bootstrap times icon
        }
        row.insertCell(1).textContent = item.testrunid;
        row.insertCell(2).textContent = item.testcaseid;
        row.insertCell(3).textContent = item.details.EndTime;
        row.insertCell(4).textContent = item.details.ErrorMessage;
        row.insertCell(5).textContent = item.details.StartTime;
        row.insertCell(6).textContent = item.details.TimeTaken;
    });

    // Inform the MutationObserver about the table update
    mutationObserverCallback();
}

// MutationObserver for observing changes in the table
const tableBody = document.getElementById('dynamodbTable').getElementsByTagName('tbody')[0];
const observer = new MutationObserver(function(mutationsList) {
    for (let mutation of mutationsList) {
        if (mutation.type === 'childList') {
            console.log('Table updated with new data.');
        }
    }
});

observer.observe(tableBody, { childList: true, subtree: true });

// Callback function to handle mutations
function mutationObserverCallback() {
    // Placeholder for additional logic to handle DOM changes
}

// Event listener for dropdown changes
document.getElementById('testRunIdDropdown').addEventListener('change', function() {
    const selectedTestRunId = this.value;
    if (selectedTestRunId) {
        updateTableForTestRunId(selectedTestRunId);
    }
});

authenticate(); // Call authenticate when the script loads

// Clean up observer when it's no longer needed to prevent memory leaks
// observer.disconnect();
