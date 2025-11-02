'use client';

import React, { useState } from 'react';
import {
  Box,
  TextField,
  Button,
  Paper,
  List,
  ListItem,
  ListItemText,
  IconButton,
  Typography,
  Container,
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import { useChatStore } from '@/store/chatStore';
import api from '@/utils/api';
import { ChatMessage } from '@/types';
import { useAuthStore } from '@/store/authStore';
import { useRouter } from 'next/navigation';

const ChatInterface: React.FC = () => {
  const { messages, addMessage, clearMessages } = useChatStore();
  const { logout } = useAuthStore();
  const router = useRouter();
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const generateMessageId = (() => {
    let counter = 0;
    return () => `msg-${counter++}-${Math.random().toString(36).slice(2)}`;
  })();

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMsg: ChatMessage = { id: generateMessageId(), role: 'user', content: input };
    addMessage(userMsg);
    setInput('');
    setLoading(true);

    try {
      const response = await api.post('/chat', { message: input });
      const aiMsg: ChatMessage = { id: generateMessageId(), role: 'ai', content: response.data.reply };
      addMessage(aiMsg);
    } catch (error) {
      console.error('API Error:', error);
      addMessage({ id: Date.now() + 1, role: 'ai', content: '抱歉，回复生成失败。请重试。' });
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    clearMessages();
    setInput('');
  };

  return (
    <Container maxWidth="md" sx={{ mt: 4, height: '80vh' }}>
      <Paper elevation={3} sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
        {/* 顶部工具栏 */}
        <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider', display: 'flex', alignItems: 'center', gap: 2 }}>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>AI 聊天机器人 (Gemini 2.5 Pro)</Typography>
          <Button onClick={handleClear} size="small" variant="outlined">清空聊天</Button>
          <Button onClick={() => { logout(); router.push('/login'); }} size="small" variant="outlined">登出</Button>
        </Box>

        {/* 聊天消息列表 */}
        <List sx={{ flexGrow: 1, overflowY: 'auto', p: 2 }}>
          {messages.map((msg) => (
            <ListItem key={msg.id} sx={{ justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start' }}>
              <Paper
                sx={{
                  p: 2,
                  maxWidth: '70%',
                  backgroundColor: msg.role === 'user' ? '#e3f2fd' : '#f5f5f5',
                  ml: msg.role === 'ai' ? 0 : 'auto',
                }}
              >
                <ListItemText primary={msg.content} primaryTypographyProps={{ variant: 'body2' }} />
              </Paper>
            </ListItem>
          ))}
          {loading && (
            <ListItem sx={{ justifyContent: 'flex-start' }}>
              <Paper sx={{ p: 2, maxWidth: '70%', backgroundColor: '#f5f5f5' }}>
                <Typography variant="body2">AI 正在思考...</Typography>
              </Paper>
            </ListItem>
          )}
        </List>

        {/* 输入框 */}
        <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider' }}>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <TextField
              fullWidth
              variant="outlined"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
              placeholder="输入消息..."
              disabled={loading}
            />
            <IconButton onClick={handleSend} disabled={loading || !input.trim()} color="primary">
              <SendIcon />
            </IconButton>
          </Box>
        </Box>
      </Paper>
    </Container>
  );
};

export default ChatInterface;