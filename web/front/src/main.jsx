import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import Entrance from './entrance.jsx'

createRoot(document.getElementById('entrance')).render(
  <StrictMode>
    <Entrance />
  </StrictMode>,
)