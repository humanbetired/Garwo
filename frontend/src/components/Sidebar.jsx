import { MessageSquare, Plus, Trash2, Bot, Sun, Moon } from 'lucide-react'
import DocumentUpload from './DocumentUpload'

export default function Sidebar({ sessions, activeSession, onNewChat, onSelectSession, onDeleteSession, isDark, onToggleDark }) {
  return (
    <div className={`w-64 h-screen flex flex-col border-r ${isDark ? 'bg-gray-900 border-gray-800' : 'bg-white border-gray-100'}`}>
      {/* Logo */}
      <div className={`p-5 border-b ${isDark ? 'border-gray-800' : 'border-gray-100'}`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div>
              <h1 className={`font-bold text-lg leading-none ${isDark ? 'text-white' : 'text-gray-900'}`}>Garwo</h1>
              <p className={`text-xs mt-0.5 ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>Your Sigaran Jiwo</p>
            </div>
          </div>
          <button onClick={onToggleDark} className={`p-1.5 rounded-lg transition-colors ${isDark ? 'hover:bg-gray-800 text-gray-400' : 'hover:bg-gray-100 text-gray-500'}`}>
            {isDark ? <Sun size={16} /> : <Moon size={16} />}
          </button>
        </div>
      </div>

      {/* New Chat */}
      <div className="p-3">
        <button onClick={onNewChat} className={`w-full flex items-center gap-2 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${isDark ? 'bg-indigo-900 hover:bg-indigo-800 text-indigo-300' : 'bg-indigo-50 hover:bg-indigo-100 text-indigo-700'}`}>
          <Plus size={16} />
          New Chat
        </button>
      </div>

      {/* Sessions */}
      <div className="flex-1 overflow-y-auto px-3 space-y-1">
        {sessions.length === 0 && (
          <p className={`text-xs text-center mt-4 ${isDark ? 'text-gray-600' : 'text-gray-400'}`}>No conversations yet</p>
        )}
        {sessions.map(session => (
          <div
            key={session.id}
            onClick={() => onSelectSession(session.id)}
            className={`group flex items-center gap-2 px-3 py-2.5 rounded-lg cursor-pointer transition-colors ${
              activeSession === session.id
                ? isDark ? 'bg-indigo-900 text-indigo-300' : 'bg-indigo-50 text-indigo-700'
                : isDark ? 'hover:bg-gray-800 text-gray-400' : 'hover:bg-gray-50 text-gray-600'
            }`}
          >
            <MessageSquare size={14} className="shrink-0" />
            <span className="text-sm truncate flex-1">{session.title}</span>
            <button onClick={e => { e.stopPropagation(); onDeleteSession(session.id) }} className="opacity-0 group-hover:opacity-100 p-0.5 hover:text-red-500 transition-all">
              <Trash2 size={13} />
            </button>
          </div>
        ))}
      </div>

      {/* Document Upload */}
      {activeSession && (
        <DocumentUpload sessionId={activeSession} isDark={isDark} />
      )}

      {/* Footer */}
      <div className={`p-4 border-t ${isDark ? 'border-gray-800' : 'border-gray-100'}`}>
        <p className={`text-xs text-center ${isDark ? 'text-gray-600' : 'text-gray-400'}`}>Garwo v1.0.0</p>
      </div>
    </div>
  )
}