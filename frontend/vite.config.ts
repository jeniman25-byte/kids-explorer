import { defineConfig } from 'vite'
import uniModule from '@dcloudio/vite-plugin-uni'

const uni = ((uniModule as any).default ?? uniModule) as () => any

export default defineConfig({
  plugins: [uni()],
})
