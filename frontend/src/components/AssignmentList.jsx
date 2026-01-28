import { useState } from 'react'
import { Search, Filter } from 'lucide-react'
import { useAssignments, useUploadHistory } from '../hooks/useAssignments'
import AssignmentCard from './AssignmentCard'

const ASSIGNMENT_TYPES = [
  'all',
  'homework',
  'quiz',
  'exam',
  'project',
  'paper',
  'reading',
  'presentation',
  'lab',
  'discussion',
  'other',
]

export default function AssignmentList() {
  const [searchTerm, setSearchTerm] = useState('')
  const [typeFilter, setTypeFilter] = useState('all')
  const [classFilter, setClassFilter] = useState('all')
  const [sortBy, setSortBy] = useState('due_date')

  const { data: syllabi } = useUploadHistory()
  const { data: assignments, isLoading, error } = useAssignments(classFilter !== 'all' ? parseInt(classFilter) : null)

  if (isLoading) {
    return (
      <div className="space-y-4">
        {[...Array(3)].map((_, i) => (
          <div key={i} className="bg-white rounded-lg shadow p-4 animate-pulse">
            <div className="h-4 bg-gray-200 rounded w-1/4 mb-2"></div>
            <div className="h-6 bg-gray-200 rounded w-3/4 mb-2"></div>
            <div className="h-4 bg-gray-200 rounded w-1/2"></div>
          </div>
        ))}
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 text-red-600 p-4 rounded-lg">
        Failed to load assignments: {error.message}
      </div>
    )
  }

  // Filter and sort assignments
  let filteredAssignments = assignments || []

  if (searchTerm) {
    const search = searchTerm.toLowerCase()
    filteredAssignments = filteredAssignments.filter(
      (a) =>
        a.title.toLowerCase().includes(search) ||
        a.description?.toLowerCase().includes(search)
    )
  }

  if (typeFilter !== 'all') {
    filteredAssignments = filteredAssignments.filter(
      (a) => a.assignment_type === typeFilter
    )
  }

  // Sort assignments
  filteredAssignments = [...filteredAssignments].sort((a, b) => {
    if (sortBy === 'due_date') {
      if (!a.due_date) return 1
      if (!b.due_date) return -1
      return new Date(a.due_date) - new Date(b.due_date)
    }
    if (sortBy === 'title') {
      return a.title.localeCompare(b.title)
    }
    if (sortBy === 'hours') {
      return b.estimated_hours - a.estimated_hours
    }
    return 0
  })

  return (
    <div className="space-y-4">
      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search assignments..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
        <select
          value={classFilter}
          onChange={(e) => setClassFilter(e.target.value)}
          className="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
        >
          <option value="all">All Classes</option>
          {syllabi?.map((syllabus) => (
            <option key={syllabus.id} value={syllabus.id}>
              {syllabus.course_name || syllabus.filename}
            </option>
          ))}
        </select>
        <select
          value={typeFilter}
          onChange={(e) => setTypeFilter(e.target.value)}
          className="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
        >
          {ASSIGNMENT_TYPES.map((type) => (
            <option key={type} value={type}>
              {type === 'all' ? 'All Types' : type.charAt(0).toUpperCase() + type.slice(1)}
            </option>
          ))}
        </select>
        <select
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value)}
          className="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
        >
          <option value="due_date">Sort by Due Date</option>
          <option value="title">Sort by Title</option>
          <option value="hours">Sort by Hours</option>
        </select>
      </div>

      {/* Assignment list */}
      {filteredAssignments.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          {assignments?.length === 0
            ? 'No assignments yet. Upload a syllabus to get started!'
            : 'No assignments match your filters.'}
        </div>
      ) : (
        <div className="space-y-3">
          {filteredAssignments.map((assignment) => (
            <AssignmentCard key={assignment.id} assignment={assignment} />
          ))}
        </div>
      )}
    </div>
  )
}
