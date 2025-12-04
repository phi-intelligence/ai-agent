'use client'

import { useQuery } from '@tanstack/react-query'
import { tasksApi } from '@/lib/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { CheckCircle2, XCircle, Loader2, Clock } from 'lucide-react'
import { TaskExecutionView } from './TaskExecutionView'

interface TaskHistoryProps {
  agentId: string
}

export function TaskHistory({ agentId }: TaskHistoryProps) {
  const { data: tasks, isLoading } = useQuery({
    queryKey: ['agent-tasks', agentId],
    queryFn: () => tasksApi.listByAgent(agentId),
    enabled: !!agentId,
  })

  if (isLoading) {
    return (
      <Card>
        <CardContent className="p-8 text-center">
          <Loader2 className="h-8 w-8 animate-spin text-[#2D8CFF] mx-auto" />
          <p className="text-gray-500 mt-4">Loading task history...</p>
        </CardContent>
      </Card>
    )
  }

  if (!tasks || tasks.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Task History</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-gray-500 text-center py-8">
            No tasks have been executed yet. Start a conversation with the agent to see tasks here.
          </p>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>Task History</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {tasks.map((task: any) => (
              <div key={task.id} className="border rounded-lg p-4 hover:bg-gray-50 transition-colors">
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-2">
                    {task.status === 'SUCCESS' && <CheckCircle2 className="h-5 w-5 text-green-500" />}
                    {task.status === 'FAILED' && <XCircle className="h-5 w-5 text-red-500" />}
                    {(task.status === 'RUNNING' || task.status === 'PENDING') && (
                      <Loader2 className="h-5 w-5 text-blue-500 animate-spin" />
                    )}
                    <span className="font-semibold">{task.type}</span>
                  </div>
                  <div className="flex items-center gap-2 text-sm text-gray-500">
                    <Clock className="h-4 w-4" />
                    {new Date(task.created_at).toLocaleString()}
                  </div>
                </div>
                <div className="text-sm text-gray-600">
                  Status: <span className={`font-medium ${
                    task.status === 'SUCCESS' ? 'text-green-600' :
                    task.status === 'FAILED' ? 'text-red-600' :
                    'text-blue-600'
                  }`}>{task.status}</span>
                </div>
                {task.current_step && (
                  <div className="text-sm text-gray-500 mt-1">
                    {task.current_step}
                  </div>
                )}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

