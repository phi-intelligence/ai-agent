'use client'

import { Card, CardContent } from '@/components/ui/card'
import { Database, Eye, BarChart3, MessageSquare, Shield } from 'lucide-react'

const features = [
  {
    icon: Database,
    title: 'Uses your systems like an employee',
    description: 'Logs into web apps, downloads reports, fills forms, sends emails, reads dashboards.',
    color: 'text-[#2D8CFF]'
  },
  {
    icon: Eye,
    title: 'Sees your warehouse',
    description: 'Analyses CCTV, detects defects, monitors worker safety.',
    color: 'text-[#5FFBF1]'
  },
  {
    icon: BarChart3,
    title: 'Builds dashboards & apps automatically',
    description: 'If your company doesn\'t have reporting tools, your agent generates them instantly.',
    color: 'text-[#2D8CFF]'
  },
  {
    icon: MessageSquare,
    title: 'Human-like communication',
    description: 'Talks via text and voice, sends updates, asks clarifying questions.',
    color: 'text-[#5FFBF1]'
  },
  {
    icon: Shield,
    title: 'Runs locally & respects data boundaries',
    description: 'Your data never leaves your environment. Agent executes tasks on-prem.',
    color: 'text-[#2D8CFF]'
  }
]

export function TheDifference() {
  return (
    <section className="py-20 bg-gradient-to-br from-[#0A1A2F] to-[#1a2f4f]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
            The Difference: Not a Chatbot.
            <br />
            <span className="bg-gradient-to-r from-[#2D8CFF] to-[#5FFBF1] bg-clip-text text-transparent">
              A Real Worker.
            </span>
          </h2>
          <p className="text-xl text-[#B5C4D4] max-w-3xl mx-auto mt-6">
            What makes Phi Agents unique?
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feature, index) => {
            const Icon = feature.icon
            return (
              <Card key={index} className="bg-white/5 border border-[#2D8CFF]/20 backdrop-blur-sm hover:bg-white/10 transition-all">
                <CardContent className="p-6">
                  <Icon className={`h-10 w-10 ${feature.color} mb-4`} />
                  <h3 className="text-xl font-bold text-white mb-3">
                    {feature.title}
                  </h3>
                  <p className="text-[#B5C4D4] leading-relaxed">
                    {feature.description}
                  </p>
                </CardContent>
              </Card>
            )
          })}
        </div>

        {/* Split-screen visual placeholder */}
        <div className="mt-16 grid md:grid-cols-2 gap-8">
          <Card className="bg-red-500/10 border-red-500/30">
            <CardContent className="p-8 text-center">
              <h3 className="text-2xl font-bold text-red-400 mb-4">❌ Chatbot</h3>
              <p className="text-[#B5C4D4]">Limited to text responses. Can't access your systems.</p>
            </CardContent>
          </Card>
          <Card className="bg-green-500/10 border-green-500/30">
            <CardContent className="p-8 text-center">
              <h3 className="text-2xl font-bold text-green-400 mb-4">✅ Virtual Employee</h3>
              <p className="text-[#B5C4D4]">Full system access. Works like a real teammate.</p>
            </CardContent>
          </Card>
        </div>
      </div>
    </section>
  )
}

