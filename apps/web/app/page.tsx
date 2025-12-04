'use client'

import { Navigation } from '@/components/landing/Navigation'
import { HeroSection } from '@/components/landing/HeroSection'
import { HowItWorks } from '@/components/landing/HowItWorks'
import { TheDifference } from '@/components/landing/TheDifference'
import { FeatureGrid } from '@/components/landing/FeatureGrid'
import { UseCases } from '@/components/landing/UseCases'
import { DemoSection } from '@/components/landing/DemoSection'
import { PricingSection } from '@/components/landing/PricingSection'
import { SecurityTrust } from '@/components/landing/SecurityTrust'
import { SocialProof } from '@/components/landing/SocialProof'
import { FinalCTA } from '@/components/landing/FinalCTA'
import { Footer } from '@/components/landing/Footer'

export default function LandingPage() {
  return (
    <div className="min-h-screen">
      <Navigation />
      <main>
        <HeroSection />
        <div id="features">
          <HowItWorks />
        </div>
        <TheDifference />
        <FeatureGrid />
        <div id="use-cases">
          <UseCases />
        </div>
        <DemoSection />
        <PricingSection />
        <SecurityTrust />
        <SocialProof />
        <FinalCTA />
      </main>
      <Footer />
    </div>
  )
}
