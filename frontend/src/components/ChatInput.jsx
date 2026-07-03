import { useState } from 'react'
import { Send } from 'lucide-react'

export default function ChatInput({ onSend, disabled, isDark }) {
  const [value, setValue] = useState('')

  const handleSend = () => {
    if (!value.trim() || disabled) return
    onSend(value.trim())
    setValue('')
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className={`p-4 border-t ${isDark ? 'bg-gray-900 border-gray-800' : 'bg-white border-gray-100'}`}>
      <div className={`flex items-end gap-3 rounded-2xl px-4 py-3 border transition-all ${
        isDark
          ? 'bg-gray-800 border-gray-700 focus-within:border-indigo-500'
          : 'bg-gray-50 border-gray-200 focus-within:border-indigo-300 focus-within:bg-white'
      }`}>
        <textarea
          value={value}
          onChange={e => setValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Luapin ke Garwo..."
          rows={1}
          disabled={disabled}
          className={`flex-1 bg-transparent text-sm resize-none outline-none max-h-32 ${
            isDark ? 'text-gray-200 placeholder-gray-600' : 'text-gray-800 placeholder-gray-400'
          }`}
        />
        <button
          onClick={handleSend}
          disabled={!value.trim() || disabled}
          className="w-8 h-8 bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-300 dark:disabled:bg-gray-700 rounded-xl flex items-center justify-center transition-colors shrink-0"
        >
          <Send size={14} className="text-white" />
        </button>
      </div>
      <p className={`text-xs text-center mt-2 ${isDark ? 'text-gray-600' : 'text-gray-400'}`}>
        Enter to send, Shift+Enter for new line
      </p>
    </div>
  )
}