import { useEffect, useRef } from 'react'
import MessageBubble from './MessageBubble'
import { Bot } from 'lucide-react'

export default function ChatWindow({ messages, isLoading, isDark }) {
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isLoading])

  return (
    <div className={`flex-1 overflow-y-auto px-6 py-6 space-y-4 ${isDark ? 'bg-gray-950' : 'bg-gray-50'}`}>
      {messages.length === 0 && (
        <div className="flex flex-col items-center justify-center h-full gap-3 text-center">
          <div>
            <h2 className={`font-semibold ${isDark ? 'text-gray-200' : 'text-gray-800'}`}>Halo! Saya Garwo</h2>
            <p className={`text-sm mt-1 ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>
              Ceritakan harimu, catat pengeluaran,<br />atau tanyakan apa saja.
            </p>
          </div>
        </div>
      )}

      {messages.map((msg, i) => (
        <MessageBubble
          key={i}
          message={msg}
          isDark={isDark}
          isLatest={msg.role === 'assistant' && i === messages.length - 1}
        />
      ))}

      {isLoading && (
        <div className="flex gap-3">
          <div className={`w-8 h-8 rounded-full flex items-center justify-center ${isDark ? 'bg-gray-800 border border-gray-700' : 'bg-white border border-gray-200'}`}>
            <Bot size={15} className="text-indigo-500" />
          </div>
          <div className={`rounded-2xl rounded-tl-sm px-4 py-3 ${isDark ? 'bg-gray-800 border border-gray-700' : 'bg-white border border-gray-100 shadow-sm'}`}>
            <div className="flex gap-1 items-center h-4">
              <div className="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-bounce [animation-delay:0ms]" />
              <div className="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-bounce [animation-delay:150ms]" />
              <div className="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-bounce [animation-delay:300ms]" />
            </div>
          </div>
        </div>
      )}

      <div ref={bottomRef} />
    </div>
  )
}