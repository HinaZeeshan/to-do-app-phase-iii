'use client';

import Header from '../../components/layout/Header';
import { AuthWrapper } from '../../components/auth/AuthWrapper';
import Chatbot from '../../components/ui/Chatbot';

export default function TasksLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <AuthWrapper requireAuth={true}>
      <div className="min-h-screen bg-gray-50">
        <Header />
        <main>{children}</main>
        <Chatbot />
      </div>
    </AuthWrapper>
  );
}