import { X, History, Plus } from 'lucide-react';
import { useState } from 'react';

import { useChatStore } from '@/store/chatStore';
import { useAuthStore } from '@/store/authStore';
import { useChatSession } from '@/hooks/useChatSession';
import { ChatWindow } from './ChatWindow';
import { SessionItem } from './SessionItem';

export function ChatModal() {
  const { isChatOpen, closeChat } = useChatStore();
  const { user } = useAuthStore();
  const { 
    sessions, 
    messages, 
    sendMessage, 
    isSending,
    loadSessionMessages,
    createNewSession 
  } = useChatSession(user?.electricity_id || '');

  const [showHistory, setShowHistory] = useState(false);

  if (!isChatOpen) return null;

  return (
    <div className="fixed inset-0 z-50 bg-background/95 backdrop-blur-sm flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b bg-background">
        <button
          onClick={() => setShowHistory(!showHistory)}
          className="p-2 hover:bg-muted rounded-full transition-colors"
          aria-label="Toggle history"
        >
          <History className="w-5 h-5" />
        </button>
        
        <h2 className="font-semibold text-lg">BillBot Chat</h2>
        
        <button
          onClick={closeChat}
          className="p-2 hover:bg-muted rounded-full transition-colors"
          aria-label="Close chat"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* History View */}
      {showHistory ? (
        <div className="flex flex-col h-full">
          <div className="p-4 border-b flex items-center justify-between bg-muted/30">
            <h3 className="font-medium">Chat History</h3>
            <button
              onClick={async () => {
                await createNewSession();
                // Clear current view to show empty chat
                setShowHistory(false);
              }}
              className="text-sm text-primary hover:underline flex items-center gap-1"
            >
              <Plus className="w-3 h-3" /> New Chat
            </button>
          </div>
          <div className="flex-1 overflow-y-auto p-2 space-y-1">
            {sessions?.map((session) => (
              <SessionItem 
                key={session.session_id} 
                session={session}
                onClick={async () => {
                  await loadSessionMessages(session.session_id);
                  setShowHistory(false);
                }}
              />
            ))}
          </div>
        </div>
      ) : (
        /* Chat Window (Centered on Desktop, Full-width on Mobile) */
        <div className="flex-1 flex flex-col max-w-4xl mx-auto w-full h-full border-x border-muted/20">
          <ChatWindow
            messages={messages}
            onSend={async (message) => { await sendMessage(message); }}
            isLoading={isSending}
          />
        </div>
      )}
    </div>
  );
}