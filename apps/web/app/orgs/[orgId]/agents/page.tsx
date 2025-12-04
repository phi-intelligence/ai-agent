'use client'

import { useRouter } from 'next/navigation'
import { useQuery } from '@tanstack/react-query'
import { orgApi, agentsApi } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

export default function AgentsPage({ params }: { params: { orgId: string } }) {
  const router = useRouter()
  const orgId = params.orgId

  const { data: org, isLoading: orgLoading } = useQuery({
    queryKey: ['org', orgId],
    queryFn: () => orgApi.get(orgId),
  })

  const { data: agents, isLoading: agentsLoading } = useQuery({
    queryKey: ['agents', orgId],
    queryFn: () => agentsApi.list(orgId),
    enabled: !!org,
  })

  if (orgLoading || agentsLoading) {
    return <div className="p-8">Loading...</div>
  }

  if (!org) {
    return <div className="p-8">Organization not found</div>
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-semibold">Phi Agents</h1>
            </div>
            <div className="flex items-center space-x-4">
              <Button variant="outline" onClick={() => router.push(`/orgs/${orgId}`)}>
                Back to Organization
              </Button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8 flex justify-between items-center">
          <div>
            <h2 className="text-2xl font-bold mb-2">Agents</h2>
            <p className="text-gray-600">Manage your virtual employees for {org.name}</p>
          </div>
          <Button onClick={() => router.push(`/orgs/${orgId}/agents/new`)}>
            Create Agent
          </Button>
        </div>

        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {agents && agents.length > 0 ? (
            agents.map((agent: any) => (
              <Card
                key={agent.id}
                className="cursor-pointer hover:shadow-lg transition-shadow"
                onClick={() => router.push(`/agents/${agent.id}`)}
              >
                <CardHeader>
                  <CardTitle>{agent.name}</CardTitle>
                  <CardDescription>
                    Status: <span className={agent.status === 'ACTIVE' ? 'text-green-600' : 'text-gray-600'}>
                      {agent.status}
                    </span>
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-gray-600">Click to view details</p>
                </CardContent>
              </Card>
            ))
          ) : (
            <Card className="col-span-full">
              <CardHeader>
                <CardTitle>No Agents</CardTitle>
                <CardDescription>Create your first agent to get started</CardDescription>
              </CardHeader>
              <CardContent>
                <Button onClick={() => router.push(`/orgs/${orgId}/agents/new`)}>
                  Create Your First Agent
                </Button>
              </CardContent>
            </Card>
          )}
        </div>
      </main>
    </div>
  )
}


