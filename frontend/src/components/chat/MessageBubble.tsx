// Message styling

import { cn } from '@/utils/cn';

interface MessageBubbleProps {
  message: {
    role: 'user' | 'assistant';
    content: string;
    timestamp: string;
    metadata?: { sql?: string; error?: string };
  };
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === 'user';
  
  return (
    <div className={cn(
      "flex gap-3 py-4",
      isUser ? "justify-end" : "justify-start"
    )}>
      {!isUser && (
        <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0">
          <span className="text-xs font-bold text-primary">AI</span>
        </div>
      )}
      
      <div className={cn(
        "max-w-[85%] rounded-2xl px-4 py-3",
        isUser 
          ? "bg-primary text-primary-foreground rounded-br-md" 
          : "bg-muted rounded-bl-md"
      )}>
        <p className="text-sm whitespace-pre-wrap">{message.content}</p>
        
        {/* Debug: Show SQL metadata in dev mode */}
        {import.meta.env.DEV && message.metadata?.sql && (
          <details className="mt-2 text-xs opacity-70">
            <summary className="cursor-pointer">🔍 SQL</summary>
            <pre className="mt-1 p-2 bg-black/10 rounded overflow-x-auto">
              {message.metadata.sql}
            </pre>
          </details>
        )}
        
        <p className={cn(
          "text-xs mt-1",
          isUser ? "text-primary-foreground/70" : "text-muted-foreground"
        )}>
          {new Date(message.timestamp).toLocaleTimeString([], { 
            hour: '2-digit', 
            minute: '2-digit' 
          })}
        </p>
      </div>
      
      {isUser && (
        <div className="w-8 h-8 rounded-full bg-muted flex items-center justify-center flex-shrink-0">
          <span className="text-xs font-bold">You</span>
        </div>
      )}
    </div>
  );
}