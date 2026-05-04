import tailwindcss from '@tailwindcss/vite';
import { defineConfig, ModuleNode, PluginOption } from 'vite';
import solidPlugin from 'vite-plugin-solid';
import {spawn} from "node:child_process"
import chokidar from 'chokidar';

const watchPlugin: PluginOption = {
  name: "vite-plugin-watch",
  configurePreviewServer(){
    // Declaring values
    let timer: NodeJS.Timeout | null = null
    let isBuilding = false

    // A function to add the relevant file to scheduled rebuild
    function scheduleBuild(fileName: string){
      const fileRegex = /(src\/)?.+\.tsx?$/
      if (!fileRegex.test(fileName)) return

      if(timer) clearTimeout(timer)
      timer = setTimeout(() => runBuild(), 60 * 1000)
    }

    // A function that runs the actual build
    function runBuild(){
      if(isBuilding) return
      isBuilding = true

      console.log("Rebuilding...")
      const process = spawn("bun", ["run", "build"], {stdio: "inherit"})
      process.on("exit", (code) => {
        // If build ran well, revalidate
        if(code === 0) isBuilding = false
      })
    }

    // Register the watcher for typescript file changes
    chokidar.watch(".").on("all", (event, path) => {
      if(event === "add" || event === "change" || event === "unlink"){
        scheduleBuild(path)
      }
    })
  }
}

export default defineConfig({
  plugins: [ solidPlugin(), tailwindcss(), watchPlugin ],
  server: {
    port: 3000,
  },
  build: {
    target: 'esnext',
  },
});
