'use client'

import { useState, useRef, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Send, Bot, User, Loader2 } from 'lucide-react'
import { Card, CardContent } from '@/components/ui/card'
import { tasksApi } from '@/lib/api'
import { useMutation, useQuery } from '@tanstack/react-query'
import { TaskExecutionView } from './TaskExecutionView'
import { VoiceInterface, speakText } from './VoiceInterface'

interface Message {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: Date
  taskId?: string
}

interface ChatInterfaceProps {
  agentId: string
  agentName: string
}

export function ChatInterface({ agentId, agentName }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'system',
      content: `Hello! I'm ${agentName}. I can help you with warehouse analysis, reports, and various tasks. What would you like me to do?`,
      timestamp: new Date()
    }
  ])
  const [input, setInput] = useState('')
  const [activeTaskId, setActiveTaskId] = useState<string | null>(null)
  const [isListening, setIsListening] = useState(false)
  const [voiceEnabled, setVoiceEnabled] = useState(true)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const { data: activeTask } = useQuery({
    queryKey: ['task', activeTaskId],
    queryFn: () => tasksApi.get(activeTaskId!),
    enabled: !!activeTaskId,
    refetchInterval: (data) => {
      return data?.status === 'RUNNING' || data?.status === 'PENDING' ? 2000 : false
    },
  })

  const runTaskMutation = useMutation({
    mutationFn: (taskType: string) => tasksApi.runTask(agentId, taskType),
    onSuccess: (data) => {
      setActiveTaskId(data.id)
      const assistantMessage: Message = {
        id: Date.now().toString(),
        role: 'assistant',
        content: 'I\'ve started working on your request. You can see my progress below.',
        timestamp: new Date(),
        taskId: data.id
      }
      setMessages(prev => [...prev, assistantMessage])
    },
    onError: (error: any) => {
      const errorText = `Sorry, I encountered an error: ${error.response?.data?.detail || 'Failed to start task'}`
      const errorMessage: Message = {
        id: Date.now().toString(),
        role: 'assistant',
        content: errorText,
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMessage])
      
      // Speak error if voice is enabled
      if (voiceEnabled) {
        speakText(errorText)
      }
    },
  })

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages, activeTask])

  // Update message when task completes
  useEffect(() => {
    if (activeTask && (activeTask.status === 'SUCCESS' || activeTask.status === 'FAILED')) {
      const completionMessage = activeTask.status === 'SUCCESS'
        ? `Task completed! ${activeTask.output?.summary_text || 'Results are ready.'}`
        : `Task failed: ${activeTask.error || 'Unknown error'}`

      setMessages(prev => prev.map(msg => 
        msg.taskId === activeTask.id
          ? {
              ...msg,
              content: completionMessage
            }
          : msg
      ))

      // Speak completion message if voice is enabled
      if (voiceEnabled && activeTask.status === 'SUCCESS') {
        speakText(completionMessage)
      }
    }
  }, [activeTask, voiceEnabled])

  const handleSend = async () => {
    if (!input.trim() || runTaskMutation.isPending) return

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    const userInput = input.trim().toLowerCase()
    const originalInput = input.trim()
    setInput('')

    // Simple intent detection - map user requests to task types
    let taskType = 'DAILY_WAREHOUSE_REPORT'
    if (userInput.includes('warehouse') || userInput.includes('inventory') || userInput.includes('report') || userInput.includes('daily')) {
      taskType = 'DAILY_WAREHOUSE_REPORT'
    } else if (userInput.includes('analyze') || userInput.includes('analysis') || userInput.includes('data')) {
      taskType = 'DAILY_WAREHOUSE_REPORT' // Default to warehouse report for analysis
    }

    // Show immediate response
    const thinkingMessage: Message = {
      id: (Date.now() + 1).toString(),
      role: 'assistant',
      content: 'I\'ll help you with that. Let me start working on it...',
      timestamp: new Date()
    }
    setMessages(prev => [...prev, thinkingMessage])

    // Speak the response if voice is enabled
    if (voiceEnabled) {
      speakText('I\'ll help you with that. Let me start working on it.')
    }

    runTaskMutation.mutate(taskType)
  }

  const handleVoiceTranscript = (text: string) => {
    setInput(text)
    // Auto-send after a short delay
    setTimeout(() => {
      if (text.trim()) {
        const userMessage: Message = {
          id: Date.now().toString(),
          role: 'user',
          content: text,
          timestamp: new Date()
        }
        setMessages(prev => [...prev, userMessage])
        
        const userInput = text.trim().toLowerCase()
        let taskType = 'DAILY_WAREHOUSE_REPORT'
        if (userInput.includes('warehouse') || userInput.includes('inventory') || userInput.includes('report') || userInput.includes('daily')) {
          taskType = 'DAILY_WAREHOUSE_REPORT'
        } else if (userInput.includes('analyze') || userInput.includes('analysis') || userInput.includes('data')) {
          taskType = 'DAILY_WAREHOUSE_REPORT'
        }

        const thinkingMessage: Message = {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: 'I\'ll help you with that. Let me start working on it...',
          timestamp: new Date()
        }
        setMessages(prev => [...prev, thinkingMessage])

        if (voiceEnabled) {
          speakText('I\'ll help you with that. Let me start working on it.')
        }

        runTaskMutation.mutate(taskType)
      }
    }, 500)
  }

  return (
    <div className="flex flex-col h-full">
      <Card className="flex-1 flex flex-col min-h-[600px]">
        <CardContent className="flex-1 flex flex-col p-0">
          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex gap-3 ${
                  message.role === 'user' ? 'justify-end' : 'justify-start'
                }`}
              >
                {message.role !== 'user' && (
                  <div className="w-8 h-8 rounded-full bg-gradient-to-br from-[#2D8CFF] to-[#5FFBF1] flex items-center justify-center flex-shrink-0">
                    <Bot className="h-5 w-5 text-white" />
                  </div>
                )}
                <div
                  className={`max-w-[80%] rounded-lg p-4 ${
                    message.role === 'user'
                      ? 'bg-[#2D8CFF] text-white'
                      : message.role === 'system'
                      ? 'bg-gray-100 text-gray-800'
                      : 'bg-gray-50 text-gray-900'
                  }`}
                >
                  <p className="whitespace-pre-wrap">{message.content}</p>
                  <span className="text-xs opacity-70 mt-2 block">
                    {message.timestamp.toLocaleTimeString()}
                  </span>
                </div>
                {message.role === 'user' && (
                  <div className="w-8 h-8 rounded-full bg-gray-300 flex items-center justify-center flex-shrink-0">
                    <User className="h-5 w-5 text-gray-600" />
                  </div>
                )}
              </div>
            ))}
            {runTaskMutation.isPending && (
              <div className="flex gap-3 justify-start">
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-[#2D8CFF] to-[#5FFBF1] flex items-center justify-center">
                  <Bot className="h-5 w-5 text-white" />
                </div>
                <div className="bg-gray-50 rounded-lg p-4">
                  <Loader2 className="h-5 w-5 animate-spin text-[#2D8CFF]" />
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Task Execution View */}
          {activeTask && (
            <div className="border-t p-4 bg-gray-50">
              <TaskExecutionView task={activeTask} />
            </div>
          )}

          {/* Input Area */}
          <div className="border-t p-4 bg-white">
            <form
              onSubmit={(e) => {
                e.preventDefault()
                handleSend()
              }}
              className="space-y-2"
            >
              <div className="flex gap-2">
                <Input
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="Ask me to analyze data, generate reports, check inventory..."
                  className="flex-1"
                  disabled={runTaskMutation.isPending || isListening}
                />
                <VoiceInterface
                  onTranscript={handleVoiceTranscript}
                  isListening={isListening}
                  setIsListening={setIsListening}
                  voiceEnabled={voiceEnabled}
                  setVoiceEnabled={setVoiceEnabled}
                />
                <Button
                  type="submit"
                  disabled={!input.trim() || runTaskMutation.isPending || isListening}
                  className="bg-[#2D8CFF] hover:bg-[#1a6fcc] text-white"
                >
                  <Send className="h-4 w-4" />
                </Button>
              </div>
              {isListening && (
                <div className="flex items-center gap-2 text-sm text-red-600">
                  <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse" />
                  Listening... Speak now
                </div>
              )}
            </form>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
