'use client'

import { Card, CardContent } from '@/components/ui/card'
import { Shield, Lock, FileText, CheckCircle } from 'lucide-react'

const securityFeatures = [
  {
    icon: Shield,
    title: 'All execution happens locally',
    description: 'Agents run on your machines — not in the cloud.',
    color: 'text-[#2D8CFF]'
  },
  {
    icon: Lock,
    title: 'Fine-grained permission control',
    description: 'Admins choose which tools the agent can access.',
    color: 'text-[#5FFBF1]'
  },
  {
    icon: FileText,
    title: 'Audit logs',
    description: 'Every action is traceable.',
    color: 'text-[#2D8CFF]'
  },
  {
    icon: CheckCircle,
    title: 'Compatible with SOC2, ISO27001',
    description: 'Alignment-ready for enterprise compliance.',
    color: 'text-[#5FFBF1]'
  }
]

export function SecurityTrust() {
  return (
    <section className="py-20 bg-gradient-to-br from-[#0A1A2F] to-[#1a2f4f]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
            Security & Trust
          </h2>
          <p className="text-xl text-[#B5C4D4] max-w-2xl mx-auto">
            Enterprise-grade security built in
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          {securityFeatures.map((feature, index) => {
            const Icon = feature.icon
            return (
              <Card key={index} className="bg-white/5 border border-[#2D8CFF]/20 backdrop-blur-sm hover:bg-white/10 transition-all">
                <CardContent className="p-6 text-center">
                  <Icon className={`h-12 w-12 ${feature.color} mx-auto mb-4`} />
                  <h3 className="text-lg font-bold text-white mb-3">
                    {feature.title}
                  </h3>
                  <p className="text-[#B5C4D4] text-sm">
                    {feature.description}
                  </p>
                </CardContent>
              </Card>
            )
          })}
        </div>
      </div>
    </section>
  )
}

