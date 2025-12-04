'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { 
  Workflow, 
  Camera, 
  Wrench, 
  BarChart3, 
  MessageCircle, 
  Server 
} from 'lucide-react'

const features = [
  {
    icon: Workflow,
    title: 'Autonomous Workflows',
    items: [
      'Daily warehouse reports',
      'Safety audits',
      'Inventory accuracy checks',
      'Pick route optimization',
      'Bottleneck detection',
      'Labour productivity analysis'
    ],
    color: 'from-[#2D8CFF] to-[#1a6fcc]'
  },
  {
    icon: Camera,
    title: 'Computer Vision Engine',
    items: [
      'CCTV anomaly detection',
      'Safety violation monitoring',
      'Pallet/box defect recognition',
      'Worker PPE detection'
    ],
    color: 'from-[#5FFBF1] to-[#4dd9c7]'
  },
  {
    icon: Wrench,
    title: 'Multi-Tool Access',
    items: [
      'DB queries',
      'File reading & writing',
      'Browser automation',
      'Email sending',
      'Slack/Teams messaging'
    ],
    color: 'from-[#2D8CFF] to-[#5FFBF1]'
  },
  {
    icon: BarChart3,
    title: 'Dashboard Builder',
    items: [
      'Automatic Streamlit dashboards',
      'Real-time charts & KPIs',
      'Inventory heatmaps',
      'Operational control rooms'
    ],
    color: 'from-[#5FFBF1] to-[#2D8CFF]'
  },
  {
    icon: MessageCircle,
    title: 'Communication Interface',
    items: [
      'Human-like text responses',
      'Voice assistant mode',
      'Status updates + ETA'
    ],
    color: 'from-[#2D8CFF] to-[#1a6fcc]'
  },
  {
    icon: Server,
    title: 'Local Execution Engine',
    items: [
      'Works on customer\'s machines',
      'Full privacy & security',
      'Customizable permissions'
    ],
    color: 'from-[#5FFBF1] to-[#4dd9c7]'
  }
]

export function FeatureGrid() {
  return (
    <section className="py-20 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-[#0A1A2F] mb-4">
            Feature Grid
          </h2>
          <p className="text-xl text-[#B5C4D4] max-w-2xl mx-auto">
            Show depth, show power
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feature, index) => {
            const Icon = feature.icon
            return (
              <Card key={index} className="border-2 hover:border-[#2D8CFF] transition-all hover:shadow-xl">
                <CardHeader>
                  <div className={`w-12 h-12 rounded-lg bg-gradient-to-br ${feature.color} flex items-center justify-center mb-4`}>
                    <Icon className="h-6 w-6 text-white" />
                  </div>
                  <CardTitle className="text-xl font-bold text-[#0A1A2F]">
                    {feature.title}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-2">
                    {feature.items.map((item, itemIndex) => (
                      <li key={itemIndex} className="text-[#B5C4D4] flex items-start">
                        <span className="text-[#2D8CFF] mr-2">•</span>
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

