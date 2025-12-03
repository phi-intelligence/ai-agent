import axios from 'axios'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
const ORCHESTRATOR_API_URL = process.env.NEXT_PUBLIC_ORCHESTRATOR_URL || 'http://localhost:8001'

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Auth API
export const authApi = {
  signup: async (email: string, password: string, name?: string) => {
    const response = await api.post('/auth/signup', { email, password, name })
    return response.data
  },
  login: async (email: string, password: string) => {
    const response = await api.post('/auth/login', { email, password })
    return response.data
  },
  getMe: async () => {
    const response = await api.get('/me')
    return response.data
  },
}

// Organization API
export const orgApi = {
  create: async (name: string) => {
    const response = await api.post('/orgs', { name })
    return response.data
  },
  list: async () => {
    const response = await api.get('/orgs')
    return response.data
  },
  get: async (orgId: string) => {
    const response = await api.get(`/orgs/${orgId}`)
    return response.data
  },
}

// Industries API
export const industriesApi = {
  list: async () => {
    const response = await api.get('/industries')
    return response.data
  },
}

// Role Templates API
export const roleTemplatesApi = {
  list: async (industryKey?: string) => {
    const params = industryKey ? { industry_key: industryKey } : {}
    const response = await api.get('/role-templates', { params })
    return response.data
  },
}

// Tools API
export const toolsApi = {
  list: async () => {
    const response = await api.get('/tools')
    return response.data
  },
}

// Agents API
export const agentsApi = {
  create: async (orgId: string, data: {
    industry_id: string
    role_template_id: string
    name: string
    tool_ids: string[]
  }) => {
    const response = await api.post(`/orgs/${orgId}/agents`, data)
    return response.data
  },
  list: async (orgId: string) => {
    const response = await api.get(`/orgs/${orgId}/agents`)
    return response.data
  },
  get: async (agentId: string) => {
    const response = await api.get(`/agents/${agentId}`)
    return response.data
  },
  generateProfile: async (agentId: string) => {
    const response = await api.post(`/agents/${agentId}/generate-profile`)
    return response.data
  },
  downloadConfig: async (agentId: string, format: 'yaml' | 'json' = 'yaml') => {
    const response = await api.get(`/agents/${agentId}/config?format=${format}`, {
      responseType: 'blob',
    })
    return response.data
  },
}

// Documents API
export const documentsApi = {
  upload: async (agentId: string, file: File, sourceType: string) => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('source_type', sourceType)
    const response = await api.post(`/agents/${agentId}/documents`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },
  list: async (agentId: string) => {
    const response = await api.get(`/agents/${agentId}/documents`)
    return response.data
  },
  search: async (agentId: string, query: string, topK: number = 5) => {
    const response = await api.post(`/agents/${agentId}/documents/search-docs`, {
      query,
      top_k: topK,
    })
    return response.data
  },
}

// Orchestrator API
export const orchestratorApi = axios.create({
  baseURL: ORCHESTRATOR_API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add token to requests
orchestratorApi.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export const tasksApi = {
  runTask: async (agentId: string, type: string, input?: any) => {
    const response = await orchestratorApi.post(`/agents/${agentId}/run-task`, {
      type,
      input,
    })
    return response.data
  },
  get: async (taskId: string) => {
    const response = await orchestratorApi.get(`/tasks/${taskId}`)
    return response.data
  },
}

// Admin API
export const adminApi = {
  listTasks: async (params?: {
    org_id?: string
    agent_id?: string
    status?: string
    limit?: number
  }) => {
    const response = await api.get('/admin/tasks', { params })
    return response.data
  },
  getTaskEvents: async (taskId: string) => {
    const response = await api.get(`/admin/tasks/${taskId}/events`)
    return response.data
  },
}

