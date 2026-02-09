import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ThemeProvider } from '../context/ThemeContext'
import { UsageProvider } from '../context/UsageContext'
import App from '../App'

// Mock do localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
}
Object.defineProperty(window, 'localStorage', { value: localStorageMock })

// Mock do matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation((query) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
})

function renderWithProviders(ui: React.ReactElement) {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  })

  return render(
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <UsageProvider>{ui}</UsageProvider>
      </ThemeProvider>
    </QueryClientProvider>
  )
}

describe('App', () => {
  it('renders the header with app name', () => {
    renderWithProviders(<App />)
    expect(screen.getByText('Traduz Saúde')).toBeInTheDocument()
  })

  it('shows terms acceptance on first load', () => {
    renderWithProviders(<App />)
    expect(screen.getByText('Bem-vindo ao Traduz Saúde')).toBeInTheDocument()
  })

  it('shows terms checkbox', () => {
    renderWithProviders(<App />)
    expect(
      screen.getByText(/Li e concordo com os termos de uso/)
    ).toBeInTheDocument()
  })
})
