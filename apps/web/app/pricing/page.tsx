'use client'

import { Navigation } from '@/components/landing/Navigation'
import { PricingSection } from '@/components/landing/PricingSection'
import { Footer } from '@/components/landing/Footer'

export default function PricingPage() {
  return (
    <div className="min-h-screen">
      <Navigation />
      <main>
        <PricingSection />
      </main>
      <Footer />
    </div>
  )
}

