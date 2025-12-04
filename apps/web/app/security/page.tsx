'use client'

import { Navigation } from '@/components/landing/Navigation'
import { SecurityTrust } from '@/components/landing/SecurityTrust'
import { Footer } from '@/components/landing/Footer'

export default function SecurityPage() {
  return (
    <div className="min-h-screen">
      <Navigation />
      <main>
        <SecurityTrust />
      </main>
      <Footer />
    </div>
  )
}

