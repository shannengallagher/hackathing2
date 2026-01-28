import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import * as api from '../services/api'

export const useAssignments = (syllabusId = null) => {
  return useQuery({
    queryKey: ['assignments', syllabusId],
    queryFn: () => api.getAssignments(syllabusId),
  })
}

export const useUpcomingAssignments = (days = 14) => {
  return useQuery({
    queryKey: ['assignments', 'upcoming', days],
    queryFn: () => api.getUpcomingAssignments(days),
  })
}

export const useAssignmentStats = () => {
  return useQuery({
    queryKey: ['assignments', 'stats'],
    queryFn: api.getAssignmentStats,
  })
}

export const useUpdateAssignment = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, data }) => api.updateAssignment(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['assignments'] })
    },
  })
}

export const useDeleteAssignment = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: api.deleteAssignment,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['assignments'] })
    },
  })
}

export const useUploadHistory = () => {
  return useQuery({
    queryKey: ['syllabi'],
    queryFn: api.getUploadHistory,
  })
}

export const useDeleteSyllabus = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: api.deleteSyllabus,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['syllabi'] })
      queryClient.invalidateQueries({ queryKey: ['assignments'] })
    },
  })
}
