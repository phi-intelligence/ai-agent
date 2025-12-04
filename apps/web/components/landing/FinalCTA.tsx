'use client'

import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { ArrowRight, Calendar } from 'lucide-react'

export function FinalCTA() {
  const router = useRouter()

  return (
    <section className="py-20 bg-gradient-to-br from-[#0A1A2F] via-[#1a2f4f] to-[#0A1A2F]">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <h2 className="text-4xl md:text-6xl font-bold text-white mb-6">
          Hire your first Virtual Employee today.
        </h2>
        <p className="text-xl md:text-2xl text-[#B5C4D4] mb-12 max-w-2xl mx-auto">
          Start automating real work in minutes — reports, dashboards, analysis, audits, everything.
        </p>

        <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
          <Button
            size="lg"
            className="bg-[#2D8CFF] hover:bg-[#1a6fcc] text-white px-8 py-6 text-lg rounded-lg shadow-lg hover:shadow-xl transition-all"
            onClick={() => router.push('/signup')}
          >
            Get Started (Free)
            <ArrowRight className="ml-2 h-5 w-5" />
          </Button>
          <Button
            size="lg"
            variant="outline"
            className="border-2 border-[#5FFBF1] text-[#5FFBF1] hover:bg-[#5FFBF1] hover:text-[#0A1A2F] px-8 py-6 text-lg rounded-lg"
            onClick={() => router.push('/contact')}
          >
            <Calendar className="mr-2 h-5 w-5" />
            Book a Demo
          </Button>
        </div>

        {/* Visual placeholder */}
        <div className="mt-16 flex justify-center">
          <div className="relative">
            <div className="w-64 h-64 bg-gradient-to-br from-[#2D8CFF]/20 to-[#5FFBF1]/20 rounded-full flex items-center justify-center border-2 border-[#2D8CFF]/30">
              <div className="text-6xl">🤖</div>
            </div>
            <div className="absolute -bottom-4 -right-4 w-32 h-32 bg-gradient-to-br from-[#5FFBF1]/20 to-[#2D8CFF]/20 rounded-full flex items-center justify-center border-2 border-[#5FFBF1]/30">
              <div className="text-4xl">👤</div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}

