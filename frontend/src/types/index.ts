export interface ChatMessage {
  id: string | number; 
  role: 'user' | 'ai';
  content: string;
  timestamp?: number;
}