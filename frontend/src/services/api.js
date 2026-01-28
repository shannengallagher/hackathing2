import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
})

// Upload endpoints
export const uploadSyllabus = async (file) => {
  const formData = new FormData()
  formData.append('file', file)
  const response = await api.post('/upload/syllabus', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return response.data
}

export const getUploadStatus = async (syllabusId) => {
  const response = await api.get(`/upload/status/${syllabusId}`)
  return response.data
}

export const getUploadHistory = async () => {
  const response = await api.get('/upload/history')
  return response.data
}

export const deleteSyllabus = async (syllabusId) => {
  const response = await api.delete(`/upload/${syllabusId}`)
  return response.data
}

// Assignment endpoints
export const getAssignments = async (syllabusId = null) => {
  const params = syllabusId ? { syllabus_id: syllabusId } : {}
  const response = await api.get('/assignments', { params })
  return response.data
}

export const getUpcomingAssignments = async (days = 14) => {
  const response = await api.get('/assignments/upcoming', { params: { days } })
  return response.data
}

export const getAssignmentStats = async () => {
  const response = await api.get('/assignments/stats')
  return response.data
}

export const updateAssignment = async (id, data) => {
  const response = await api.put(`/assignments/${id}`, data)
  return response.data
}

export const deleteAssignment = async (id) => {
  const response = await api.delete(`/assignments/${id}`)
  return response.data
}

// Export endpoints
export const exportICS = (syllabusId = null) => {
  const params = syllabusId ? `?syllabus_id=${syllabusId}` : ''
  window.location.href = `/api/export/ics${params}`
}

export const exportJSON = (syllabusId = null) => {
  const params = syllabusId ? `?syllabus_id=${syllabusId}` : ''
  window.location.href = `/api/export/json${params}`
}

export const exportCSV = (syllabusId = null) => {
  const params = syllabusId ? `?syllabus_id=${syllabusId}` : ''
  window.location.href = `/api/export/csv${params}`
}

export default api
