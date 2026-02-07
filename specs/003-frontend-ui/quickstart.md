# Quickstart Guide: Frontend UI & UX for Todo Application

## Prerequisites

- Node.js 18+ installed
- npm or yarn package manager
- Access to backend API (FastAPI server running)
- Better Auth configured for authentication

## Setup Instructions

1. **Clone the repository**:
   ```bash
   git clone [repository-url]
   cd [project-directory]
   ```

2. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

3. **Install dependencies**:
   ```bash
   npm install
   # or
   yarn install
   ```

4. **Environment Configuration**:
   Create a `.env.local` file in the frontend directory:
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000/api
   NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:8000
   ```

5. **Run the development server**:
   ```bash
   npm run dev
   # or
   yarn dev
   ```

6. **Open your browser**:
   Visit `http://localhost:3000` to access the application.

## Available Scripts

- `npm run dev` - Start development server with hot reloading
- `npm run build` - Build the application for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint for code quality checks
- `npm run test` - Run component and integration tests

## Project Structure

```
frontend/
├── app/                    # Next.js App Router pages
│   ├── layout.tsx          # Root layout
│   ├── page.tsx            # Home page
│   ├── signup/page.tsx     # User signup page
│   ├── login/page.tsx      # User login page
│   ├── tasks/
│   │   ├── page.tsx        # Task list page
│   │   ├── [id]/page.tsx   # Individual task page
│   │   └── layout.tsx      # Task-specific layout
│   └── globals.css         # Global styles
├── components/             # Reusable UI components
├── lib/                    # Utility functions and services
├── hooks/                  # Custom React hooks
├── styles/                 # Styling utilities
├── public/                 # Static assets
└── types/                  # TypeScript type definitions
```

## Key Features

1. **Authentication Flow**:
   - User registration and login
   - JWT token management
   - Protected routes
   - Session handling

2. **Task Management**:
   - Create, read, update, delete (CRUD) operations
   - Mark tasks as complete/incomplete
   - Responsive design for all device sizes
   - Loading and error states

3. **Responsive Design**:
   - Mobile-first approach
   - Tablet and desktop optimized views
   - Touch-friendly interface

## API Integration

The frontend communicates with the backend API using authenticated requests:

```typescript
// Example API call with JWT
const response = await fetch('/api/tasks', {
  headers: {
    'Authorization': `Bearer ${jwtToken}`,
    'Content-Type': 'application/json',
  },
});
```

## Testing

Run the test suite:
```bash
npm run test
```

For development, run tests in watch mode:
```bash
npm run test:watch
```

Tests are located in the `tests/` directory and include:
- Component tests using React Testing Library
- Integration tests for user flows
- API mock tests