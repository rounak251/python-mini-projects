#!/usr/bin/env python3
"""
Multi-Client Real-Time Chat Server
Using WebSocket and aiohttp
"""

import asyncio
import json
import random
import time
from typing import Dict

from aiohttp import web

# ---------- HTML frontend (embedded) ----------
HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>Multi-Client Real-Time Chat</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }

        .chat-container {
            width: 100%;
            max-width: 1400px;
            height: 90vh;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            display: flex;
            overflow: hidden;
            backdrop-filter: blur(10px);
        }

        .sidebar {
            width: 280px;
            background: linear-gradient(180deg, #2c3e50 0%, #1a252f 100%);
            color: white;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }

        .sidebar-header {
            padding: 25px 20px;
            background: rgba(0, 0, 0, 0.2);
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }

        .sidebar-header h2 {
            font-size: 1.3rem;
            margin-bottom: 5px;
        }

        .sidebar-header p {
            font-size: 0.85rem;
            opacity: 0.8;
        }

        .online-count {
            background: #27ae60;
            display: inline-block;
            padding: 2px 8px;
            border-radius: 20px;
            font-size: 0.75rem;
            margin-left: 8px;
        }

        .users-list {
            flex: 1;
            overflow-y: auto;
            padding: 15px;
        }

        .user-item {
            display: flex;
            align-items: center;
            padding: 10px;
            margin-bottom: 8px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            transition: all 0.3s ease;
        }

        .user-item:hover {
            background: rgba(255, 255, 255, 0.2);
            transform: translateX(5px);
        }

        .user-avatar {
            width: 35px;
            height: 35px;
            border-radius: 50%;
            background: linear-gradient(135deg, #667eea, #764ba2);
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 12px;
            font-weight: bold;
            font-size: 1rem;
        }

        .user-name {
            flex: 1;
            font-size: 0.9rem;
        }

        .current-user {
            border: 2px solid #667eea;
            background: rgba(102, 126, 234, 0.3);
        }

        .chat-area {
            flex: 1;
            display: flex;
            flex-direction: column;
            background: #f8f9fa;
        }

        .chat-header {
            background: white;
            padding: 20px 25px;
            border-bottom: 1px solid #e0e0e0;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
        }

        .chat-header h1 {
            font-size: 1.5rem;
            color: #333;
        }

        .connection-status {
            font-size: 0.8rem;
            margin-top: 5px;
        }

        .status-connected {
            color: #27ae60;
        }

        .status-disconnected {
            color: #e74c3c;
        }

        .messages-container {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }

        .message {
            display: flex;
            animation: slideIn 0.3s ease;
        }

        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .message-own {
            justify-content: flex-end;
        }

        .message-bubble {
            max-width: 70%;
            padding: 10px 15px;
            border-radius: 18px;
            position: relative;
        }

        .message-own .message-bubble {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border-bottom-right-radius: 4px;
        }

        .message-other .message-bubble {
            background: white;
            color: #333;
            border-bottom-left-radius: 4px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
        }

        .message-sender {
            font-size: 0.75rem;
            font-weight: bold;
            margin-bottom: 4px;
            opacity: 0.8;
        }

        .message-text {
            font-size: 0.95rem;
            word-wrap: break-word;
        }

        .message-time {
            font-size: 0.7rem;
            margin-top: 4px;
            opacity: 0.6;
            text-align: right;
        }

        .system-message {
            text-align: center;
            margin: 10px 0;
        }

        .system-message span {
            background: rgba(0, 0, 0, 0.1);
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.8rem;
            color: #666;
        }

        .typing-indicator {
            padding: 10px 20px;
            font-size: 0.85rem;
            color: #999;
            font-style: italic;
            min-height: 40px;
        }

        .input-area {
            background: white;
            padding: 20px;
            border-top: 1px solid #e0e0e0;
            display: flex;
            gap: 10px;
        }

        .input-area input {
            flex: 1;
            padding: 12px 15px;
            border: 2px solid #e0e0e0;
            border-radius: 25px;
            font-size: 0.95rem;
            outline: none;
            transition: all 0.3s ease;
        }

        .input-area input:focus {
            border-color: #667eea;
        }

        .input-area button {
            padding: 12px 30px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-size: 0.95rem;
            font-weight: bold;
            transition: transform 0.2s ease;
        }

        .input-area button:hover {
            transform: scale(1.05);
        }

        .input-area button:active {
            transform: scale(0.95);
        }

        ::-webkit-scrollbar {
            width: 8px;
        }

        ::-webkit-scrollbar-track {
            background: #f1f1f1;
        }

        ::-webkit-scrollbar-thumb {
            background: #888;
            border-radius: 4px;
        }

        ::-webkit-scrollbar-thumb:hover {
            background: #555;
        }

        @media (max-width: 768px) {
            .sidebar {
                width: 200px;
            }
            .message-bubble {
                max-width: 85%;
            }
            .input-area button {
                padding: 12px 20px;
            }
        }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="sidebar">
            <div class="sidebar-header">
                <h2>Online Users <span class="online-count" id="onlineCount">0</span></h2>
                <p>Real-time WebSocket Chat</p>
            </div>
            <div class="users-list" id="usersList">
                <div style="text-align: center; padding: 20px; opacity: 0.7;">Loading users...</div>
            </div>
        </div>

        <div class="chat-area">
            <div class="chat-header">
                <h1>💬 Multi-Client Chat Room</h1>
                <div class="connection-status">
                    Status: <span id="connectionStatus" class="status-disconnected">Disconnected</span>
                </div>
            </div>

            <div class="messages-container" id="messagesContainer">
                <div class="system-message">
                    <span>Welcome! Connect to start chatting</span>
                </div>
            </div>

            <div class="typing-indicator" id="typingIndicator"></div>

            <div class="input-area">
                <input type="text" id="messageInput" placeholder="Type your message here..." disabled>
                <button id="sendButton" disabled>Send</button>
            </div>
        </div>
    </div>

    <script>
        let ws = null;
        let currentClientId = null;
        let currentUsername = null;
        let typingTimeout = null;
        
        const messagesContainer = document.getElementById('messagesContainer');
        const messageInput = document.getElementById('messageInput');
        const sendButton = document.getElementById('sendButton');
        const connectionStatusSpan = document.getElementById('connectionStatus');
        const usersListDiv = document.getElementById('usersList');
        const onlineCountSpan = document.getElementById('onlineCount');
        const typingIndicatorDiv = document.getElementById('typingIndicator');
        
        function formatTime(timestamp) {
            if (!timestamp) return '';
            const date = new Date(timestamp);
            return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        }
        
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
        
        function addMessage(type, data) {
            const messageDiv = document.createElement('div');
            if (type === 'system') {
                messageDiv.className = 'system-message';
                messageDiv.innerHTML = `<span>${data.message}</span>`;
            } else if (type === 'chat') {
                const isOwn = data.sender.id === currentClientId;
                messageDiv.className = `message ${isOwn ? 'message-own' : 'message-other'}`;
                messageDiv.innerHTML = `
                    <div class="message-bubble">
                        ${!isOwn ? `<div class="message-sender">${escapeHtml(data.sender.username)}</div>` : ''}
                        <div class="message-text">${escapeHtml(data.message)}</div>
                        <div class="message-time">${formatTime(data.timestamp)}</div>
                    </div>
                `;
            }
            messagesContainer.appendChild(messageDiv);
            messageDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
        
        function updateUsersList(users) {
            if (!users || users.length === 0) {
                usersListDiv.innerHTML = '<div style="text-align: center; padding: 20px; opacity: 0.7;">No users online</div>';
                onlineCountSpan.textContent = '0';
                return;
            }
            onlineCountSpan.textContent = users.length;
            usersListDiv.innerHTML = users.map(user => `
                <div class="user-item ${user.id === currentClientId ? 'current-user' : ''}">
                    <div class="user-avatar">${user.username.charAt(0).toUpperCase()}</div>
                    <div class="user-name">${escapeHtml(user.username)}${user.id === currentClientId ? ' (You)' : ''}</div>
                </div>
            `).join('');
        }
        
        function handleWebSocketMessage(event) {
            try {
                const data = JSON.parse(event.data);
                switch (data.type) {
                    case 'init':
                        currentClientId = data.clientId;
                        currentUsername = data.username;
                        addMessage('system', { message: `Connected as ${currentUsername}` });
                        break;
                    case 'user_list':
                        updateUsersList(data.users);
                        break;
                    case 'user_joined':
                        addMessage('system', { message: data.message });
                        break;
                    case 'user_left':
                        addMessage('system', { message: data.message });
                        break;
                    case 'chat':
                        addMessage('chat', data);
                        break;
                    case 'typing':
                        if (data.sender.id !== currentClientId) {
                            if (data.isTyping) {
                                typingIndicatorDiv.textContent = `${data.sender.username} is typing...`;
                                clearTimeout(typingTimeout);
                                typingTimeout = setTimeout(() => {
                                    typingIndicatorDiv.textContent = '';
                                }, 2000);
                            } else {
                                typingIndicatorDiv.textContent = '';
                            }
                        }
                        break;
                }
            } catch (err) {
                console.error('Error parsing message:', err);
            }
        }
        
        function sendMessage() {
            const message = messageInput.value.trim();
            if (!message || !ws || ws.readyState !== WebSocket.OPEN) return;
            ws.send(JSON.stringify({ type: 'chat', message: message }));
            messageInput.value = '';
            messageInput.focus();
            if (ws.readyState === WebSocket.OPEN) {
                ws.send(JSON.stringify({ type: 'typing', isTyping: false }));
            }
        }
        
        function sendTypingIndicator(isTyping) {
            if (!ws || ws.readyState !== WebSocket.OPEN) return;
            ws.send(JSON.stringify({ type: 'typing', isTyping: isTyping }));
        }
        
        function connect() {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/ws`;
            ws = new WebSocket(wsUrl);
            
            ws.onopen = () => {
                connectionStatusSpan.textContent = 'Connected';
                connectionStatusSpan.className = 'status-connected';
                messageInput.disabled = false;
                sendButton.disabled = false;
                messageInput.focus();
                addMessage('system', { message: 'Connected to server' });
            };
            
            ws.onmessage = handleWebSocketMessage;
            ws.onerror = () => addMessage('system', { message: 'Connection error occurred' });
            ws.onclose = () => {
                connectionStatusSpan.textContent = 'Disconnected';
                connectionStatusSpan.className = 'status-disconnected';
                messageInput.disabled = true;
                sendButton.disabled = true;
                addMessage('system', { message: 'Disconnected. Please refresh the page.' });
                usersListDiv.innerHTML = '<div style="text-align: center; padding: 20px; opacity: 0.7;">Disconnected</div>';
                onlineCountSpan.textContent = '0';
            };
        }
        
        sendButton.addEventListener('click', sendMessage);
        messageInput.addEventListener('keypress', (e) => { if (e.key === 'Enter') sendMessage(); });
        
        let typingTimer;
        messageInput.addEventListener('input', () => {
            if (!ws || ws.readyState !== WebSocket.OPEN) return;
            sendTypingIndicator(true);
            clearTimeout(typingTimer);
            typingTimer = setTimeout(() => sendTypingIndicator(false), 1000);
        });
        messageInput.addEventListener('blur', () => sendTypingIndicator(false));
        
        connect();
    </script>
</body>
</html>
"""

# ---------- WebSocket server logic ----------
class ChatServer:
    def __init__(self):
        self.clients: Dict[web.WebSocketResponse, dict] = {}  # ws -> {id, username}
        self.next_id = 0

    def _generate_username(self) -> str:
        adjectives = ['Happy', 'Swift', 'Bright', 'Clever', 'Brave', 'Calm', 'Witty', 'Kind']
        nouns = ['Panda', 'Tiger', 'Eagle', 'Wolf', 'Fox', 'Bear', 'Hawk', 'Deer']
        adj = random.choice(adjectives)
        noun = random.choice(nouns)
        num = random.randint(10, 99)
        return f"{adj}{noun}{num}"

    async def _broadcast(self, message: dict, exclude_ws: web.WebSocketResponse = None):
        """Send a JSON message to all connected clients except `exclude_ws`."""
        data = json.dumps(message)
        for ws in list(self.clients.keys()):
            if ws is exclude_ws:
                continue
            if not ws.closed:
                try:
                    await ws.send_str(data)
                except Exception:
                    pass  # client disconnected

    async def _send_user_list(self, ws: web.WebSocketResponse):
        """Send current user list to a specific client."""
        users = [{"id": info["id"], "username": info["username"]} for info in self.clients.values()]
        await ws.send_str(json.dumps({"type": "user_list", "users": users}))

    async def _broadcast_user_list(self):
        """Send updated user list to all clients."""
        users = [{"id": info["id"], "username": info["username"]} for info in self.clients.values()]
        await self._broadcast({"type": "user_list", "users": users})

    async def websocket_handler(self, request: web.Request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)

        # Generate client ID and username
        client_id = f"client_{int(time.time() * 1000)}_{self.next_id}"
        self.next_id += 1
        username = self._generate_username()

        # Store client
        self.clients[ws] = {"id": client_id, "username": username}
        print(f"[+] Connected: {username} ({client_id}) | Total: {len(self.clients)}")

        # Send init data to the new client
        await ws.send_str(json.dumps({
            "type": "init",
            "clientId": client_id,
            "username": username
        }))

        # Send current user list to the new client
        await self._send_user_list(ws)

        # Notify others that a new user joined
        await self._broadcast({
            "type": "user_joined",
            "user": {"id": client_id, "username": username},
            "message": f"{username} joined the chat"
        }, exclude_ws=ws)

        # Broadcast updated user list to everyone
        await self._broadcast_user_list()

        # Handle incoming messages
        async for msg in ws:
            if msg.type == web.WSMsgType.TEXT:
                try:
                    data = json.loads(msg.data)
                    client_info = self.clients.get(ws)
                    if not client_info:
                        continue

                    if data.get("type") == "chat":
                        # Broadcast chat message
                        await self._broadcast({
                            "type": "chat",
                            "sender": {"id": client_info["id"], "username": client_info["username"]},
                            "message": data["message"],
                            "timestamp": time.time() * 1000
                        })
                        print(f"[CHAT] {client_info['username']}: {data['message']}")

                    elif data.get("type") == "typing":
                        # Broadcast typing indicator
                        await self._broadcast({
                            "type": "typing",
                            "sender": {"id": client_info["id"], "username": client_info["username"]},
                            "isTyping": data.get("isTyping", False)
                        }, exclude_ws=ws)

                except json.JSONDecodeError:
                    print("Received invalid JSON")
                except Exception as e:
                    print(f"Error handling message: {e}")

            elif msg.type == web.WSMsgType.ERROR:
                print(f"WebSocket error for {self.clients.get(ws, {}).get('username', 'unknown')}")

        # Client disconnected
        client_info = self.clients.pop(ws, None)
        if client_info:
            print(f"[-] Disconnected: {client_info['username']} ({client_info['id']}) | Remaining: {len(self.clients)}")
            await self._broadcast({
                "type": "user_left",
                "user": {"id": client_info["id"], "username": client_info["username"]},
                "message": f"{client_info['username']} left the chat"
            })
            await self._broadcast_user_list()

        return ws

# ---------- HTTP server ----------
async def index_handler(request: web.Request) -> web.Response:
    return web.Response(text=HTML_PAGE, content_type='text/html')

async def init_app():
    app = web.Application()
    chat = ChatServer()
    app.router.add_get('/', index_handler)
    app.router.add_get('/ws', chat.websocket_handler)
    return app

if __name__ == '__main__':
    web.run_app(init_app(), host='0.0.0.0', port=8080)