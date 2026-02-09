import { ReactNode } from 'react'
import { clsx } from 'clsx'
import { AlertTriangle, Info, CheckCircle, XCircle } from 'lucide-react'

interface AlertProps {
  variant?: 'info' | 'success' | 'warning' | 'error'
  title?: string
  children: ReactNode
  className?: string
}

const variants = {
  info: {
    container: 'bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800',
    icon: 'text-blue-600 dark:text-blue-400',
    title: 'text-blue-800 dark:text-blue-200',
    text: 'text-blue-700 dark:text-blue-300',
    Icon: Info,
  },
  success: {
    container: 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800',
    icon: 'text-green-600 dark:text-green-400',
    title: 'text-green-800 dark:text-green-200',
    text: 'text-green-700 dark:text-green-300',
    Icon: CheckCircle,
  },
  warning: {
    container: 'bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-800',
    icon: 'text-yellow-600 dark:text-yellow-400',
    title: 'text-yellow-800 dark:text-yellow-200',
    text: 'text-yellow-700 dark:text-yellow-300',
    Icon: AlertTriangle,
  },
  error: {
    container: 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800',
    icon: 'text-red-600 dark:text-red-400',
    title: 'text-red-800 dark:text-red-200',
    text: 'text-red-700 dark:text-red-300',
    Icon: XCircle,
  },
}

export function Alert({ variant = 'info', title, children, className }: AlertProps) {
  const styles = variants[variant]
  const Icon = styles.Icon

  return (
    <div
      className={clsx(
        'flex gap-3 p-4 rounded-lg border',
        styles.container,
        className
      )}
    >
      <Icon className={clsx('flex-shrink-0', styles.icon)} size={20} />
      <div>
        {title && (
          <h4 className={clsx('font-semibold mb-1', styles.title)}>{title}</h4>
        )}
        <div className={clsx('text-sm', styles.text)}>{children}</div>
      </div>
    </div>
  )
}
