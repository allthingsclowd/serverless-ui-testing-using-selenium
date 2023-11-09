/*jshint esversion: 6 */

AWS.config.credentials = new AWS.CognitoIdentityCredentials({
  IdentityPoolId: 'eu-west-2:d08b7fac-6c5c-45e5-a934-98041f52db66',
});

AWS.config.region = "eu-west-2";
var ddb = new AWS.DynamoDB.DocumentClient();
var body, chrome_tab, firefox_tab;
var firstload = 1;

function getdata(trunid, params) {
  var flag;
  var tbl = document.createElement('table');
  tbl.setAttribute('id', 'testRunTab');
  tbl.style.backgroundColor = "#ccdecc";
  tbl.style.fontFamily = "Arial";
  tbl.style.fontSize = "90%";
  tbl.style.whiteSpace = "nowrap";
  thead = tbl.createTHead();
  tr = thead.insertRow();
  td = tr.insertCell();
  td.appendChild(document.createTextNode(trunid));
  td.style.fontWeight = 'bolder';
  td.setAttribute('colSpan', '8');
  // td.verticalAlign = 'top';
  tr = thead.insertRow();
  tr.style.fontWeight = 'bolder';
  td = tr.insertCell();
  td.appendChild(document.createTextNode('Module'));
  td = tr.insertCell();
  td.appendChild(document.createTextNode('Browser'));
  td = tr.insertCell();
  td.appendChild(document.createTextNode('Testcase'));
  td = tr.insertCell();
  td.appendChild(document.createTextNode('Status'));
  td = tr.insertCell();
  td.appendChild(document.createTextNode('Start Time'));
  td = tr.insertCell();
  td.appendChild(document.createTextNode('End Time'));
  td = tr.insertCell();
  td.appendChild(document.createTextNode('Time Taken (ms)'));
  td = tr.insertCell();
  td.appendChild(document.createTextNode('Error Message'));
  ddb.query(params, function (err, data) {
    if (err) console.error(err, err.stack); // an error occurred
    else {
      if ( data.Items.length === 0 ){
        tr = tbl.insertRow();
        td = tr.insertCell();
        td.appendChild(document.createTextNode("Test run " + trunid + " doesn't exists"));
        td.setAttribute('colSpan', '8');
        td.style.color = 'red';
        return tbl
      }
      tdata = data.Items;
      // console.log(tdata);
      for (var i = 0; i < tdata.length; i++) {
        tcdetails = tdata[i].testcaseid.split('-');
        tr = tbl.insertRow();
        td = tr.insertCell();
        td.appendChild(document.createTextNode(tcdetails[0]));
        td = tr.insertCell();
        td.appendChild(document.createTextNode(tcdetails[1]));
        td = tr.insertCell();
        td.appendChild(document.createTextNode(tcdetails[2]));
        td = tr.insertCell();
        td.appendChild(document.createTextNode(tdata[i].details.Status));
        if ( tdata[i].details.Status == 'Passed' ){
          td.style.color = 'green';
        }
        else {
          td.style.color = 'red';
        }
        td = tr.insertCell();
        td.appendChild(document.createTextNode(tdata[i].details.StartTime));
        td = tr.insertCell();
        td.appendChild(document.createTextNode(tdata[i].details.EndTime));
        td = tr.insertCell();
        td.appendChild(document.createTextNode(tdata[i].details.TimeTaken));
        td = tr.insertCell();
        td.appendChild(document.createTextNode(tdata[i].details.ErrorMessage));
      }
    }
  });
  return tbl;
}


function tableCreate() {
  var trunid = document.getElementById("testrunid").value;
  var params = {
    TableName: 'StatusTable-decky',
    KeyConditionExpression: "#testrunid = :trid",
    ExpressionAttributeNames: {
      "#testrunid": "testrunid"
    },
    ExpressionAttributeValues: { 
      ":trid": trunid
    }
  };

  trun_tbl = getdata(trunid, params);
  body.replaceChild(trun_tbl, document.getElementById('testRunTab'));
}

document.addEventListener("DOMContentLoaded", function(event) {
  body = document.body;
  if (firstload == 1){
    testRunTab  = document.createElement('table');
    testRunTab.setAttribute('id', 'testRunTab');
    body.appendChild(testRunTab);
    body.appendChild(document.createElement('br'));
    tableCreate();
    firstload = 0;
  }
});