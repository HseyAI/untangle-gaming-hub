import { useEffect, useState } from 'react'
import { sessionsApi } from '../services/api'
import type { GamingSession } from '../types'
import { GamepadIcon, Clock, Play } from 'lucide-react'
import { formatDistance } from 'date-fns'

export default function SessionsPage() {
  const [sessions, setSessions] = useState<GamingSession[]>([])
  const [activeSessions, setActiveSessions] = useState<GamingSession[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    loadSessions()
  }, [])

  const loadSessions = async () => {
    try {
      setIsLoading(true)
      const [allData, activeData] = await Promise.all([
        sessionsApi.list({ page_size: 100 }),
        sessionsApi.getActive(),
      ])
      setSessions(allData.sessions || allData.items || [])
      setActiveSessions(activeData || [])
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load sessions')
    } finally {
      setIsLoading(false)
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800'
      case 'completed':
        return 'bg-blue-100 text-blue-800'
      case 'cancelled':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  return (
    <div>
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Gaming Sessions</h1>
        <p className="text-gray-600 mt-2">Track active and completed gaming sessions</p>
      </div>

      {/* Active Sessions Alert */}
      {activeSessions.length > 0 && (
        <div className="mb-6 bg-green-50 border border-green-200 rounded-lg p-4">
          <div className="flex items-center gap-3">
            <Play className="w-5 h-5 text-green-600" />
            <div>
              <p className="font-medium text-green-900">
                {activeSessions.length} Active Session{activeSessions.length > 1 ? 's' : ''}
              </p>
              <p className="text-sm text-green-700">
                Members are currently playing
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
          {error}
        </div>
      )}

      {/* Loading */}
      {isLoading && (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        </div>
      )}

      {/* Sessions Table */}
      {!isLoading && sessions.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          <table className="w-full">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Date & Time
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Station
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Game
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Hours
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Duration
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {sessions.map((session) => {
                const startTime = new Date(session.time_start)
                const endTime = session.time_end ? new Date(session.time_end) : new Date()
                const duration = formatDistance(startTime, endTime)

                return (
                  <tr key={session.id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-6 py-4">
                      <div>
                        <div className="font-medium text-gray-900">
                          {startTime.toLocaleDateString()}
                        </div>
                        <div className="text-sm text-gray-500">
                          {startTime.toLocaleTimeString()}
                          {session.time_end && ` - ${endTime.toLocaleTimeString()}`}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="font-medium text-gray-900">{session.table_number}</div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        <GamepadIcon className="w-4 h-4 text-gray-400" />
                        <span className="text-gray-900">{session.game_title}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        <Clock className="w-4 h-4 text-gray-400" />
                        <span className="font-semibold text-gray-900">
                          {session.hours_consumed.toFixed(2)}h
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span className="text-sm text-gray-600">{duration}</span>
                    </td>
                    <td className="px-6 py-4">
                      <span
                        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium capitalize ${getStatusColor(
                          session.status
                        )}`}
                      >
                        {session.status}
                      </span>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* Empty State */}
      {!isLoading && sessions.length === 0 && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-12 text-center">
          <GamepadIcon className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">No sessions found</h3>
          <p className="text-gray-600">Gaming sessions will appear here once members start playing</p>
        </div>
      )}
    </div>
  )
}
