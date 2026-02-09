import { Menu, Sun, Moon, Heart } from 'lucide-react'
import { useTheme } from '../../context/ThemeContext'

interface HeaderProps {
  onMenuClick: () => void
}

export function Header({ onMenuClick }: HeaderProps) {
  const { theme, toggleTheme } = useTheme()

  return (
    <header className="gradient-header text-white shadow-lg">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          {/* Menu mobile */}
          <button
            onClick={onMenuClick}
            className="lg:hidden p-2 rounded-lg hover:bg-white/10 transition-colors"
            aria-label="Abrir menu"
          >
            <Menu size={24} />
          </button>

          {/* Logo e título */}
          <div className="flex items-center gap-3">
            <Heart className="text-red-300" size={32} fill="currentColor" />
            <div>
              <h1 className="text-xl md:text-2xl font-bold">Traduz Saúde</h1>
              <p className="text-xs md:text-sm text-blue-100 hidden sm:block">
                Documentos médicos em linguagem acessível
              </p>
            </div>
          </div>

          {/* Toggle de tema */}
          <button
            onClick={toggleTheme}
            className="p-2 rounded-lg hover:bg-white/10 transition-colors"
            aria-label={theme === 'dark' ? 'Ativar tema claro' : 'Ativar tema escuro'}
          >
            {theme === 'dark' ? <Sun size={24} /> : <Moon size={24} />}
          </button>
        </div>
      </div>
    </header>
  )
}
