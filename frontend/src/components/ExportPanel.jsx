import { Calendar, FileJson, FileSpreadsheet, Download } from 'lucide-react'
import { exportICS, exportJSON, exportCSV } from '../services/api'

export default function ExportPanel({ syllabusId = null }) {
  const exports = [
    {
      name: 'Calendar (.ics)',
      description: 'Import into Google Calendar, Apple Calendar, or Outlook',
      icon: Calendar,
      action: () => exportICS(syllabusId),
      color: 'bg-blue-500 hover:bg-blue-600',
    },
    {
      name: 'JSON',
      description: 'Structured data for developers or other apps',
      icon: FileJson,
      action: () => exportJSON(syllabusId),
      color: 'bg-green-500 hover:bg-green-600',
    },
    {
      name: 'CSV',
      description: 'Open in Excel, Google Sheets, or other spreadsheets',
      icon: FileSpreadsheet,
      action: () => exportCSV(syllabusId),
      color: 'bg-purple-500 hover:bg-purple-600',
    },
  ]

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
        <Download className="h-5 w-5" />
        Export Assignments
      </h2>
      <div className="space-y-3">
        {exports.map((exp) => (
          <button
            key={exp.name}
            onClick={exp.action}
            className={`w-full flex items-center gap-3 p-3 rounded-lg text-white transition-colors ${exp.color}`}
          >
            <exp.icon className="h-5 w-5" />
            <div className="text-left">
              <div className="font-medium">{exp.name}</div>
              <div className="text-sm opacity-90">{exp.description}</div>
            </div>
          </button>
        ))}
      </div>
    </div>
  )
}
