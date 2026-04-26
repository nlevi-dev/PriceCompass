import path from 'path'
import fs from 'fs'
import { fileURLToPath } from 'url'
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { viteSingleFile } from 'vite-plugin-singlefile'

const __dirname = path.dirname(fileURLToPath(import.meta.url))

const devDataPlugin = {
    name: 'dev-data',
    configureServer(server) {
        server.middlewares.use('/data', (req, res, next) => {
            const filePath = path.resolve(__dirname, '../deploy/index/data', req.url.slice(1))
            if (fs.existsSync(filePath)) {
                res.setHeader('Content-Type', 'application/octet-stream')
                fs.createReadStream(filePath).pipe(res)
            } else {
                res.statusCode = 404
                res.end()
            }
        })
    }
}

export default defineConfig({
    plugins: [react(), viteSingleFile(), devDataPlugin],
    build: {
        codeSplitting: false,
        assetsInlineLimit: 100000000,
    },
})