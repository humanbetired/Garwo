import { useState, useCallback } from 'react'
import Sidebar from './components/Sidebar'
import ChatWindow from './components/ChatWindow'
import ChatInput from './components/ChatInput'

const generateId = () => Math.random().toString(36).substring(2, 10)

export default function App() {
  const [sessions, setSessions] = useState([])
  const [activeSessionId, setActiveSessionId] = useState(null)
  const [chats, setChats] = useState({})
  const [isLoading, setIsLoading] = useState(false)
  const [isDark, setIsDark] = useState(false)

  const activeMessages = chats[activeSessionId] || []

  const handleNewChat = useCallback(() => {
    const id = generateId()
    setSessions(prev => [{ id, title: 'New Chat' }, ...prev])
    setChats(prev => ({ ...prev, [id]: [] }))
    setActiveSessionId(id)
  }, [])

  const handleSelectSession = (id) => setActiveSessionId(id)

  const handleDeleteSession = (id) => {
    setSessions(prev => prev.filter(s => s.id !== id))
    setChats(prev => { const c = { ...prev }; delete c[id]; return c })
    if (activeSessionId === id) setActiveSessionId(null)
  }

  const handleSend = async (message) => {
    if (!activeSessionId) return
    const userMsg = { role: 'user', content: message }
    setChats(prev => ({
      ...prev,
      [activeSessionId]: [...(prev[activeSessionId] || []), userMsg]
    }))
    setSessions(prev => prev.map(s =>
      s.id === activeSessionId && s.title === 'New Chat'
        ? { ...s, title: message.slice(0, 30) + (message.length > 30 ? '...' : '') }
        : s
    ))
    setIsLoading(true)
    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: activeSessionId, message })
      })
      const data = await res.json()
      setChats(prev => ({
        ...prev,
        [activeSessionId]: [...(prev[activeSessionId] || []), { role: 'assistant', content: data.reply, tools_used: data.tools_used || [] }]
      }))
    } catch (err) {
      console.error(err)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className={`flex h-screen font-sans ${isDark ? 'bg-gray-950' : 'bg-gray-50'}`}>
      <Sidebar
        sessions={sessions}
        activeSession={activeSessionId}
        onNewChat={handleNewChat}
        onSelectSession={handleSelectSession}
        onDeleteSession={handleDeleteSession}
        isDark={isDark}
        onToggleDark={() => setIsDark(d => !d)}
      />
      <div className="flex-1 flex flex-col overflow-hidden">
        {activeSessionId ? (
          <>
            <div className={`px-6 py-4 border-b ${isDark ? 'bg-gray-900 border-gray-800' : 'bg-white border-gray-100'}`}>
              <h2 className={`font-semibold text-sm ${isDark ? 'text-gray-100' : 'text-gray-800'}`}>
                {sessions.find(s => s.id === activeSessionId)?.title || 'Chat'}
              </h2>
              <p className={`text-xs ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>Garwo · Online</p>
            </div>
            <ChatWindow messages={activeMessages} isLoading={isLoading} isDark={isDark} />
            <ChatInput onSend={handleSend} disabled={isLoading} isDark={isDark} />
          </>
        ) : (
          <div className="flex-1 flex flex-col items-center justify-center gap-4">
            <div className={`w-16 h-16 rounded-2xl flex items-center justify-center ${isDark ? 'bg-indigo-900' : 'bg-indigo-50'}`}>
              <span className="text-3xl">?</span>
            </div>
            <div className="text-center">
              <h2 className={`font-semibold ${isDark ? 'text-gray-100' : 'text-gray-800'}`}>Selamat datang di Garwo</h2>
              <p className={`text-sm mt-1 ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>Mulai percakapan baru untuk memulai</p>
            </div>
            <button
              onClick={handleNewChat}
              className="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-medium rounded-md transition-colors"
            >
              Mulai Chat
            </button>
          </div>
        )}
      </div>
    </div>
  )
}