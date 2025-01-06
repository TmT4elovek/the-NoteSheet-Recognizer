import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './css/index.css'
import Entrance from './templates/entrance.jsx'

createRoot(document.getElementById('entrance')).render(
  <StrictMode>
    <Entrance />
  </StrictMode>,
)