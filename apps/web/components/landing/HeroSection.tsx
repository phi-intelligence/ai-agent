'use client'

import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { ArrowRight, Play } from 'lucide-react'

export function HeroSection() {
  const router = useRouter()

  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden bg-gradient-to-br from-[#0A1A2F] via-[#1a2f4f] to-[#0A1A2F]">
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-[#2D8CFF] opacity-20 rounded-full blur-3xl animate-pulse" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-[#5FFBF1] opacity-20 rounded-full blur-3xl animate-pulse delay-1000" />
      </div>

      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 text-center">
        {/* Main Headline */}
        <h1 className="text-5xl md:text-7xl font-bold text-white mb-6 leading-tight">
          Meet Your First
          <br />
          <span className="bg-gradient-to-r from-[#2D8CFF] to-[#5FFBF1] bg-clip-text text-transparent">
            Virtual Employee
          </span>
        </h1>
        
        <p className="text-xl md:text-2xl text-[#B5C4D4] mb-4 max-w-3xl mx-auto">
          An AI-powered worker that performs tasks exactly like a human.
        </p>
        
        <p className="text-lg md:text-xl text-[#B5C4D4] mb-12 max-w-4xl mx-auto leading-relaxed">
          Phi Agents connect to your systems, understand your workflows, audit your warehouse, 
          generate dashboards, analyse CCTV, send emails, build apps, and communicate like a 
          real colleague — 24/7.
        </p>

        {/* CTA Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
          <Button
            size="lg"
            className="bg-[#2D8CFF] hover:bg-[#1a6fcc] text-white px-8 py-6 text-lg rounded-lg shadow-lg hover:shadow-xl transition-all"
            onClick={() => router.push('/signup')}
          >
            Try Phi Agent (Free)
            <ArrowRight className="ml-2 h-5 w-5" />
          </Button>
          <Button
            size="lg"
            variant="outline"
            className="border-2 border-[#5FFBF1] text-[#5FFBF1] hover:bg-[#5FFBF1] hover:text-[#0A1A2F] px-8 py-6 text-lg rounded-lg"
            onClick={() => router.push('/contact')}
          >
            <Play className="mr-2 h-5 w-5" />
            Book a Demo
          </Button>
        </div>

        {/* Visual Placeholder - Animated Grid */}
        <div className="mt-20 relative">
          <div className="grid grid-cols-3 gap-4 max-w-4xl mx-auto">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <div
                key={i}
                className="aspect-square bg-gradient-to-br from-[#2D8CFF]/20 to-[#5FFBF1]/20 rounded-lg border border-[#2D8CFF]/30 backdrop-blur-sm animate-pulse"
                style={{ animationDelay: `${i * 200}ms` }}
              >
                <div className="h-full flex items-center justify-center text-[#5FFBF1] text-2xl">
                  {i === 1 && '📊'}
                  {i === 2 && '🎥'}
                  {i === 3 && '📧'}
                  {i === 4 && '🤖'}
                  {i === 5 && '📈'}
                  {i === 6 && '⚡'}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  )
}

