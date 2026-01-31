// User types
export interface User {
  id: string
  email: string
  full_name: string
  role: 'admin' | 'manager' | 'staff'
  is_active: boolean
  is_verified: boolean
}

export interface LoginCredentials {
  username: string  // email
  password: string
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
}

// Member types
export interface Member {
  id: string
  full_name: string
  mobile: string
  email?: string
  total_hours_granted: number
  total_hours_used: number
  balance_hours: number
  expiry_date?: string
  is_expired: boolean
  registration_date: string
  created_at: string
  updated_at: string
}

export interface MemberCreate {
  full_name: string
  mobile: string
  email?: string
}

// Purchase types
export interface Purchase {
  id: string
  member_id: string
  plan_name: string
  hours_granted: number
  amount_paid: number
  purchase_date: string
  expiry_date: string
  rollover_deadline: string
  rollover_status: 'pending' | 'completed' | 'expired'
  created_at: string
}

export interface PurchaseCreate {
  member_id: string
  plan_name: string
  hours_granted: number
  amount_paid: number
}

// Session types
export interface GamingSession {
  id: string
  member_id: string
  date: string
  time_start: string
  time_end?: string
  hours_consumed: number
  table_number: string
  game_title: string
  status: 'active' | 'completed' | 'cancelled'
  created_at: string
}

export interface SessionStart {
  member_id: string
  table_number: string
  game_title: string
}

// Dashboard types
export interface DashboardStats {
  total_members: number
  active_members: number
  expired_members: number
  total_revenue: number
  total_hours_granted: number
  total_hours_used: number
  total_balance_hours: number
  active_sessions: number
  members_expiring_soon: number
}

export interface RevenueStats {
  total_revenue: number
  revenue_this_month: number
  revenue_last_month: number
  average_purchase_value: number
  total_purchases: number
  purchases_this_month: number
  payment_methods: Record<string, number>
}

// API response types
export interface ApiResponse<T> {
  data?: T
  success?: boolean
  error?: string
  message?: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  total_pages: number
}
