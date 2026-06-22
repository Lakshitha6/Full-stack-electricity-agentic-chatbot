import { Outlet } from 'react-router-dom';

import { Navbar } from './Navbar';
import { ChatFab } from '@/components/chat/ChatFab';
import { ChatModal } from '@/components/chat/ChatModal';

export function MainLayout() {
  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <main className="flex-1 container py-6">
        <Outlet />
      </main>
      <footer className="relative border-t py-8 text-center">
        <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-blue-500/20 to-transparent" />
        <p className="text-sm text-muted-foreground">
          © {new Date().getFullYear()} Electricity Board Agentic Platform. All rights reserved.
        </p>
      </footer>
      
      {/* Chat UI (Works on Desktop & Mobile) */}
      <ChatFab />
      <ChatModal />
    </div>
  );
}