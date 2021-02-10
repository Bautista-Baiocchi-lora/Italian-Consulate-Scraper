
const venom = require('venom-bot');
var fs = require('fs');

const express = require('express')
const app = express()
const port = 3000

var bodyParser = require('body-parser');
app.use(bodyParser.json());

app.post('/alert', async function (req, res) {

var date = new Date().toLocaleString(); 

var file = fs.createWriteStream('backup.txt', {flags:'a'})
file.write(`Date: ${date}\n`)
file.write(req.body.available.join('\n'))
file.write('\n')
file.end()
  
await venom.create(session='italian messenger', options={
  headless:true,
  useChrome:false,
  disableSpins: true, 
  disableWelcome: true, 
  updatesLog: true, 
  autoClose: 0
})
.then(client => client.sendText(
  '5491131747385@c.us',
`TURNO(s) DISPONIBLE: \n${req.body.available.join('\n')}\n
Datos para ingresar a Cuenta:\nmarisabaiocchi@yahoo.com\nMarisa25\n
https://prenotaonline.esteri.it/login.aspx?cidsede=100076&returnUrl=%2f%2f\n`
)
.then((result) => {
  console.log('Result: ', result); //return object success
  res.send(result)
})
.catch((erro) => {
  console.error('Error when sending: ', erro); //return object error
  res.send(erro)
}))
.catch((erro) => {
console.log(erro);
res.send(erro)
});

})

process.on('unhandledRejection', err => {
  console.log(err)
});

app.listen(port, () => {
  console.log(`App listening at http://localhost:${port}`)
})


