'use client'

import { Navigation } from '@/components/landing/Navigation'
import { DemoSection } from '@/components/landing/DemoSection'
import { Footer } from '@/components/landing/Footer'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { useRouter } from 'next/navigation'

export default function DemoPage() {
  const router = useRouter()

  return (
    <div className="min-h-screen">
      <Navigation />
      <main className="pt-16">
        <DemoSection />
        
        {/* Additional demo content */}
        <section className="py-20 bg-gradient-to-br from-[#0A1A2F] to-[#1a2f4f]">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-12">
              <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
                Interactive Demo
              </h2>
              <p className="text-xl text-[#B5C4D4] max-w-2xl mx-auto">
                Try Phi Agents yourself
              </p>
            </div>

            <Card className="bg-white/5 border-[#2D8CFF]/20 backdrop-blur-sm max-w-2xl mx-auto">
              <CardContent className="p-8">
                <p className="text-white text-center mb-6">
                  To try Phi Agents with a live demo, please sign up for a free account.
                </p>
                <div className="flex flex-col sm:flex-row gap-4 justify-center">
                  <Button
                    className="bg-[#2D8CFF] hover:bg-[#1a6fcc] text-white"
                    onClick={() => router.push('/signup')}
                  >
                    Sign Up Free
                  </Button>
                  <Button
                    variant="outline"
                    className="border-[#5FFBF1] text-[#5FFBF1] hover:bg-[#5FFBF1] hover:text-[#0A1A2F]"
                    onClick={() => router.push('/contact')}
                  >
                    Book a Demo
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        </section>
      </main>
      <Footer />
    </div>
  )
}

