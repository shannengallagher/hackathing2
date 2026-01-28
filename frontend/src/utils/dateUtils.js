import { format, formatDistanceToNow, isPast, isToday, isTomorrow, addDays, differenceInDays } from 'date-fns'

export const formatDate = (dateStr) => {
  if (!dateStr) return 'No due date'
  const date = new Date(dateStr)
  return format(date, 'MMM d, yyyy')
}

export const formatDateTime = (dateStr, timeStr) => {
  if (!dateStr) return 'No due date'
  const date = new Date(dateStr)
  let formatted = format(date, 'MMM d, yyyy')
  if (timeStr) {
    formatted += ` at ${timeStr}`
  }
  return formatted
}

export const getRelativeDate = (dateStr) => {
  if (!dateStr) return null
  const date = new Date(dateStr)

  if (isToday(date)) return 'Today'
  if (isTomorrow(date)) return 'Tomorrow'
  if (isPast(date)) return 'Overdue'

  const daysUntil = differenceInDays(date, new Date())
  if (daysUntil <= 7) return `In ${daysUntil} days`

  return formatDistanceToNow(date, { addSuffix: true })
}

export const getDueDateStatus = (dateStr) => {
  if (!dateStr) return 'none'
  const date = new Date(dateStr)

  if (isPast(date) && !isToday(date)) return 'overdue'
  if (isToday(date)) return 'today'
  if (isTomorrow(date)) return 'tomorrow'

  const daysUntil = differenceInDays(date, new Date())
  if (daysUntil <= 3) return 'urgent'
  if (daysUntil <= 7) return 'soon'

  return 'later'
}

export const getStatusColor = (status) => {
  const colors = {
    overdue: 'text-red-600 bg-red-50',
    today: 'text-orange-600 bg-orange-50',
    tomorrow: 'text-amber-600 bg-amber-50',
    urgent: 'text-yellow-600 bg-yellow-50',
    soon: 'text-blue-600 bg-blue-50',
    later: 'text-gray-600 bg-gray-50',
    none: 'text-gray-400 bg-gray-50'
  }
  return colors[status] || colors.none
}
