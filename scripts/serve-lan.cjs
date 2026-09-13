const https = require('node:https');
const fs = require('node:fs');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const host = process.argv[2] || '127.0.0.1';
const assets = new Map([
 ['/', ['index.html', 'text/html; charset=utf-8']],
 ['/index.html', ['index.html', 'text/html; charset=utf-8']],
 ['/style.css', ['style.css', 'text/css; charset=utf-8']],
 ['/room.js', ['room.js', 'text/javascript; charset=utf-8']],
 ['/aframe.min.js', ['aframe.min.js', 'text/javascript; charset=utf-8']],
 ['/pokoj.glb', ['pokoj.glb', 'model/gltf-binary']]
]);
const server = https.createServer({
 key: fs.readFileSync(path.join(root,'.local-vr/key.pem')),
 cert: fs.readFileSync(path.join(root,'.local-vr/cert.pem')),
 minVersion: 'TLSv1.2'
}, (req, res) => {
 if (!['GET','HEAD'].includes(req.method)) {res.writeHead(405, {Allow:'GET, HEAD'});res.end();return;}
 let asset;try {asset=assets.get(new URL(req.url,'https://localhost').pathname);}catch {res.writeHead(400);res.end();return;}
 if(!asset){res.writeHead(404);res.end('Not found');return;}
 const file=path.join(root,'dist',asset[0]);
 fs.stat(file,(error,stat)=>{
  if(error){res.writeHead(404);res.end();return;}
  res.writeHead(200,{'Content-Type':asset[1],'Content-Length':stat.size,'Cache-Control':'no-cache','X-Content-Type-Options':'nosniff','Permissions-Policy':'xr-spatial-tracking=(self)'});
  if(req.method==='HEAD'){res.end();return;}
  const stream=fs.createReadStream(file);stream.on('error',()=>res.destroy());stream.pipe(res);
 });
});
server.on('error',error=>{console.error(error.message);process.exit(1);});
server.listen(8443,host,()=>console.log(`Komnata VR: https://${host}:8443`));
