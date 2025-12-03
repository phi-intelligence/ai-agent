'use client'

import { use } from 'react'
import { useRouter } from 'next/navigation'
import { useQuery } from '@tanstack/react-query'
import { orgApi } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

export default function OrgDetailPage({ params }: { params: Promise<{ orgId: string }> }) {
  const resolvedParams = use(params)
  const router = useRouter()
  const orgId = resolvedParams.orgId

  const { data: org, isLoading } = useQuery({
    queryKey: ['org', orgId],
    queryFn: () => orgApi.get(orgId),
  })

  if (isLoading) {
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
            <Button variant="outline" onClick={() => router.push('/dashboard')}>
              Back to Dashboard
            </Button>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h2 className="text-2xl font-bold mb-2">{org.name}</h2>
          <p className="text-gray-600">Organization Overview</p>
        </div>

        <div className="mb-6 flex space-x-4">
          <Button onClick={() => router.push(`/orgs/${orgId}/agents`)}>
            View Agents
          </Button>
          <Button variant="outline" onClick={() => router.push('/dashboard')}>
            Back to Dashboard
          </Button>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Organization Details</CardTitle>
            <CardDescription>Information about this organization</CardDescription>
          </CardHeader>
          <CardContent>
            <dl className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div>
                <dt className="text-sm font-medium text-gray-500">ID</dt>
                <dd className="mt-1 text-sm text-gray-900">{org.id}</dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Created</dt>
                <dd className="mt-1 text-sm text-gray-900">
                  {new Date(org.created_at).toLocaleDateString()}
                </dd>
              </div>
            </dl>
          </CardContent>
        </Card>
      </main>
    </div>
  )
}

