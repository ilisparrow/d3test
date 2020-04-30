const express = require('express');
const app = express();
const cors = require('cors');
const sql = require('mssql');
const config = require('./config/mysql.json');
const {
  Parser
} = require('json2csv');
const fs = require('fs-extra')
const neatCsv = require('neat-csv');


const fields = ['id', 'device', 'accX', 'accY', 'accZ', 'millis', 'created'];
const opts = {
  fields
};


//TOCHECK : I don't know if this is safe todo.
app.use(cors())

app.use(express.static('Frontend'));



let doconnection = async function (device) {
  console.log('**doconnection');
  try {
    // make sure that any items are correctly URL encoded in the connection string

    let query = `SELECT [id],[device],[accX],[accY],[accZ],[millis],[created],[gyX],[gyY],[gyZ]
    ,[magX],[magY],[magZ],[yaw],[pitch],[roll],[temp] FROM [iot].[pilot_fish] 
    where [device] = '${device}' 
    and created >= '2020-04-27 00:00:00' 
    and created < '2020-04-28 00:00:00'
    order by millis`;

    await sql.connect(config);

    const result = await sql.query(query);

    //`select top 100 * from [iot].[pilot_fish]`; // where [device] = '${device}'`
    //    console.log(result)

    if (result && result.recordsets && result.recordsets[0]) {
      // The result is an object, lets convert to CSV
      const parser = new Parser(opts);
      const csv = parser.parse(result.recordsets[0]);

      // Write it to disk
      let filename = './tmp/data.csv'; // not for production use
      fs.outputFileSync(filename, csv);
      return filename;

    } else {
      return "ooops";
    }
  } catch (err) {
    // ... error checks
    console.log('**error');
    console.error(err);
    throw (err);
  }
}

// process and send the data back
let processdata = async function (filename, _callback) {
  console.log('**processdata');
  const spawn = require('child_process').spawn;

    const process = spawn('python', ['./acce_data_processing.py']);
    console.log('processing....');
    process.stdout.on('data', datao => {

      fs.readFile('./export_dataframe.csv', async (err, data) => {
        if (err) {
          console.error(err)
          return
        }
        _callback(await neatCsv(data));
      })
      
    });
}

let start = async function (req, res) {

  let device = req.query.device || 'pilot02';

  try {
    let filename = await doconnection(device);
    processdata(filename, function(data, error) {
      res.send(data);  
    });

  } catch (err) {
    res.send(err);
  }
}


app.get('/process', start);

app.get('/test', function (req, res) {
  //Executong the python script
  console.log('get');
  const spawn = require('child_process').spawn;
  const process = spawn('python', ['./acce_data_processing.py', './tmp/data.csv']);
  console.log('processing....');
  process.stdout.on('data', data => {
    console.log(data.toString());
    console.log("Data processed succesfully");

    res.send("Data processed succesfully");
  });
})












app.listen(3000, function () {
  console.log('Data processing app started on port 3000')
})