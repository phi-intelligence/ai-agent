'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Check, X } from 'lucide-react'
import { useRouter } from 'next/navigation'

const plans = [
  {
    name: 'Starter',
    price: 'Free',
    period: '',
    features: [
      { text: '1 virtual employee', included: true },
      { text: '1 workflow', included: true },
      { text: 'No CCTV', included: true },
      { text: 'Basic support', included: true }
    ],
    cta: 'Get Started',
    color: 'from-[#B5C4D4] to-[#8a9ba8]'
  },
  {
    name: 'Pro',
    price: '£99',
    period: '/month per agent',
    features: [
      { text: 'Up to 5 workflows', included: true },
      { text: 'Local agent runtime', included: true },
      { text: 'Dashboard builder', included: true },
      { text: 'Slack/Email integration', included: true },
      { text: 'Priority support', included: true },
      { text: 'CCTV integration', included: false }
    ],
    cta: 'Start Free Trial',
    color: 'from-[#2D8CFF] to-[#1a6fcc]',
    popular: true
  },
  {
    name: 'Enterprise',
    price: 'Custom',
    period: '',
    features: [
      { text: 'Unlimited agents', included: true },
      { text: 'Full CCTV integration', included: true },
      { text: 'On-prem GPU', included: true },
      { text: 'Advanced workflows', included: true },
      { text: 'Priority SLAs', included: true },
      { text: 'Dedicated support', included: true }
    ],
    cta: 'Contact Sales',
    color: 'from-[#5FFBF1] to-[#4dd9c7]'
  }
]

export function PricingSection() {
  const router = useRouter()

  return (
    <section className="py-20 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-[#0A1A2F] mb-4">
            Pricing
          </h2>
          <p className="text-xl text-[#B5C4D4] max-w-2xl mx-auto">
            Choose the plan that fits your needs
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          {plans.map((plan, index) => (
            <Card
              key={index}
              className={`border-2 transition-all ${
                plan.popular
                  ? 'border-[#2D8CFF] shadow-xl scale-105'
                  : 'border-gray-200 hover:border-[#2D8CFF]'
              }`}
            >
              {plan.popular && (
                <div className="bg-gradient-to-r from-[#2D8CFF] to-[#5FFBF1] text-white text-center py-2 text-sm font-semibold">
                  Most Popular
                </div>
              )}
              <CardHeader className="text-center pb-4">
                <CardTitle className="text-2xl font-bold text-[#0A1A2F] mb-2">
                  {plan.name}
                </CardTitle>
                <div className="flex items-baseline justify-center">
                  <span className="text-4xl font-bold text-[#0A1A2F]">
                    {plan.price}
                  </span>
                  {plan.period && (
                    <span className="text-[#B5C4D4] ml-2">{plan.period}</span>
                  )}
                </div>
              </CardHeader>
              <CardContent>
                <ul className="space-y-4 mb-8">
                  {plan.features.map((feature, featureIndex) => (
                    <li key={featureIndex} className="flex items-start">
                      {feature.included ? (
                        <Check className="h-5 w-5 text-green-500 mr-3 flex-shrink-0 mt-0.5" />
                      ) : (
                        <X className="h-5 w-5 text-gray-400 mr-3 flex-shrink-0 mt-0.5" />
                      )}
                      <span className={feature.included ? 'text-[#0A1A2F]' : 'text-[#B5C4D4]'}>
                        {feature.text}
                      </span>
                    </li>
                  ))}
                </ul>
                <Button
                  className={`w-full bg-gradient-to-r ${plan.color} text-white hover:opacity-90`}
                  onClick={() => {
                    if (plan.name === 'Enterprise') {
                      router.push('/contact')
                    } else {
                      router.push('/signup')
                    }
                  }}
                >
                  {plan.cta}
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  )
}

