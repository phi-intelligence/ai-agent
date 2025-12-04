'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { adminApi } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Select } from '@/components/ui/select'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

export default function AdminTasksPage() {
  const [orgId, setOrgId] = useState('')
  const [agentId, setAgentId] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [selectedTaskId, setSelectedTaskId] = useState<string | null>(null)

  const { data: tasks, isLoading } = useQuery({
    queryKey: ['admin-tasks', orgId, agentId, statusFilter],
    queryFn: () => adminApi.listTasks({
      org_id: orgId || undefined,
      agent_id: agentId || undefined,
      status: statusFilter || undefined,
      limit: 100,
    }),
  })

  const { data: events } = useQuery({
    queryKey: ['admin-task-events', selectedTaskId],
    queryFn: () => adminApi.getTaskEvents(selectedTaskId!),
    enabled: !!selectedTaskId,
  })

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-semibold">Phi Agents - Admin</h1>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h2 className="text-2xl font-bold mb-2">Task Management</h2>
          <p className="text-gray-600">View and inspect tasks across all organizations</p>
        </div>

        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Filters</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="text-sm font-medium mb-2 block">Organization ID</label>
                <Input
                  placeholder="Filter by org ID"
                  value={orgId}
                  onChange={(e) => setOrgId(e.target.value)}
                />
              </div>
              <div>
                <label className="text-sm font-medium mb-2 block">Agent ID</label>
                <Input
                  placeholder="Filter by agent ID"
                  value={agentId}
                  onChange={(e) => setAgentId(e.target.value)}
                />
              </div>
              <div>
                <label className="text-sm font-medium mb-2 block">Status</label>
                <Select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                >
                  <option value="">All Statuses</option>
                  <option value="PENDING">Pending</option>
                  <option value="RUNNING">Running</option>
                  <option value="SUCCESS">Success</option>
                  <option value="FAILED">Failed</option>
                </Select>
              </div>
            </div>
          </CardContent>
        </Card>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle>Tasks</CardTitle>
              <CardDescription>
                {tasks ? `${tasks.length} tasks found` : 'Loading...'}
              </CardDescription>
            </CardHeader>
            <CardContent>
              {isLoading ? (
                <p>Loading tasks...</p>
              ) : tasks && tasks.length > 0 ? (
                <div className="space-y-2 max-h-96 overflow-y-auto">
                  {tasks.map((task: any) => (
                    <div
                      key={task.id}
                      className={`p-3 rounded-md border cursor-pointer hover:bg-gray-50 ${
                        selectedTaskId === task.id ? 'bg-blue-50 border-blue-300' : ''
                      }`}
                      onClick={() => setSelectedTaskId(task.id)}
                    >
                      <div className="flex justify-between items-start">
                        <div className="flex-1">
                          <p className="font-medium text-sm">{task.type}</p>
                          <p className="text-xs text-gray-500">
                            {new Date(task.created_at).toLocaleString()}
                          </p>
                          {task.current_step && (
                            <p className="text-xs text-gray-600 mt-1">{task.current_step}</p>
                          )}
                          {(task.status === 'RUNNING' || task.status === 'PENDING') && task.progress !== undefined && (
                            <div className="mt-2">
                              <div className="w-full bg-gray-200 rounded-full h-1.5">
                                <div
                                  className="bg-blue-600 h-1.5 rounded-full transition-all"
                                  style={{ width: `${task.progress}%` }}
                                />
                              </div>
                              <p className="text-xs text-gray-500 mt-1">{task.progress}%</p>
                            </div>
                          )}
                        </div>
                        <span
                          className={`text-xs px-2 py-1 rounded ${
                            task.status === 'SUCCESS'
                              ? 'bg-green-100 text-green-800'
                              : task.status === 'FAILED'
                              ? 'bg-red-100 text-red-800'
                              : task.status === 'RUNNING'
                              ? 'bg-blue-100 text-blue-800'
                              : 'bg-gray-100 text-gray-800'
                          }`}
                        >
                          {task.status}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500">No tasks found</p>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Task Details & Events</CardTitle>
              <CardDescription>
                {selectedTaskId ? `Task: ${selectedTaskId.slice(0, 8)}...` : 'Select a task to view details'}
              </CardDescription>
            </CardHeader>
            <CardContent>
              {selectedTaskId ? (
                <div className="space-y-4">
                  {tasks && (
                    <>
                      {(() => {
                        const task = tasks.find((t: any) => t.id === selectedTaskId)
                        if (!task) return null
                        return (
                          <div className="space-y-3">
                            <div>
                              <p className="text-sm font-medium">Type: {task.type}</p>
                              <p className="text-sm">Status: <span className={task.status === 'SUCCESS' ? 'text-green-600' : task.status === 'FAILED' ? 'text-red-600' : ''}>{task.status}</span></p>
                              {task.error && (
                                <p className="text-sm text-red-600 mt-2">Error: {task.error}</p>
                              )}
                            </div>

                            {/* Progress Bar */}
                            {(task.status === 'RUNNING' || task.status === 'PENDING') && task.progress !== undefined && (
                              <div className="space-y-2">
                                <div className="flex justify-between items-center">
                                  <span className="text-sm font-medium">Progress</span>
                                  <span className="text-sm text-gray-600">{task.progress}%</span>
                                </div>
                                <div className="w-full bg-gray-200 rounded-full h-2.5">
                                  <div
                                    className="bg-blue-600 h-2.5 rounded-full transition-all duration-300"
                                    style={{ width: `${task.progress}%` }}
                                  />
                                </div>
                                {task.current_step && (
                                  <p className="text-xs text-gray-600 mt-1">{task.current_step}</p>
                                )}
                                {task.eta_seconds && task.eta_seconds > 0 && (
                                  <p className="text-xs text-gray-500">
                                    ETA: {Math.ceil(task.eta_seconds / 60)} minute{Math.ceil(task.eta_seconds / 60) !== 1 ? 's' : ''}
                                  </p>
                                )}
                              </div>
                            )}

                            {task.output && (
                              <div className="space-y-2">
                                <p className="text-sm font-medium mb-1">Output:</p>
                                <pre className="text-xs bg-gray-50 p-2 rounded overflow-auto max-h-32">
                                  {typeof task.output === 'string' ? task.output : JSON.stringify(task.output, null, 2)}
                                </pre>
                                {task.output.dashboard_url && (
                                  <div className="mt-2 p-2 bg-blue-50 rounded border border-blue-200">
                                    <p className="text-xs font-medium text-blue-900 mb-1">Dashboard Available</p>
                                    <a
                                      href={task.output.dashboard_url}
                                      target="_blank"
                                      rel="noopener noreferrer"
                                      className="text-xs text-blue-600 hover:text-blue-800 underline"
                                    >
                                      Open Dashboard →
                                    </a>
                                  </div>
                                )}
                              </div>
                            )}
                          </div>
                        )
                      })()}
                    </>
                  )}

                  <div>
                    <p className="text-sm font-medium mb-2">Events ({events?.length || 0}):</p>
                    {events && events.length > 0 ? (
                      <div className="space-y-1 max-h-64 overflow-y-auto">
                        {events.map((event: any) => (
                          <div key={event.id} className="text-xs bg-gray-50 p-2 rounded">
                            <div className="flex justify-between">
                              <span className="font-medium">{event.event_type}</span>
                              <span className="text-gray-500">
                                {new Date(event.timestamp).toLocaleTimeString()}
                              </span>
                            </div>
                            {event.payload && (
                              <pre className="mt-1 text-xs text-gray-600">
                                {JSON.stringify(event.payload, null, 2)}
                              </pre>
                            )}
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-xs text-gray-500">No events</p>
                    )}
                  </div>
                </div>
              ) : (
                <p className="text-gray-500 text-sm">Select a task from the list to view details</p>
              )}
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  )
}


