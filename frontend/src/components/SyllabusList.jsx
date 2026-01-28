import { Trash2, FileText, Loader2 } from 'lucide-react'
import { useUploadHistory, useDeleteSyllabus } from '../hooks/useAssignments'

export default function SyllabusList() {
  const { data: syllabi, isLoading } = useUploadHistory()
  const deleteMutation = useDeleteSyllabus()

  const handleDelete = (id, filename) => {
    if (confirm(`Delete "${filename}" and all its assignments?`)) {
      deleteMutation.mutate(id)
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-4">
        <Loader2 className="h-5 w-5 animate-spin text-gray-400" />
      </div>
    )
  }

  if (!syllabi || syllabi.length === 0) {
    return (
      <p className="text-sm text-gray-500 text-center py-4">
        No syllabi uploaded yet.
      </p>
    )
  }

  return (
    <div className="space-y-2">
      {syllabi.map((syllabus) => (
        <div
          key={syllabus.id}
          className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
        >
          <div className="flex items-center gap-3 min-w-0">
            <FileText className="h-5 w-5 text-gray-400 flex-shrink-0" />
            <div className="min-w-0">
              <p className="text-sm font-medium text-gray-900 truncate">
                {syllabus.course_name || syllabus.filename}
              </p>
              <p className="text-xs text-gray-500">
                {syllabus.assignments?.length || 0} assignments
              </p>
            </div>
          </div>
          <button
            onClick={() => handleDelete(syllabus.id, syllabus.course_name || syllabus.filename)}
            disabled={deleteMutation.isPending}
            className="p-2 text-gray-400 hover:text-red-600 flex-shrink-0"
          >
            <Trash2 className="h-4 w-4" />
          </button>
        </div>
      ))}
    </div>
  )
}
