// import { create } from "zustand";

// interface ChatUIState {
//   currentSessionId: string | null;
//   isChatOpen: boolean;
//   isHistoryDrawerOpen: boolean;
//   requestNewChat: boolean;
//   isSidebarCollapsed: boolean;
  
//   setCurrentSession: (id: string | null) => void;
//   openChat: () => void;
//   closeChat: () => void;
//   toggleHistoryDrawer: () => void;
//   closeHistoryDrawer: () => void;
//   triggerNewChat: () => void;
//   resetNewChat: () => void;
//   reset: () => void;
//   toggleSidebar: () => void;
//   expandSidebar: () => void;
// }

// export const useChatStore = create<ChatUIState>((set) => ({
//   currentSessionId: null,
//   isChatOpen: false,
//   isHistoryDrawerOpen: false,
//   requestNewChat: false,
//   isSidebarCollapsed: false,
  
//   setCurrentSession: (id) => set({ currentSessionId: id }),
//   openChat: () => set({ isChatOpen: true }),
//   closeChat: () => set({ isChatOpen: false, isSidebarCollapsed: true }),

//   toggleHistoryDrawer: () => set((state) => ({ 
//     isHistoryDrawerOpen: !state.isHistoryDrawerOpen 
//   })),
  
//   closeHistoryDrawer: () => set({ isHistoryDrawerOpen: false }),
  
//   triggerNewChat: () => set({ requestNewChat: true }), // ← Action
//   resetNewChat: () => set({ requestNewChat: false }),  // ← Action
//   toggleSidebar: () => set((state) => ({ 
//     isSidebarCollapsed: !state.isSidebarCollapsed 
//   })),

//   expandSidebar: () => set({ isSidebarCollapsed: false }),

//   reset: () => set({ 
//     currentSessionId: null, 
//     isChatOpen: false, 
//     isHistoryDrawerOpen: false,
//     requestNewChat: false,
//     isSidebarCollapsed: false,
//   }),
// }));

// src/store/chatStore.ts
import { create } from 'zustand';

interface ChatUIState {
  isChatOpen: boolean;
  openChat: () => void;
  closeChat: () => void;
}

export const useChatStore = create<ChatUIState>((set) => ({
  isChatOpen: false,
  openChat: () => set({ isChatOpen: true }),
  closeChat: () => set({ isChatOpen: false }),
}));