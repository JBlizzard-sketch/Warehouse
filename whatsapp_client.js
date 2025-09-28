const { Client } = require('whatsapp-web.js');
const qrcode = require('qrcode');
const fs = require('fs');

const number = process.argv[2] || process.env.WHATSAPP_NUMBER;
const sessionPath = ./data/whatsapp_session_${number}.json;

const client = new Client({ session: fs.existsSync(sessionPath) ? JSON.parse(fs.readFileSync(sessionPath)) : {} });

client.on('qr', (qr) => {
qrcode.toFile(./data/qr_${number}.txt, qr, (err) => {
if (err) console.error('QR error:', err);
else console.log(QR code saved to ./data/qr_${number}.txt);
});
});

client.on('authenticated', (session) => {
fs.writeFileSync(sessionPath, JSON.stringify(session));
console.log('Authenticated');
});

client.on('message', async (msg) => {
if (msg.body.startsWith('query:')) {
console.log(Query from ${msg.from}: ${msg.body});
// Forward to TG (handled by Orchestrator)
}
});

client.initialize();

if (process.argv[3]) {
client.sendMessage(process.argv[2], process.argv[3]).then(() => {
console.log('Message sent');
}).catch((err) => {
console.error('Message error:', err);
});
}
