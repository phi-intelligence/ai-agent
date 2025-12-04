'use client'

import { Card, CardContent } from '@/components/ui/card'
import { UserPlus, Plug, Rocket } from 'lucide-react'

const steps = [
  {
    number: '1',
    icon: UserPlus,
    title: 'Create your Virtual Employee',
    description: 'Pick a role — Warehouse Analyst, Safety Officer, Ops Manager, HR Assistant, etc.',
    color: 'from-[#2D8CFF] to-[#1a6fcc]'
  },
  {
    number: '2',
    icon: Plug,
    title: 'Connect your tools',
    description: 'Give it access to WMS, ERP, CCTV, files, databases, email, browser.',
    color: 'from-[#5FFBF1] to-[#4dd9c7]'
  },
  {
    number: '3',
    icon: Rocket,
    title: 'It starts working like a real teammate',
    description: 'Your agent performs tasks, communicates, builds dashboards, and sends updates with ETA — exactly like a human.',
    color: 'from-[#2D8CFF] to-[#5FFBF1]'
  }
]

export function HowItWorks() {
  return (
    <section className="py-20 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-[#0A1A2F] mb-4">
            How It Works
          </h2>
          <p className="text-xl text-[#B5C4D4] max-w-2xl mx-auto">
            Three simple steps to get your virtual employee working
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          {steps.map((step, index) => {
            const Icon = step.icon
            return (
              <Card key={index} className="border-2 hover:border-[#2D8CFF] transition-all hover:shadow-xl">
                <CardContent className="p-8">
                  <div className="flex items-center mb-6">
                    <div className={`w-16 h-16 rounded-full bg-gradient-to-br ${step.color} flex items-center justify-center text-white text-2xl font-bold mr-4`}>
                      {step.number}
                    </div>
                    <Icon className="h-8 w-8 text-[#2D8CFF]" />
                  </div>
                  <h3 className="text-2xl font-bold text-[#0A1A2F] mb-4">
                    {step.title}
                  </h3>
                  <p className="text-[#B5C4D4] text-lg leading-relaxed">
                    {step.description}
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

