import FileUpload from './FileUpload'
import StatsCards from './StatsCards'
import AssignmentList from './AssignmentList'
import ExportPanel from './ExportPanel'
import SyllabusList from './SyllabusList'
import { useAssignments } from '../hooks/useAssignments'

export default function Dashboard() {
  const { data: assignments } = useAssignments()
  const hasAssignments = assignments && assignments.length > 0

  return (
    <div className="space-y-6">
      {/* Upload Section */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Upload Syllabus</h2>
        <FileUpload />
      </div>

      {hasAssignments && (
        <>
          {/* Stats */}
          <StatsCards />

          {/* Main Content Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
            {/* Assignment List - Takes up 3 columns */}
            <div className="lg:col-span-3">
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">All Assignments</h2>
                <AssignmentList />
              </div>
            </div>

            {/* Sidebar - Takes up 1 column */}
            <div className="space-y-6">
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">Uploaded Syllabi</h2>
                <SyllabusList />
              </div>
              <ExportPanel />
            </div>
          </div>
        </>
      )}

      {!hasAssignments && (
        <div className="text-center py-12">
          <p className="text-gray-500">
            Upload a syllabus to extract assignments and due dates automatically.
          </p>
        </div>
      )}
    </div>
  )
}
