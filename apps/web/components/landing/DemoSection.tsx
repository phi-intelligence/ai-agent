'use client'

import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { useRouter } from 'next/navigation'
import { Play, BarChart3, MessageSquare, Clock } from 'lucide-react'

export function DemoSection() {
  const router = useRouter()

  return (
    <section className="py-20 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-[#0A1A2F] mb-4">
            Live Demo
          </h2>
          <p className="text-xl text-[#B5C4D4] max-w-2xl mx-auto">
            See Phi Agents in action
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-8 mb-12">
          {/* CCTV Detection Demo */}
          <Card className="border-2 hover:border-[#2D8CFF] transition-all">
            <CardContent className="p-8">
              <div className="flex items-center mb-4">
                <Play className="h-8 w-8 text-[#2D8CFF] mr-3" />
                <h3 className="text-2xl font-bold text-[#0A1A2F]">
                  CCTV Detection
                </h3>
              </div>
              <p className="text-[#B5C4D4] mb-6">
                Playback of CCTV detection showing bounding boxes detecting unsafe forklift behaviour.
              </p>
              <div className="bg-gradient-to-br from-[#0A1A2F] to-[#1a2f4f] rounded-lg h-48 flex items-center justify-center text-[#5FFBF1]">
                <div className="text-center">
                  <div className="text-4xl mb-2">🎥</div>
                  <div className="text-sm">CCTV Analysis Preview</div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Dashboard Generation Demo */}
          <Card className="border-2 hover:border-[#2D8CFF] transition-all">
            <CardContent className="p-8">
              <div className="flex items-center mb-4">
                <BarChart3 className="h-8 w-8 text-[#5FFBF1] mr-3" />
                <h3 className="text-2xl font-bold text-[#0A1A2F]">
                  Auto-Generated Dashboard
                </h3>
              </div>
              <p className="text-[#B5C4D4] mb-6">
                Click → "Generate Warehouse Audit" → interactive charts appear.
              </p>
              <Button
                className="w-full bg-[#2D8CFF] hover:bg-[#1a6fcc] text-white"
                onClick={() => router.push('/demo')}
              >
                Generate Dashboard
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* Human-like Communication Example */}
        <Card className="border-2 border-[#2D8CFF] bg-gradient-to-br from-[#0A1A2F] to-[#1a2f4f]">
          <CardContent className="p-8">
            <div className="flex items-center mb-6">
              <MessageSquare className="h-8 w-8 text-[#5FFBF1] mr-3" />
              <h3 className="text-2xl font-bold text-white">
                Human-like Communication
              </h3>
            </div>
            <div className="bg-white/10 rounded-lg p-6 backdrop-blur-sm">
              <div className="flex items-start space-x-4">
                <div className="w-10 h-10 rounded-full bg-gradient-to-br from-[#2D8CFF] to-[#5FFBF1] flex items-center justify-center text-white font-bold">
                  Φ
                </div>
                <div className="flex-1">
                  <p className="text-white mb-2">
                    I'm running your inventory audit now, ETA 2 min 14 seconds.
                  </p>
                  <div className="flex items-center text-[#5FFBF1] text-sm">
                    <Clock className="h-4 w-4 mr-2" />
                    Progress: 45% • Current step: Analyzing stock levels
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </section>
  )
}

