'use client'

import { useRouter } from 'next/navigation'
import { Github, Twitter, Linkedin, Mail } from 'lucide-react'

export function Footer() {
  const router = useRouter()

  return (
    <footer className="bg-[#0A1A2F] border-t border-[#2D8CFF]/20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid md:grid-cols-4 gap-8">
          <div>
            <h3 className="text-2xl font-bold bg-gradient-to-r from-[#2D8CFF] to-[#5FFBF1] bg-clip-text text-transparent mb-4">
              Phi Agents
            </h3>
            <p className="text-[#B5C4D4] text-sm">
              The world's first realistic AI employee that performs the full job, not just chat.
            </p>
          </div>

          <div>
            <h4 className="text-white font-semibold mb-4">Product</h4>
            <ul className="space-y-2">
              <li>
                <button
                  onClick={() => router.push('/#features')}
                  className="text-[#B5C4D4] hover:text-white text-sm transition-colors"
                >
                  Features
                </button>
              </li>
              <li>
                <button
                  onClick={() => router.push('/pricing')}
                  className="text-[#B5C4D4] hover:text-white text-sm transition-colors"
                >
                  Pricing
                </button>
              </li>
              <li>
                <button
                  onClick={() => router.push('/security')}
                  className="text-[#B5C4D4] hover:text-white text-sm transition-colors"
                >
                  Security
                </button>
              </li>
            </ul>
          </div>

          <div>
            <h4 className="text-white font-semibold mb-4">Company</h4>
            <ul className="space-y-2">
              <li>
                <button
                  onClick={() => router.push('/contact')}
                  className="text-[#B5C4D4] hover:text-white text-sm transition-colors"
                >
                  Contact
                </button>
              </li>
              <li>
                <button
                  onClick={() => router.push('/demo')}
                  className="text-[#B5C4D4] hover:text-white text-sm transition-colors"
                >
                  Demo
                </button>
              </li>
            </ul>
          </div>

          <div>
            <h4 className="text-white font-semibold mb-4">Connect</h4>
            <div className="flex space-x-4">
              <a href="#" className="text-[#B5C4D4] hover:text-[#2D8CFF] transition-colors">
                <Twitter className="h-5 w-5" />
              </a>
              <a href="#" className="text-[#B5C4D4] hover:text-[#2D8CFF] transition-colors">
                <Linkedin className="h-5 w-5" />
              </a>
              <a href="#" className="text-[#B5C4D4] hover:text-[#2D8CFF] transition-colors">
                <Github className="h-5 w-5" />
              </a>
              <a href="#" className="text-[#B5C4D4] hover:text-[#2D8CFF] transition-colors">
                <Mail className="h-5 w-5" />
              </a>
            </div>
          </div>
        </div>

        <div className="mt-8 pt-8 border-t border-[#2D8CFF]/20 text-center">
          <p className="text-[#B5C4D4] text-sm">
            © 2024 Phi Agents. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  )
}

