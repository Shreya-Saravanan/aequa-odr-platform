import { CaseProvider } from '@/context/CaseContext'
import Sidebar from '@/components/Sidebar'

export default function CaseLayout({ children }: { children: React.ReactNode }) {
  return (
    <CaseProvider>
      <div className="flex min-h-screen bg-page-gradient">
        <Sidebar />
        <main className="flex-1 overflow-y-auto px-10 py-8 animate-fade-in">
          {children}
        </main>
      </div>
    </CaseProvider>
  )
}
