import { Message } from '@/types/chat';
import { chatService } from "@/services/chat";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useCallback, useState } from "react";


export const useChatSession = (electricityId: string) => {
  const queryClient = useQueryClient();
  const [currentMessages, setCurrentMessages] = useState<Message[]>([]);
  const [currentSessionId, setCurrentSession] = useState<string | null>(null);

  // Fetch sessions (cached, auto-refetch on focus)
  const { data: sessions, isLoading: sessionsLoading } = useQuery({
    queryKey: ['chat-sessions', electricityId],
    queryFn: () => chatService.getSessions(electricityId),
    enabled: !!electricityId,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });


  // Mutation: send message
  const sendMessageMutation = useMutation({
    mutationFn: (message: string) => 
      chatService.sendMessage({
        electricity_id: electricityId,
        session_id: currentSessionId || undefined, // use existing session if available
        message
      }),
    onMutate: async (message) => {
      // add user message immediately
      const userMsg: Message = {
        id: `opt-${Date.now()}`,
        role: 'user',
        content: message,
        timestamp: new Date().toISOString(),
      };
      setCurrentMessages(prev => [...prev, userMsg]);
      return { userMsg };
    },
    onSuccess: (data, sentMessage) => {
      if (data.session_id && currentSessionId !== data.session_id) {
        setCurrentSession(data.session_id);
      }

      const botMsg: Message = {
        id: data.message_id,
        role: 'assistant',
        content: data.response,
        timestamp: data.timestamp,
        metadata: data.metadata,
      };
      
      setCurrentMessages(prev => {
        // Keep the user message by removing the 'opt-' prefix for the one that matches
        const updatedPrev = prev.map(m => 
          m.id.startsWith('opt-') && m.content === sentMessage 
            ? { ...m, id: `msg-${Date.now()}` } 
            : m
        );
        return [...updatedPrev, botMsg];
      });
      
      // Refresh session list in background
      queryClient.invalidateQueries({ queryKey: ['chat-sessions', electricityId] });
    },
    onError: (error) => {
      // Remove optimistic message on error
      setCurrentMessages(prev => prev.filter(m => !m.id.startsWith('opt-')));
      console.error('Failed to send message:', error);
    },
  });

  const loadSessionMessages = useCallback(async (sessionId: string) => {
    setCurrentSession(sessionId);  // Track current session
    const msgs = await chatService.getMessages(sessionId);
    setCurrentMessages(msgs);
    return msgs;
  }, []);

  // Create new session
  const createNewSession = useCallback(async (title?: string) => {
    const session = await chatService.createSession(electricityId, title);
    queryClient.invalidateQueries({ queryKey: ['chat-sessions', electricityId] });
    setCurrentSession(session.session_id);
    setCurrentMessages([]);
    return session;
  }, [electricityId, queryClient]);


  
  return {
    sessions,
    sessionsLoading,
    messages: currentMessages,
    isSending: sendMessageMutation.isPending,
    sendMessage: sendMessageMutation.mutateAsync,
    loadSessionMessages,
    createNewSession,
    currentSessionId,
    setCurrentSession,
  };
};