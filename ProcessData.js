
const express = require('express')
const app = express()
var cors = require('cors')

//TOCHECK : I don't know if this is safe todo.
app.use(cors())

app.get('/', function (req, res) {
//Executong the python script
const spawn = require('child_process').spawn;
const process = spawn('python',['./acce_data_processing.py']);
process.stdout.on('data',data =>{console.log(data.toString());});

console.log("Data processed succesfully");

})

app.listen(3000, function () {
  console.log('Data processing app started on port 3000')
})

