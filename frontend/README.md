# Todo Application Frontend

This is the frontend for the Todo application built with Next.js 16+ using the App Router.

## Features

- User authentication (signup/login)
- Task management (create, read, update, delete)
- Responsive design for mobile, tablet, and desktop
- JWT-based authentication
- Loading and error states
- Form validation

## Tech Stack

- Next.js 16+ with App Router
- React 18+
- TypeScript
- Tailwind CSS
- GSAP for animations

## Getting Started

First, run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

## Environment Variables

Create a `.env.local` file in the root of the frontend directory:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:8000
```

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

## Deployment

The application can be deployed to platforms like Vercel, Netlify, or any other hosting provider that supports Next.js applications.