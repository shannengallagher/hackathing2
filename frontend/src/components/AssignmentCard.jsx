import { useState } from 'react'
import { Clock, Calendar, Trash2, Edit2, X, Check } from 'lucide-react'
import { formatDateTime, getRelativeDate, getDueDateStatus, getStatusColor } from '../utils/dateUtils'
import { useUpdateAssignment, useDeleteAssignment } from '../hooks/useAssignments'

const typeColors = {
  homework: 'bg-blue-100 text-blue-800',
  quiz: 'bg-yellow-100 text-yellow-800',
  exam: 'bg-red-100 text-red-800',
  project: 'bg-purple-100 text-purple-800',
  paper: 'bg-indigo-100 text-indigo-800',
  reading: 'bg-green-100 text-green-800',
  presentation: 'bg-pink-100 text-pink-800',
  lab: 'bg-cyan-100 text-cyan-800',
  discussion: 'bg-orange-100 text-orange-800',
  other: 'bg-gray-100 text-gray-800',
}

export default function AssignmentCard({ assignment }) {
  const [isEditing, setIsEditing] = useState(false)
  const [editData, setEditData] = useState({
    title: assignment.title,
    due_date: assignment.due_date || '',
    estimated_hours: assignment.estimated_hours || '',
    assignment_type: assignment.assignment_type || 'other',
  })

  const updateMutation = useUpdateAssignment()
  const deleteMutation = useDeleteAssignment()

  const status = getDueDateStatus(assignment.due_date)
  const statusColor = getStatusColor(status)
  const relativeDate = getRelativeDate(assignment.due_date)

  const handleSave = () => {
    const dataToSend = {
      ...editData,
      estimated_hours: editData.estimated_hours ? parseFloat(editData.estimated_hours) : null,
      due_date: editData.due_date || null,
    }
    updateMutation.mutate(
      { id: assignment.id, data: dataToSend },
      { onSuccess: () => setIsEditing(false) }
    )
  }

  const handleDelete = () => {
    if (confirm('Are you sure you want to delete this assignment?')) {
      deleteMutation.mutate(assignment.id)
    }
  }

  if (isEditing) {
    return (
      <div className="bg-white rounded-lg shadow p-4 border-2 border-blue-500">
        <div className="space-y-3">
          <input
            type="text"
            value={editData.title}
            onChange={(e) => setEditData({ ...editData, title: e.target.value })}
            className="w-full px-3 py-2 border rounded-md"
            placeholder="Assignment title"
          />
          <div className="flex gap-3">
            <input
              type="date"
              value={editData.due_date}
              onChange={(e) => setEditData({ ...editData, due_date: e.target.value })}
              className="flex-1 px-3 py-2 border rounded-md"
            />
            <input
              type="number"
              value={editData.estimated_hours}
              onChange={(e) => setEditData({ ...editData, estimated_hours: e.target.value })}
              className="w-24 px-3 py-2 border rounded-md"
              placeholder="Hours"
              step="0.5"
              min="0"
            />
          </div>
          <div className="flex justify-end gap-2">
            <button
              onClick={() => setIsEditing(false)}
              className="px-3 py-1 text-gray-600 hover:text-gray-800"
            >
              <X className="h-5 w-5" />
            </button>
            <button
              onClick={handleSave}
              disabled={updateMutation.isPending}
              className="px-3 py-1 text-green-600 hover:text-green-800"
            >
              <Check className="h-5 w-5" />
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg shadow p-4 hover:shadow-md transition-shadow">
      <div className="flex justify-between items-start">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            <span className={`px-2 py-1 rounded-full text-xs font-medium ${typeColors[assignment.assignment_type] || typeColors.other}`}>
              {assignment.assignment_type}
            </span>
            {relativeDate && (
              <span className={`px-2 py-1 rounded-full text-xs font-medium ${statusColor}`}>
                {relativeDate}
              </span>
            )}
          </div>
          <h3 className="font-medium text-gray-900">{assignment.title}</h3>
          {assignment.description && (
            <p className="text-sm text-gray-500 mt-1 line-clamp-2">{assignment.description}</p>
          )}
        </div>
        <div className="flex gap-1 ml-4">
          <button
            onClick={() => setIsEditing(true)}
            className="p-1 text-gray-400 hover:text-blue-600"
          >
            <Edit2 className="h-4 w-4" />
          </button>
          <button
            onClick={handleDelete}
            disabled={deleteMutation.isPending}
            className="p-1 text-gray-400 hover:text-red-600"
          >
            <Trash2 className="h-4 w-4" />
          </button>
        </div>
      </div>
      <div className="flex items-center gap-4 mt-3 text-sm text-gray-500">
        {assignment.due_date && (
          <div className="flex items-center gap-1">
            <Calendar className="h-4 w-4" />
            <span>{formatDateTime(assignment.due_date, assignment.due_time)}</span>
          </div>
        )}
        {assignment.estimated_hours > 0 && (
          <div className="flex items-center gap-1">
            <Clock className="h-4 w-4" />
            <span>{assignment.estimated_hours}h estimated</span>
          </div>
        )}
        {assignment.course_name && (
          <div className="text-xs text-gray-400">
            {assignment.course_name}
          </div>
        )}
      </div>
    </div>
  )
}
