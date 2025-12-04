'use client'

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { CheckCircle2, XCircle, Loader2, Database, FileText, Globe, Mail, BarChart3 } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'

interface TaskEvent {
  id: string
  event_type: string
  timestamp: string
  payload?: {
    tool_name?: string
    step_id?: string
    current_step?: string
    progress?: number
    status?: string
    error?: string
    result?: any
  }
}

interface TaskExecutionViewProps {
  task: {
    id: string
    status: string
    progress?: number
    current_step?: string
    eta_seconds?: number
    error?: string
    output?: any
    events?: TaskEvent[]
  }
}

const toolIcons: Record<string, any> = {
  db: Database,
  file: FileText,
  web: Globe,
  email: Mail,
  dashboard: BarChart3,
}

export function TaskExecutionView({ task }: TaskExecutionViewProps) {
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'SUCCESS':
        return <CheckCircle2 className="h-5 w-5 text-green-500" />
      case 'FAILED':
        return <XCircle className="h-5 w-5 text-red-500" />
      case 'RUNNING':
      case 'PENDING':
        return <Loader2 className="h-5 w-5 text-blue-500 animate-spin" />
      default:
        return null
    }
  }

  const getToolEvents = () => {
    if (!task.events) return []
    // Get all relevant events, ordered by timestamp
    return task.events
      .filter(e => 
        e.event_type === 'TOOL_COMPLETED' || 
        e.event_type === 'TOOL_FAILED' ||
        e.event_type === 'PROGRESS_UPDATE' ||
        e.event_type === 'WORKFLOW_STARTED' ||
        e.event_type === 'WORKFLOW_COMPLETED'
      )
      .sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime())
  }

  const toolEvents = getToolEvents()

  return (
    <Card className="border-2">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              {getStatusIcon(task.status)}
              Task Execution
            </CardTitle>
            <CardDescription>
              {task.status === 'RUNNING' || task.status === 'PENDING'
                ? 'Agent is working on your request...'
                : task.status === 'SUCCESS'
                ? 'Task completed successfully'
                : 'Task failed'}
            </CardDescription>
          </div>
          {task.status === 'RUNNING' && task.progress !== undefined && (
            <div className="text-right">
              <div className="text-2xl font-bold text-[#2D8CFF]">{task.progress}%</div>
              <div className="text-xs text-gray-500">Complete</div>
            </div>
          )}
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Progress Bar */}
        {(task.status === 'RUNNING' || task.status === 'PENDING') && task.progress !== undefined && (
          <div className="space-y-2">
            <div className="flex justify-between items-center text-sm">
              <span className="font-medium">Progress</span>
              <span className="text-gray-600">{task.progress}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
              <motion.div
                className="bg-gradient-to-r from-[#2D8CFF] to-[#5FFBF1] h-full rounded-full"
                initial={{ width: 0 }}
                animate={{ width: `${task.progress}%` }}
                transition={{ duration: 0.5 }}
              />
            </div>
            {task.current_step && (
              <p className="text-sm text-gray-600 mt-2 flex items-center gap-2">
                <Loader2 className="h-4 w-4 animate-spin text-[#2D8CFF]" />
                {task.current_step}
              </p>
            )}
            {task.eta_seconds && task.eta_seconds > 0 && (
              <p className="text-xs text-gray-500">
                Estimated time remaining: {Math.ceil(task.eta_seconds / 60)} minute{Math.ceil(task.eta_seconds / 60) !== 1 ? 's' : ''}
              </p>
            )}
          </div>
        )}

        {/* Tool Calls Timeline */}
        {toolEvents.length > 0 && (
          <div className="space-y-3">
            <h4 className="font-semibold text-sm flex items-center gap-2">
              <div className="w-2 h-2 bg-[#2D8CFF] rounded-full animate-pulse" />
              Agent Actions
            </h4>
            <div className="space-y-2">
              <AnimatePresence>
                {toolEvents.map((event, index) => {
                  const Icon = event.payload?.tool_name ? toolIcons[event.payload.tool_name] || Database : null
                  const isCompleted = event.event_type === 'TOOL_COMPLETED'
                  const isFailed = event.event_type === 'TOOL_FAILED'
                  const isProgress = event.event_type === 'PROGRESS_UPDATE'

                  return (
                    <motion.div
                      key={event.id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0 }}
                      className={`flex items-start gap-3 p-3 rounded-lg border ${
                        isCompleted
                          ? 'bg-green-50 border-green-200'
                          : isFailed
                          ? 'bg-red-50 border-red-200'
                          : 'bg-blue-50 border-blue-200'
                      }`}
                    >
                      {Icon && (
                        <div className={`p-2 rounded-lg ${
                          isCompleted
                            ? 'bg-green-100'
                            : isFailed
                            ? 'bg-red-100'
                            : 'bg-blue-100'
                        }`}>
                          <Icon className={`h-4 w-4 ${
                            isCompleted
                              ? 'text-green-600'
                              : isFailed
                              ? 'text-red-600'
                              : 'text-blue-600'
                          }`} />
                        </div>
                      )}
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          {isProgress ? (
                            <>
                              <Loader2 className="h-4 w-4 animate-spin text-blue-500" />
                              <span className="font-medium text-sm">
                                {event.payload?.current_step || 'Processing...'}
                              </span>
                            </>
                          ) : (
                            <>
                              {isCompleted ? (
                                <CheckCircle2 className="h-4 w-4 text-green-500" />
                              ) : isFailed ? (
                                <XCircle className="h-4 w-4 text-red-500" />
                              ) : (
                                <Loader2 className="h-4 w-4 animate-spin text-blue-500" />
                              )}
                              <span className="font-medium text-sm">
                                {event.payload?.tool_name || 'Tool'}
                                {isCompleted && ' completed'}
                                {isFailed && ' failed'}
                                {!isCompleted && !isFailed && ' running...'}
                              </span>
                            </>
                          )}
                        </div>
                        {event.payload?.error && (
                          <p className="text-xs text-red-600 mt-1">{event.payload.error}</p>
                        )}
                        {event.payload?.result && typeof event.payload.result === 'string' && (
                          <p className="text-xs text-gray-600 mt-1">{event.payload.result}</p>
                        )}
                        <p className="text-xs text-gray-400 mt-1">
                          {new Date(event.timestamp).toLocaleTimeString()}
                        </p>
                      </div>
                    </motion.div>
                  )
                })}
              </AnimatePresence>
            </div>
          </div>
        )}

        {/* Error Display */}
        {task.error && (
          <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
            <div className="flex items-start gap-2">
              <XCircle className="h-5 w-5 text-red-500 flex-shrink-0 mt-0.5" />
              <div>
                <p className="font-medium text-red-900">Error</p>
                <p className="text-sm text-red-700 mt-1">{task.error}</p>
              </div>
            </div>
          </div>
        )}

        {/* Output Display */}
        {task.output && task.status === 'SUCCESS' && (
          <div className="space-y-3">
            <h4 className="font-semibold text-sm">Results</h4>
            {task.output.full_report_md ? (
              <div className="prose prose-sm max-w-none bg-gray-50 p-4 rounded-lg">
                <pre className="whitespace-pre-wrap text-sm">{task.output.full_report_md}</pre>
              </div>
            ) : (
              <pre className="text-sm bg-gray-50 p-4 rounded-lg overflow-auto">
                {JSON.stringify(task.output, null, 2)}
              </pre>
            )}
            
            {task.output.dashboard_url && (
              <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <p className="text-sm font-medium text-blue-900 mb-2">Interactive Dashboard Available</p>
                <a
                  href={task.output.dashboard_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-blue-600 hover:text-blue-800 underline inline-flex items-center gap-1"
                >
                  Open Dashboard →
                </a>
              </div>
            )}
          </div>
        )}

        {/* All Events Timeline */}
        {task.events && task.events.length > 0 && (
          <div className="space-y-2">
            <h4 className="font-semibold text-sm">Event Timeline</h4>
            <div className="space-y-1 max-h-64 overflow-y-auto">
              {task.events.map((event) => (
                <div key={event.id} className="flex items-start gap-2 text-xs p-2 bg-gray-50 rounded">
                  <div className="w-2 h-2 rounded-full bg-[#2D8CFF] mt-1.5 flex-shrink-0" />
                  <div className="flex-1">
                    <div className="flex justify-between items-start">
                      <span className="font-medium">{event.event_type}</span>
                      <span className="text-gray-400">{new Date(event.timestamp).toLocaleTimeString()}</span>
                    </div>
                    {event.payload && Object.keys(event.payload).length > 0 && (
                      <div className="mt-1 text-gray-600">
                        {event.payload.tool_name && <p>Tool: {event.payload.tool_name}</p>}
                        {event.payload.current_step && <p>Step: {event.payload.current_step}</p>}
                        {event.payload.progress !== undefined && <p>Progress: {event.payload.progress}%</p>}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

