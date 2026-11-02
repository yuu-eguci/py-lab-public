import react from '@vitejs/plugin-react-swc'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    // tsconfig の paths (@/* -> src/*) を Vite でも使います。
    tsconfigPaths: true,
  },
})
