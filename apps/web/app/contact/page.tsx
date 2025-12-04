'use client'

import { useState } from 'react'
import { Navigation } from '@/components/landing/Navigation'
import { Footer } from '@/components/landing/Footer'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Mail, MessageSquare, Calendar } from 'lucide-react'

export default function ContactPage() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    company: '',
    message: ''
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    // TODO: Implement contact form submission
    alert('Thank you for your interest! We\'ll be in touch soon.')
  }

  return (
    <div className="min-h-screen">
      <Navigation />
      <main className="pt-16 pb-20 bg-gradient-to-br from-[#0A1A2F] to-[#1a2f4f]">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
          <div className="text-center mb-12">
            <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
              Get in Touch
            </h1>
            <p className="text-xl text-[#B5C4D4]">
              Book a demo or ask us anything
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-8 mb-12">
            <Card className="bg-white/5 border-[#2D8CFF]/20 backdrop-blur-sm">
              <CardHeader>
                <Calendar className="h-10 w-10 text-[#5FFBF1] mb-4" />
                <CardTitle className="text-white">Book a Demo</CardTitle>
                <CardDescription className="text-[#B5C4D4]">
                  See Phi Agents in action with a personalized demo
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Button
                  className="w-full bg-[#2D8CFF] hover:bg-[#1a6fcc] text-white"
                  onClick={() => window.open('https://calendly.com/phi-agents', '_blank')}
                >
                  Schedule Demo
                </Button>
              </CardContent>
            </Card>

            <Card className="bg-white/5 border-[#2D8CFF]/20 backdrop-blur-sm">
              <CardHeader>
                <Mail className="h-10 w-10 text-[#5FFBF1] mb-4" />
                <CardTitle className="text-white">Email Us</CardTitle>
                <CardDescription className="text-[#B5C4D4]">
                  Send us a message and we'll respond quickly
                </CardDescription>
              </CardHeader>
              <CardContent>
                <a
                  href="mailto:contact@phiagents.com"
                  className="block text-center text-[#2D8CFF] hover:text-[#5FFBF1] transition-colors"
                >
                  contact@phiagents.com
                </a>
              </CardContent>
            </Card>
          </div>

          <Card className="bg-white/5 border-[#2D8CFF]/20 backdrop-blur-sm">
            <CardHeader>
              <MessageSquare className="h-10 w-10 text-[#5FFBF1] mb-4" />
              <CardTitle className="text-white">Send a Message</CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-4">
                <Input
                  placeholder="Your Name"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="bg-white/10 border-[#2D8CFF]/30 text-white placeholder:text-[#B5C4D4]"
                  required
                />
                <Input
                  type="email"
                  placeholder="Your Email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  className="bg-white/10 border-[#2D8CFF]/30 text-white placeholder:text-[#B5C4D4]"
                  required
                />
                <Input
                  placeholder="Company Name"
                  value={formData.company}
                  onChange={(e) => setFormData({ ...formData, company: e.target.value })}
                  className="bg-white/10 border-[#2D8CFF]/30 text-white placeholder:text-[#B5C4D4]"
                />
                <Textarea
                  placeholder="Your Message"
                  value={formData.message}
                  onChange={(e) => setFormData({ ...formData, message: e.target.value })}
                  className="bg-white/10 border-[#2D8CFF]/30 text-white placeholder:text-[#B5C4D4] min-h-[120px]"
                  required
                />
                <Button
                  type="submit"
                  className="w-full bg-[#2D8CFF] hover:bg-[#1a6fcc] text-white"
                >
                  Send Message
                </Button>
              </form>
            </CardContent>
          </Card>
        </div>
      </main>
      <Footer />
    </div>
  )
}

