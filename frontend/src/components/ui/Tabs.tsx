import { useState, ReactNode } from 'react'
import { clsx } from 'clsx'

interface Tab {
  id: string
  label: string
  content: ReactNode
  icon?: ReactNode
}

interface TabsProps {
  tabs: Tab[]
  defaultTab?: string
}

export function Tabs({ tabs, defaultTab }: TabsProps) {
  const [activeTab, setActiveTab] = useState(defaultTab || tabs[0]?.id)

  const activeContent = tabs.find((tab) => tab.id === activeTab)?.content

  return (
    <div>
      {/* Tab headers - scrollable on mobile */}
      <div className="relative -mx-4 sm:mx-0">
        <div className="flex border-b border-gray-200 dark:border-gray-700 overflow-x-auto scrollbar-hide px-4 sm:px-0">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={clsx(
                'flex items-center gap-1.5 sm:gap-2 px-3 sm:px-4 py-2.5 sm:py-3 text-xs sm:text-sm font-medium whitespace-nowrap transition-colors',
                'border-b-2 -mb-px flex-shrink-0',
                activeTab === tab.id
                  ? 'border-primary-600 text-primary-600 dark:text-primary-400'
                  : 'border-transparent text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'
              )}
            >
              <span className="[&>svg]:w-4 [&>svg]:h-4 sm:[&>svg]:w-[16px] sm:[&>svg]:h-[16px]">
                {tab.icon}
              </span>
              <span className="hidden xs:inline sm:inline">{tab.label}</span>
              {/* Show abbreviated label on very small screens */}
              <span className="xs:hidden">
                {tab.label.split(' ')[0]}
              </span>
            </button>
          ))}
        </div>
        {/* Gradient fade indicators for scrolling */}
        <div className="absolute right-0 top-0 bottom-0 w-8 bg-gradient-to-l from-white dark:from-gray-800 pointer-events-none sm:hidden" />
      </div>

      {/* Tab content */}
      <div className="pt-4">{activeContent}</div>
    </div>
  )
}
