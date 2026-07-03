import { Bot, User, Wrench } from 'lucide-react'
import { useState, useEffect } from 'react'
import ReactMarkdown from 'react-markdown'

function TypingText({ text, isDark }) {
  const [displayed, setDisplayed] = useState('')
  const [done, setDone] = useState(false)

  useEffect(() => {
    setDisplayed('')
    setDone(false)
    let i = 0
    const interval = setInterval(() => {
      if (i < text.length) {
        setDisplayed(text.slice(0, i + 1))
        i++
      } else {
        setDone(true)
        clearInterval(interval)
      }
    }, 18)
    return () => clearInterval(interval)
  }, [text])

  return (
    <span>
      <MarkdownContent text={displayed} isDark={isDark} />
      {!done && <span className="inline-block w-0.5 h-3.5 bg-indigo-400 ml-0.5 animate-pulse rounded-sm" />}
    </span>
  )
}

function MarkdownContent({ text, isDark }) {
  return (
    <ReactMarkdown
      components={{
        p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
        strong: ({ children }) => <strong className="font-semibold">{children}</strong>,
        em: ({ children }) => <em className="italic">{children}</em>,
        ul: ({ children }) => <ul className="list-disc list-inside mb-2 space-y-1">{children}</ul>,
        ol: ({ children }) => <ol className="list-decimal list-inside mb-2 space-y-1">{children}</ol>,
        li: ({ children }) => <li className="text-sm">{children}</li>,
        code: ({ inline, children }) => inline
          ? <code className={`px-1.5 py-0.5 rounded text-xs font-mono ${isDark ? 'bg-gray-700 text-indigo-300' : 'bg-gray-100 text-indigo-600'}`}>{children}</code>
          : <pre className={`p-3 rounded-lg text-xs font-mono overflow-x-auto my-2 ${isDark ? 'bg-gray-700 text-gray-200' : 'bg-gray-100 text-gray-800'}`}><code>{children}</code></pre>,
        blockquote: ({ children }) => (
          <blockquote className={`border-l-2 border-indigo-400 pl-3 my-2 italic ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
            {children}
          </blockquote>
        ),
        h1: ({ children }) => <h1 className="text-base font-bold mb-2">{children}</h1>,
        h2: ({ children }) => <h2 className="text-sm font-bold mb-1.5">{children}</h2>,
        h3: ({ children }) => <h3 className="text-sm font-semibold mb-1">{children}</h3>,
      }}
    >
      {text}
    </ReactMarkdown>
  )
}

const TOOL_LABELS = {
  save_expense: 'Catat Pengeluaran',
  get_expenses: 'Baca Pengeluaran',
  delete_expense: 'Hapus Pengeluaran',
  add_agenda: 'Tambah Agenda',
  get_agenda: 'Baca Agenda',
  delete_agenda: 'Hapus Agenda',
  search_web: 'Web Search',
  get_weather: 'Cek Cuaca',
  sync_agenda_to_calendar: 'Sync ke Google Calendar',
  get_calendar_events: 'Baca Google Calendar',
  delete_calendar_event: 'Hapus dari Google Calendar',
  send_telegram_message: 'Kirim Telegram',
  get_telegram_messages: 'Baca Telegram',
  send_expense_report_to_telegram: 'Laporan ke Telegram',
  send_agenda_reminder_to_telegram: 'Reminder ke Telegram',
}

export default function MessageBubble({ message, isDark, isLatest }) {
  const isUser = message.role === 'user'

  return (
    <div className={`flex gap-3 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
      <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${
        isUser ? 'bg-indigo-600' : isDark ? 'bg-gray-800 border border-gray-700' : 'bg-white border border-gray-200'
      }`}>
        {isUser
          ? <User size={15} className="text-white" />
          : <Bot size={15} className="text-indigo-500" />
        }
      </div>

      <div className="flex flex-col gap-1.5 max-w-[75%]">
        {/* Tool badges */}
        {message.tools_used && message.tools_used.length > 0 && (
          <div className="flex flex-wrap gap-1">
            {message.tools_used.map(tool => (
              <span key={tool} className={`flex items-center gap-1 text-xs px-2 py-0.5 rounded-full ${
                isDark ? 'bg-indigo-900 text-indigo-300' : 'bg-indigo-50 text-indigo-600'
              }`}>
                <Wrench size={10} />
                {TOOL_LABELS[tool] || tool}
              </span>
            ))}
          </div>
        )}

        {/* Bubble */}
        <div className={`px-4 py-3 rounded-2xl text-sm leading-relaxed ${
          isUser
            ? 'bg-indigo-600 text-white rounded-tr-sm'
            : isDark
              ? 'bg-gray-800 border border-gray-700 text-gray-200 rounded-tl-sm'
              : 'bg-white border border-gray-100 text-gray-800 rounded-tl-sm shadow-sm'
        }`}>
          {isUser
            ? message.content
            : isLatest
              ? <TypingText text={message.content} isDark={isDark} />
              : <MarkdownContent text={message.content} isDark={isDark} />
          }
        </div>
      </div>
    </div>
  )
}