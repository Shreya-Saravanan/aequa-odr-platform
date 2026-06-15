import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Aequa ODR',
  description: 'AI-assisted online dispute resolution',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="antialiased">{children}</body>
    </html>
  )
}
