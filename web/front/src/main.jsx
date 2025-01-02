import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import LogIn from './login.jsx'

createRoot(document.getElementById('login')).render(
  <StrictMode>
    <LogIn />
  </StrictMode>,
)
