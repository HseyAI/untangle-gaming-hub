# UNTANGLE Frontend

Modern React + TypeScript frontend for the UNTANGLE Gaming Hub Management System.

## Tech Stack

- **Framework:** React 18 + TypeScript
- **Build Tool:** Vite
- **Styling:** Tailwind CSS
- **Routing:** React Router v6
- **HTTP Client:** Axios
- **Icons:** Lucide React
- **Date Handling:** date-fns
- **Charts:** Recharts (for future analytics)

## Features

- ✅ JWT Authentication with auto-refresh
- ✅ Protected Routes
- ✅ Dashboard with real-time stats
- ✅ Member Management
- ✅ Purchase Tracking
- ✅ Gaming Session Monitoring
- ✅ Responsive Design
- ✅ Role-Based Access Control
- ✅ Error Handling

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Backend API running on http://localhost:8000

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

The app will be available at **http://localhost:3000**

### Build for Production

```bash
npm run build
npm run preview
```

## Project Structure

```
frontend/
├── src/
│   ├── components/      # Reusable components
│   │   ├── Layout.tsx         # Main layout with sidebar
│   │   └── ProtectedRoute.tsx # Route protection
│   ├── context/         # React Context
│   │   └── AuthContext.tsx    # Authentication state
│   ├── pages/           # Page components
│   │   ├── LoginPage.tsx
│   │   ├── DashboardPage.tsx
│   │   ├── MembersPage.tsx
│   │   ├── PurchasesPage.tsx
│   │   └── SessionsPage.tsx
│   ├── services/        # API services
│   │   └── api.ts            # Axios client & API methods
│   ├── types/           # TypeScript types
│   │   └── index.ts
│   ├── App.tsx          # Main app component
│   ├── main.tsx         # Entry point
│   └── index.css        # Global styles
├── index.html
├── package.json
├── vite.config.ts
├── tailwind.config.js
└── tsconfig.json
```

## Environment Variables

Create a `.env` file:

```env
VITE_API_URL=http://localhost:8000/api/v1
```

## Test Credentials

```
Admin:   admin@untangle.com    / password123
Manager: manager@untangle.com  / password123
Staff:   staff@untangle.com    / password123
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint
- `npm run type-check` - Run TypeScript compiler

## Features by Page

### Login Page
- Email/password authentication
- JWT token storage
- Auto-redirect to dashboard
- Test credentials displayed

### Dashboard
- Real-time statistics
- Revenue overview
- Active sessions count
- Member alerts (expiring/expired)

### Members Page
- List all members
- Search by name/mobile
- View balance and expiry
- Member status indicators

### Purchases Page
- View all credit purchases
- Track rollover status
- Filter by member
- Expiry date tracking

### Sessions Page
- Active session monitoring
- Session history
- Game and station tracking
- Duration calculation

## API Integration

The frontend communicates with the backend API using Axios:

- **Base URL:** `http://localhost:8000/api/v1`
- **Authentication:** JWT Bearer token
- **Auto-refresh:** Token refresh on 401 errors
- **Interceptors:** Request/response interceptors for auth

## Future Enhancements

- [ ] Add member form (create/edit)
- [ ] Purchase creation form
- [ ] Session start/end controls
- [ ] Advanced filtering and sorting
- [ ] Data export functionality
- [ ] Real-time updates (WebSocket)
- [ ] Dark mode support
- [ ] Mobile responsive improvements

## Troubleshooting

### Backend Connection Issues

If you see "Failed to load" errors:
1. Ensure backend is running on port 8000
2. Check `.env` file has correct API_URL
3. Verify CORS is enabled on backend

### Build Issues

```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Type Errors

```bash
# Run type check
npm run type-check
```

## License

Private - UNTANGLE Gaming Hub Management System
