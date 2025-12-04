'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Warehouse, Factory, ShoppingCart, Briefcase } from 'lucide-react'

const useCases = [
  {
    icon: Warehouse,
    title: 'Warehouse & Logistics',
    items: [
      'Daily operations reporting',
      'CCTV safety compliance',
      'Stock level prediction',
      'Worker productivity scoring'
    ],
    color: 'from-[#2D8CFF] to-[#1a6fcc]'
  },
  {
    icon: Factory,
    title: 'Manufacturing',
    items: [
      'Defect detection',
      'Line performance analytics'
    ],
    color: 'from-[#5FFBF1] to-[#4dd9c7]'
  },
  {
    icon: ShoppingCart,
    title: 'Retail',
    items: [
      'Inventory auditing',
      'Theft/safety monitoring'
    ],
    color: 'from-[#2D8CFF] to-[#5FFBF1]'
  },
  {
    icon: Briefcase,
    title: 'Corporate Roles',
    items: [
      'HR assistant',
      'Data analyst',
      'Finance operations',
      'Compliance reviewer'
    ],
    color: 'from-[#5FFBF1] to-[#2D8CFF]'
  }
]

export function UseCases() {
  return (
    <section className="py-20 bg-gradient-to-br from-[#0A1A2F] to-[#1a2f4f]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
            Use Cases
          </h2>
          <p className="text-xl text-[#B5C4D4] max-w-2xl mx-auto">
            Phi Agents work across industries and roles
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          {useCases.map((useCase, index) => {
            const Icon = useCase.icon
            return (
              <Card key={index} className="bg-white/5 border border-[#2D8CFF]/20 backdrop-blur-sm hover:bg-white/10 transition-all">
                <CardHeader>
                  <div className={`w-12 h-12 rounded-lg bg-gradient-to-br ${useCase.color} flex items-center justify-center mb-4`}>
                    <Icon className="h-6 w-6 text-white" />
                  </div>
                  <CardTitle className="text-xl font-bold text-white">
                    {useCase.title}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-2">
                    {useCase.items.map((item, itemIndex) => (
                      <li key={itemIndex} className="text-[#B5C4D4] flex items-start">
                        <span className="text-[#5FFBF1] mr-2">•</span>
                        {item}
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            )
          })}
        </div>
      </div>
    </section>
  )
}

