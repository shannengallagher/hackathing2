import { BookOpen, Clock, AlertTriangle, Calendar } from 'lucide-react'
import { useAssignmentStats } from '../hooks/useAssignments'

export default function StatsCards() {
  const { data: stats, isLoading } = useAssignmentStats()

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="bg-white rounded-lg shadow p-6 animate-pulse">
            <div className="h-4 bg-gray-200 rounded w-1/2 mb-2"></div>
            <div className="h-8 bg-gray-200 rounded w-1/3"></div>
          </div>
        ))}
      </div>
    )
  }

  const cards = [
    {
      title: 'Total Assignments',
      value: stats?.total || 0,
      icon: BookOpen,
      color: 'text-blue-600 bg-blue-100',
    },
    {
      title: 'Upcoming',
      value: stats?.upcoming || 0,
      icon: Calendar,
      color: 'text-green-600 bg-green-100',
    },
    {
      title: 'Overdue',
      value: stats?.overdue || 0,
      icon: AlertTriangle,
      color: 'text-red-600 bg-red-100',
    },
    {
      title: 'Total Hours',
      value: stats?.total_hours || 0,
      icon: Clock,
      color: 'text-purple-600 bg-purple-100',
    },
  ]

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
      {cards.map((card) => (
        <div key={card.title} className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className={`p-3 rounded-lg ${card.color}`}>
              <card.icon className="h-6 w-6" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">{card.title}</p>
              <p className="text-2xl font-semibold text-gray-900">{card.value}</p>
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}
