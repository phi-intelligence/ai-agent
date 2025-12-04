'use client'

import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Menu, X } from 'lucide-react'
import { useState } from 'react'

export function Navigation() {
  const router = useRouter()
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-[#0A1A2F]/95 backdrop-blur-sm border-b border-[#2D8CFF]/20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center">
            <button
              onClick={() => router.push('/')}
              className="text-2xl font-bold bg-gradient-to-r from-[#2D8CFF] to-[#5FFBF1] bg-clip-text text-transparent"
            >
              Phi Agents
            </button>
          </div>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-8">
            <button
              onClick={() => router.push('/#features')}
              className="text-[#B5C4D4] hover:text-white transition-colors"
            >
              Features
            </button>
            <button
              onClick={() => router.push('/#use-cases')}
              className="text-[#B5C4D4] hover:text-white transition-colors"
            >
              Use Cases
            </button>
            <button
              onClick={() => router.push('/pricing')}
              className="text-[#B5C4D4] hover:text-white transition-colors"
            >
              Pricing
            </button>
            <button
              onClick={() => router.push('/security')}
              className="text-[#B5C4D4] hover:text-white transition-colors"
            >
              Security
            </button>
            <Button
              variant="outline"
              className="border-[#2D8CFF] text-[#2D8CFF] hover:bg-[#2D8CFF] hover:text-white"
              onClick={() => router.push('/login')}
            >
              Login
            </Button>
            <Button
              className="bg-[#2D8CFF] hover:bg-[#1a6fcc] text-white"
              onClick={() => router.push('/signup')}
            >
              Get Started
            </Button>
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden">
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="text-white"
            >
              {mobileMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
            </button>
          </div>
        </div>

        {/* Mobile Navigation */}
        {mobileMenuOpen && (
          <div className="md:hidden py-4 space-y-4">
            <button
              onClick={() => {
                router.push('/#features')
                setMobileMenuOpen(false)
              }}
              className="block text-[#B5C4D4] hover:text-white transition-colors"
            >
              Features
            </button>
            <button
              onClick={() => {
                router.push('/#use-cases')
                setMobileMenuOpen(false)
              }}
              className="block text-[#B5C4D4] hover:text-white transition-colors"
            >
              Use Cases
            </button>
            <button
              onClick={() => {
                router.push('/pricing')
                setMobileMenuOpen(false)
              }}
              className="block text-[#B5C4D4] hover:text-white transition-colors"
            >
              Pricing
            </button>
            <button
              onClick={() => {
                router.push('/security')
                setMobileMenuOpen(false)
              }}
              className="block text-[#B5C4D4] hover:text-white transition-colors"
            >
              Security
            </button>
            <div className="flex flex-col space-y-2 pt-4">
              <Button
                variant="outline"
                className="border-[#2D8CFF] text-[#2D8CFF] hover:bg-[#2D8CFF] hover:text-white"
                onClick={() => {
                  router.push('/login')
                  setMobileMenuOpen(false)
                }}
              >
                Login
              </Button>
              <Button
                className="bg-[#2D8CFF] hover:bg-[#1a6fcc] text-white"
                onClick={() => {
                  router.push('/signup')
                  setMobileMenuOpen(false)
                }}
              >
                Get Started
              </Button>
            </div>
          </div>
        )}
      </div>
    </nav>
  )
}

