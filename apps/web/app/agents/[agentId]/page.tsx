'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { agentsApi, documentsApi, tasksApi } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { DocumentUpload } from '@/components/DocumentUpload'
import { ChatInterface } from '@/components/agent/ChatInterface'
import { TaskHistory } from '@/components/agent/TaskHistory'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'

export default function AgentDetailPage({ params }: { params: { agentId: string } }) {
  const router = useRouter()
  const agentId = params.agentId

  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState<any[]>([])
  const queryClient = useQueryClient()

  const { data: agent, isLoading } = useQuery({
    queryKey: ['agent', agentId],
    queryFn: () => agentsApi.get(agentId),
  })

  const generateProfileMutation = useMutation({
    mutationFn: () => agentsApi.generateProfile(agentId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['agent', agentId] })
      alert('Profile generated successfully!')
    },
    onError: (error: any) => {
      alert(error.response?.data?.detail || 'Failed to generate profile')
    },
  })

  const [runningTaskId, setRunningTaskId] = useState<string | null>(null)
  const [taskResult, setTaskResult] = useState<any>(null)

  const { data: task, isLoading: taskLoading } = useQuery({
    queryKey: ['task', runningTaskId],
    queryFn: () => tasksApi.get(runningTaskId!),
    enabled: !!runningTaskId,
    refetchInterval: (data) => {
      // Poll every 2 seconds if task is still running
      return data?.status === 'RUNNING' || data?.status === 'PENDING' ? 2000 : false
    },
  })

  // Update task result when task completes
  if (task && (task.status === 'SUCCESS' || task.status === 'FAILED')) {
    if (taskResult?.id !== task.id) {
      setTaskResult(task)
    }
  }

  const runTaskMutation = useMutation({
    mutationFn: () => tasksApi.runTask(agentId, 'DAILY_WAREHOUSE_REPORT'),
    onSuccess: (data) => {
      setRunningTaskId(data.id)
      setTaskResult(null)
    },
    onError: (error: any) => {
      alert(error.response?.data?.detail || 'Failed to run task')
    },
  })

  const handleDownloadConfig = async (format: 'yaml' | 'json' = 'yaml') => {
    try {
      const blob = await agentsApi.downloadConfig(agentId, format)
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `phi-agent-config-${agent?.name?.replace(' ', '-') || 'agent'}.${format}`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to download config')
    }
  }

  const { data: documents, isLoading: documentsLoading } = useQuery({
    queryKey: ['documents', agentId],
    queryFn: () => documentsApi.list(agentId),
    enabled: !!agent,
  })

  const handleSearch = async () => {
    if (!searchQuery.trim()) return
    try {
      const results = await documentsApi.search(agentId, searchQuery, 5)
      setSearchResults(results.chunks || [])
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Search failed')
    }
  }

  if (isLoading) {
    return <div className="p-8">Loading...</div>
  }

  if (!agent) {
    return <div className="p-8">Agent not found</div>
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-semibold">Phi Agents</h1>
            </div>
            <Button variant="outline" onClick={() => router.push(`/orgs/${agent.org_id}/agents`)}>
              Back to Agents
            </Button>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8 flex justify-between items-center">
          <div>
            <h2 className="text-2xl font-bold mb-2">{agent.name}</h2>
            <p className="text-gray-600">Agent Details</p>
          </div>
          <div className="flex space-x-2">
            <Button
              onClick={() => generateProfileMutation.mutate()}
              disabled={generateProfileMutation.isPending}
            >
              {generateProfileMutation.isPending ? 'Generating...' : 'Generate Profile'}
            </Button>
            <Button
              variant="outline"
              onClick={() => handleDownloadConfig('yaml')}
              disabled={!agent.system_prompt}
            >
              Download Config (YAML)
            </Button>
          </div>
        </div>

        <Tabs defaultValue="chat" className="w-full">
          <TabsList className="grid w-full grid-cols-3 mb-6">
            <TabsTrigger value="chat">Chat with Agent</TabsTrigger>
            <TabsTrigger value="details">Agent Details</TabsTrigger>
            <TabsTrigger value="tasks">Task History</TabsTrigger>
          </TabsList>

          <TabsContent value="chat" className="mt-0">
            <div className="h-[calc(100vh-300px)] min-h-[600px]">
              <ChatInterface agentId={agentId} agentName={agent.name} />
            </div>
          </TabsContent>

          <TabsContent value="details" className="mt-0">
            <div className="grid gap-6">
          <Card>
            <CardHeader>
              <CardTitle>General Information</CardTitle>
            </CardHeader>
            <CardContent>
              <dl className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <div>
                  <dt className="text-sm font-medium text-gray-500">Status</dt>
                  <dd className="mt-1 text-sm">
                    <span className={agent.status === 'ACTIVE' ? 'text-green-600 font-medium' : 'text-gray-600'}>
                      {agent.status}
                    </span>
                  </dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">Created</dt>
                  <dd className="mt-1 text-sm text-gray-900">
                    {new Date(agent.created_at).toLocaleDateString()}
                  </dd>
                </div>
              </dl>
            </CardContent>
          </Card>

          {agent.agent_tools && agent.agent_tools.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Tools</CardTitle>
                <CardDescription>Tools configured for this agent</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {agent.agent_tools.map((agentTool: any) => (
                    <div key={agentTool.id} className="p-3 bg-gray-50 rounded-md">
                      <p className="text-sm font-medium">Tool ID: {agentTool.tool_id}</p>
                      {agentTool.config && (
                        <p className="text-xs text-gray-500 mt-1">
                          Config: {JSON.stringify(agentTool.config)}
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {agent.system_prompt && (
            <Card>
              <CardHeader>
                <CardTitle>System Prompt</CardTitle>
              </CardHeader>
              <CardContent>
                <pre className="text-sm bg-gray-50 p-4 rounded-md whitespace-pre-wrap">
                  {agent.system_prompt}
                </pre>
              </CardContent>
            </Card>
          )}

          {agent.config && (
            <Card>
              <CardHeader>
                <CardTitle>Configuration</CardTitle>
              </CardHeader>
              <CardContent>
                <pre className="text-sm bg-gray-50 p-4 rounded-md overflow-auto">
                  {JSON.stringify(agent.config, null, 2)}
                </pre>
              </CardContent>
            </Card>
          )}

          <Card>
            <CardHeader>
              <CardTitle>Documents</CardTitle>
              <CardDescription>Upload and manage documents for this agent</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <DocumentUpload agentId={agentId} />

              <div className="space-y-4">
                <div className="flex space-x-2">
                  <Input
                    placeholder="Search documents..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                  />
                  <Button onClick={handleSearch}>Search</Button>
                </div>

                {searchResults.length > 0 && (
                  <div className="space-y-2">
                    <h4 className="font-medium">Search Results:</h4>
                    {searchResults.map((chunk: any, idx: number) => (
                      <div key={idx} className="p-3 bg-gray-50 rounded-md">
                        <p className="text-sm">{chunk.chunk_text}</p>
                        {chunk.metadata && (
                          <p className="text-xs text-gray-500 mt-1">
                            Source: {chunk.metadata.source_type}
                          </p>
                        )}
                      </div>
                    ))}
                  </div>
                )}

                <div>
                  <h4 className="font-medium mb-2">Uploaded Documents:</h4>
                  {documentsLoading ? (
                    <p className="text-sm text-gray-500">Loading...</p>
                  ) : documents && documents.length > 0 ? (
                    <div className="space-y-2">
                      {documents.map((doc: any) => (
                        <div key={doc.id} className="p-3 bg-gray-50 rounded-md">
                          <p className="text-sm font-medium">{doc.name}</p>
                          <p className="text-xs text-gray-500">
                            Type: {doc.source_type} • {new Date(doc.created_at).toLocaleDateString()}
                          </p>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-sm text-gray-500">No documents uploaded yet</p>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>

            </div>
          </TabsContent>

          <TabsContent value="tasks" className="mt-0">
            <TaskHistory agentId={agentId} />
          </TabsContent>
        </Tabs>
      </main>
    </div>
  )
}




