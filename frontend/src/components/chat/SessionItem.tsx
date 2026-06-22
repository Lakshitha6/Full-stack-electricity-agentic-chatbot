// Histories

import { formatDistanceToNow } from 'date-fns';
import type { Session } from '@/types/chat';
import { cn } from '@/utils/cn';

interface SessionItemProps {
  session: Session;
  onClick: () => void;
  isActive?: boolean;
}

export function SessionItem({ session, onClick, isActive }: SessionItemProps) {
  const timeAgo = session.last_message_at || session.started_at;
  
  return (
    <button
      onClick={onClick}
      className={cn(
        "w-full text-left p-3 rounded-lg transition-colors",
        isActive 
          ? "bg-primary/10 border border-primary/20" 
          : "hover:bg-muted"
      )}
    >
      <p className="font-medium text-sm truncate">{session.title}</p>
      <p className="text-xs text-muted-foreground mt-1">
        {formatDistanceToNow(new Date(timeAgo), { addSuffix: true })}
      </p>
    </button>
  );
}