import { useEffect, useState } from 'react'
import { dashboardApi } from '../services/api'
import type { DashboardStats, RevenueStats } from '../types'
import { Users, TrendingUp, Clock, Activity } from 'lucide-react'

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [revenue, setRevenue] = useState<RevenueStats | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      setIsLoading(true)
      const [statsData, revenueData] = await Promise.all([
        dashboardApi.getStats(),
        dashboardApi.getRevenue(),
      ])
      setStats(statsData)
      setRevenue(revenueData)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load dashboard data')
    } finally {
      setIsLoading(false)
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
        {error}
      </div>
    )
  }

  const statCards = [
    {
      title: 'Total Members',
      value: stats?.total_members || 0,
      subtitle: `${stats?.active_members || 0} active`,
      icon: Users,
      color: 'bg-blue-500',
    },
    {
      title: 'Total Revenue',
      value: `₱${revenue?.total_revenue?.toLocaleString() || 0}`,
      subtitle: `₱${revenue?.revenue_this_month?.toLocaleString() || 0} this month`,
      icon: TrendingUp,
      color: 'bg-green-500',
    },
    {
      title: 'Total Hours',
      value: `${stats?.total_hours_granted || 0}h`,
      subtitle: `${stats?.total_balance_hours || 0}h remaining`,
      icon: Clock,
      color: 'bg-purple-500',
    },
    {
      title: 'Active Sessions',
      value: stats?.active_sessions || 0,
      subtitle: `${stats?.total_hours_used || 0}h consumed`,
      icon: Activity,
      color: 'bg-orange-500',
    },
  ]

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-2">Welcome to UNTANGLE management system</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {statCards.map((stat, index) => {
          const Icon = stat.icon
          return (
            <div key={index} className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <div className="flex items-center justify-between mb-4">
                <div className={`${stat.color} p-3 rounded-lg`}>
                  <Icon className="w-6 h-6 text-white" />
                </div>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-600 mb-1">{stat.title}</p>
                <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
                <p className="text-sm text-gray-500 mt-1">{stat.subtitle}</p>
              </div>
            </div>
          )
        })}
      </div>

      {/* Additional Info */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Revenue Breakdown */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Revenue Overview</h3>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Total Purchases</span>
              <span className="font-semibold">{revenue?.total_purchases || 0}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Average Purchase</span>
              <span className="font-semibold">₱{revenue?.average_purchase_value?.toFixed(2) || 0}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">This Month</span>
              <span className="font-semibold text-green-600">
                +₱{revenue?.revenue_this_month?.toLocaleString() || 0}
              </span>
            </div>
          </div>
        </div>

        {/* Alerts */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Alerts</h3>
          <div className="space-y-3">
            {stats && stats.members_expiring_soon > 0 && (
              <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                <p className="text-sm font-medium text-yellow-800">
                  {stats.members_expiring_soon} member(s) expiring soon
                </p>
              </div>
            )}
            {stats && stats.expired_members > 0 && (
              <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
                <p className="text-sm font-medium text-red-800">
                  {stats.expired_members} expired member(s)
                </p>
              </div>
            )}
            {stats && stats.members_expiring_soon === 0 && stats.expired_members === 0 && (
              <p className="text-gray-500 text-sm">All clear! No alerts at this time.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
