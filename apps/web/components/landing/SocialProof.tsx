'use client'

import { Card, CardContent } from '@/components/ui/card'
import { CheckCircle } from 'lucide-react'

const claims = [
  'Designed for modern warehouses',
  'Supports CCTV, WMS, ERP, BI systems',
  'Battle-tested workflows',
  'Enterprise-ready architecture'
]

export function SocialProof() {
  return (
    <section className="py-20 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h2 className="text-3xl md:text-4xl font-bold text-[#0A1A2F] mb-4">
            Trusted by Industry Leaders
          </h2>
          <p className="text-lg text-[#B5C4D4] max-w-2xl mx-auto">
            Built for the most demanding operational environments
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          {claims.map((claim, index) => (
            <Card key={index} className="border-2 border-gray-200 hover:border-[#2D8CFF] transition-all">
              <CardContent className="p-6 flex items-center">
                <CheckCircle className="h-6 w-6 text-green-500 mr-3 flex-shrink-0" />
                <p className="text-[#0A1A2F] font-medium">{claim}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  )
}

