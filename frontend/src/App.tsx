import { Header } from './components/layout/Header'
import { Footer } from './components/layout/Footer'
import { Sidebar } from './components/layout/Sidebar'
import { useAuth } from './context/AuthContext'
import { AuthPage } from './pages/AuthPage'
import { HistoryPage } from './pages/HistoryPage'
import { HomePage } from './pages/HomePage'
import { SpecialistPage } from './pages/SpecialistPage'

import { useState } from 'react'

type PatientView = 'home' | 'history'

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [patientView, setPatientView] = useState<PatientView>('home')
  const [selectedHistoryId, setSelectedHistoryId] = useState<string | null>(null)
  const { user, isLoading } = useAuth()

  const handleNavigate = (view: PatientView, historyId?: string) => {
    setPatientView(view)
    setSelectedHistoryId(historyId ?? null)
  }

  return (
    <div className="min-h-screen flex flex-col bg-slate-50 dark:bg-slate-900 transition-colors">
      <Header onMenuClick={() => setSidebarOpen(!sidebarOpen)} />

      <div className="flex flex-1">
        {user && (
          <Sidebar
            isOpen={sidebarOpen}
            onClose={() => setSidebarOpen(false)}
            activeView={patientView}
            onNavigate={handleNavigate}
          />
        )}

        <main className="flex-1 p-2 sm:p-4 md:p-6 lg:p-8">
          {isLoading ? (
            <div className="max-w-xl mx-auto text-center py-16 text-gray-500">Carregando...</div>
          ) : user ? (
            user.role === 'specialist' ? (
              <SpecialistPage />
            ) : patientView === 'history' ? (
              <HistoryPage
                selectedHistoryId={selectedHistoryId}
                onBackToHome={() => handleNavigate('home')}
              />
            ) : (
              <HomePage onOpenHistoryDocument={(historyId) => handleNavigate('history', historyId)} />
            )
          ) : (
            <AuthPage />
          )}
        </main>
      </div>

      <Footer />
    </div>
  )
}

export default App
