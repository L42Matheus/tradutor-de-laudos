import { useState } from 'react'
import { Header } from './components/layout/Header'
import { Footer } from './components/layout/Footer'
import { Sidebar } from './components/layout/Sidebar'
import { HomePage } from './pages/HomePage'
import { TermsAcceptance } from './components/terms/TermsAcceptance'

function App() {
  const [termsAccepted, setTermsAccepted] = useState(false)
  const [sidebarOpen, setSidebarOpen] = useState(false)

  return (
    <div className="min-h-screen flex flex-col">
      <Header onMenuClick={() => setSidebarOpen(!sidebarOpen)} />

      <div className="flex flex-1">
        <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

        <main className="flex-1 p-4 md:p-6 lg:p-8">
          {!termsAccepted ? (
            <TermsAcceptance onAccept={() => setTermsAccepted(true)} />
          ) : (
            <HomePage />
          )}
        </main>
      </div>

      <Footer />
    </div>
  )
}

export default App
