'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useQuery, useMutation } from '@tanstack/react-query'
import { orgApi, agentsApi, industriesApi, roleTemplatesApi, toolsApi } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Select } from '@/components/ui/select'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

export default function NewAgentPage({ params }: { params: { orgId: string } }) {
  const router = useRouter()
  const orgId = params.orgId

  const [industryId, setIndustryId] = useState<string>('')
  const [roleTemplateId, setRoleTemplateId] = useState<string>('')
  const [agentName, setAgentName] = useState('')
  const [selectedToolIds, setSelectedToolIds] = useState<string[]>([])

  const { data: org } = useQuery({
    queryKey: ['org', orgId],
    queryFn: () => orgApi.get(orgId),
  })

  const { data: industries } = useQuery({
    queryKey: ['industries'],
    queryFn: () => industriesApi.list(),
  })

  const { data: roleTemplates } = useQuery({
    queryKey: ['role-templates', industryId],
    queryFn: () => {
      const industry = industries?.find((ind: any) => ind.id === industryId)
      return roleTemplatesApi.list(industry?.key)
    },
    enabled: !!industryId && !!industries,
  })

  const { data: tools } = useQuery({
    queryKey: ['tools'],
    queryFn: () => toolsApi.list(),
  })

  // Reset role template when industry changes
  useEffect(() => {
    setRoleTemplateId('')
  }, [industryId])

  const createMutation = useMutation({
    mutationFn: () => agentsApi.create(orgId, {
      industry_id: industryId,
      role_template_id: roleTemplateId,
      name: agentName,
      tool_ids: selectedToolIds,
    }),
    onSuccess: (data) => {
      router.push(`/agents/${data.id}`)
    },
    onError: (error: any) => {
      alert(error.response?.data?.detail || 'Failed to create agent')
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!industryId || !roleTemplateId || !agentName) {
      alert('Please fill in all required fields')
      return
    }
    createMutation.mutate()
  }

  const toggleTool = (toolId: string) => {
    setSelectedToolIds(prev =>
      prev.includes(toolId)
        ? prev.filter(id => id !== toolId)
        : [...prev, toolId]
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-semibold">Phi Agents</h1>
            </div>
            <Button variant="outline" onClick={() => router.push(`/orgs/${orgId}/agents`)}>
              Back to Agents
            </Button>
          </div>
        </div>
      </nav>

      <main className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Card>
          <CardHeader>
            <CardTitle>Create Agent</CardTitle>
            <CardDescription>Create a new virtual employee for {org?.name}</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="space-y-2">
                <label htmlFor="industry" className="text-sm font-medium">
                  Industry *
                </label>
                <Select
                  id="industry"
                  value={industryId}
                  onChange={(e) => setIndustryId(e.target.value)}
                  required
                >
                  <option value="">Select an industry</option>
                  {industries?.map((industry: any) => (
                    <option key={industry.id} value={industry.id}>
                      {industry.name}
                    </option>
                  ))}
                </Select>
              </div>

              <div className="space-y-2">
                <label htmlFor="role" className="text-sm font-medium">
                  Role Template *
                </label>
                <Select
                  id="role"
                  value={roleTemplateId}
                  onChange={(e) => setRoleTemplateId(e.target.value)}
                  required
                  disabled={!industryId}
                >
                  <option value="">Select a role template</option>
                  {roleTemplates?.map((role: any) => (
                    <option key={role.id} value={role.id}>
                      {role.name}
                    </option>
                  ))}
                </Select>
                {!industryId && (
                  <p className="text-xs text-gray-500">Select an industry first</p>
                )}
              </div>

              <div className="space-y-2">
                <label htmlFor="name" className="text-sm font-medium">
                  Agent Name *
                </label>
                <Input
                  id="name"
                  type="text"
                  placeholder="e.g., Warehouse Analyst #1"
                  value={agentName}
                  onChange={(e) => setAgentName(e.target.value)}
                  required
                />
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">Tools</label>
                <div className="space-y-2">
                  {tools?.map((tool: any) => (
                    <label key={tool.id} className="flex items-center space-x-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={selectedToolIds.includes(tool.id)}
                        onChange={() => toggleTool(tool.id)}
                        className="rounded border-gray-300"
                      />
                      <span className="text-sm">
                        {tool.name} {tool.description && `- ${tool.description}`}
                      </span>
                    </label>
                  ))}
                </div>
              </div>

              <div className="flex space-x-4">
                <Button type="submit" disabled={createMutation.isPending}>
                  {createMutation.isPending ? 'Creating...' : 'Create Agent'}
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => router.push(`/orgs/${orgId}/agents`)}
                >
                  Cancel
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      </main>
    </div>
  )
}


