import { Menu, Sun, Moon, Heart } from 'lucide-react'
import { useTheme } from '../../context/ThemeContext'

interface HeaderProps {
  onMenuClick: () => void
}

export function Header({ onMenuClick }: HeaderProps) {
  const { theme, toggleTheme } = useTheme()

  return (
    <header className="gradient-header text-white shadow-lg sticky top-0 z-40">
      <div className="container mx-auto px-3 sm:px-4 py-3 sm:py-4">
        <div className="flex items-center justify-between gap-2">
          {/* Menu mobile */}
          <button
            onClick={onMenuClick}
            className="lg:hidden p-2 -ml-2 rounded-lg hover:bg-white/10 transition-colors"
            aria-label="Abrir menu"
          >
            <Menu size={22} />
          </button>

          {/* Logo e título */}
          <div className="flex items-center gap-2 sm:gap-3 flex-1 min-w-0">
            <Heart
              className="text-red-300 flex-shrink-0"
              size={28}
              fill="currentColor"
            />
            <div className="min-w-0">
              <h1 className="text-lg sm:text-xl md:text-2xl font-bold truncate">
                Traduz Saúde
              </h1>
              <p className="text-[10px] sm:text-xs md:text-sm text-blue-100 hidden xs:block truncate">
                Documentos médicos em linguagem acessível
              </p>
            </div>
          </div>

          {/* Toggle de tema */}
          <button
            onClick={toggleTheme}
            className="p-2 -mr-2 rounded-lg hover:bg-white/10 transition-colors flex-shrink-0"
            aria-label={theme === 'dark' ? 'Ativar tema claro' : 'Ativar tema escuro'}
          >
            {theme === 'dark' ? <Sun size={22} /> : <Moon size={22} />}
          </button>
        </div>
      </div>
    </header>
  )
}
