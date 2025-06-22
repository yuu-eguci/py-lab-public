import App from '@/App'
import '@/i18n'
// NOTE: 独自の UI を作る邪魔。
// import '@/index.css'
import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <BrowserRouter basename='/'>
      <App />
    </BrowserRouter>
  </React.StrictMode>
)
