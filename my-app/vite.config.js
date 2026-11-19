import adapterAuto from '@sveltejs/adapter-auto';
import adapterStatic from '@sveltejs/adapter-static';
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

// 'npm run build:movil' genera una app estática en build/ para empaquetarla con Capacitor (APK).
const esMovil = process.argv.includes('movil') || process.env.MOVIL === '1';

export default defineConfig({
	plugins: [
		sveltekit({
			compilerOptions: {
				runes: ({ filename }) =>
					filename.split(/[/\\]/).includes('node_modules') ? undefined : true
			},
			adapter: esMovil ? adapterStatic({ pages: 'build', assets: 'build', fallback: 'index.html', strict: false }) : adapterAuto()
		})
	]
});
