// Permite que el APK llame a la API por http (por ejemplo http://192.168.1.50:8000).
// Android bloquea http por defecto; esto agrega android:usesCleartextTraffic="true".
const fs = require('fs');
const ruta = 'android/app/src/main/AndroidManifest.xml';
if (!fs.existsSync(ruta)) {
	console.error('Primero ejecuta: npx cap add android');
	process.exit(1);
}
let xml = fs.readFileSync(ruta, 'utf8');
if (!xml.includes('usesCleartextTraffic')) {
	xml = xml.replace('<application', '<application\n        android:usesCleartextTraffic="true"');
	fs.writeFileSync(ruta, xml);
	console.log('Listo: el APK puede usar la API por http.');
} else {
	console.log('El permiso http ya estaba activo.');
}
