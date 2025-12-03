'use client'

import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { documentsApi } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Select } from '@/components/ui/select'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

interface DocumentUploadProps {
  agentId: string
}

export function DocumentUpload({ agentId }: DocumentUploadProps) {
  const [file, setFile] = useState<File | null>(null)
  const [sourceType, setSourceType] = useState<string>('OTHER')
  const queryClient = useQueryClient()

  const uploadMutation = useMutation({
    mutationFn: () => {
      if (!file) throw new Error('No file selected')
      return documentsApi.upload(agentId, file, sourceType)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents', agentId] })
      setFile(null)
      alert('Document uploaded successfully!')
    },
    onError: (error: any) => {
      alert(error.response?.data?.detail || 'Failed to upload document')
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!file) {
      alert('Please select a file')
      return
    }
    uploadMutation.mutate()
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Upload Document</CardTitle>
        <CardDescription>Upload a document to train your agent</CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <label htmlFor="file" className="text-sm font-medium">
              File
            </label>
            <Input
              id="file"
              type="file"
              accept=".pdf,.docx,.doc,.txt"
              onChange={(e) => setFile(e.target.files?.[0] || null)}
              required
            />
            <p className="text-xs text-gray-500">Supported formats: PDF, DOCX, DOC, TXT</p>
          </div>

          <div className="space-y-2">
            <label htmlFor="sourceType" className="text-sm font-medium">
              Source Type
            </label>
            <Select
              id="sourceType"
              value={sourceType}
              onChange={(e) => setSourceType(e.target.value)}
              required
            >
              <option value="JD">Job Description</option>
              <option value="SOP">Standard Operating Procedure</option>
              <option value="POLICY">Policy</option>
              <option value="MANUAL">Manual</option>
              <option value="OTHER">Other</option>
            </Select>
          </div>

          <Button type="submit" disabled={uploadMutation.isPending || !file}>
            {uploadMutation.isPending ? 'Uploading...' : 'Upload Document'}
          </Button>
        </form>
      </CardContent>
    </Card>
  )
}


