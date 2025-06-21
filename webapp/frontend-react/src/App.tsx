import "@/App.css"
import HomePage from "@/pages/HomePage"
import NotFoundPage from "@/pages/NotFoundPage"
import { Route, Routes } from "react-router-dom"

function App() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      {/* その他のパスは 404 */}
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  )
}

export default App

