import { useState } from 'react'
import { Upload, FileText, Trash2, CheckCircle } from 'lucide-react'

export default function DocumentUpload({ sessionId, isDark }) {
  const [docs, setDocs] = useState([])
  const [uploading, setUploading] = useState(false)
  const [message, setMessage] = useState('')

  const handleUpload = async (e) => {
    const file = e.target.files[0]
    if (!file) return

    setUploading(true)
    setMessage('')

    const formData = new FormData()
    formData.append('file', file)

    try {
      const res = await fetch(`/api/rag/upload/${sessionId}`, {
        method: 'POST',
        body: formData
      })
      const data = await res.json()
      setMessage(`${data.message} (${data.chunks} chunks)`)
      setDocs(prev => [...prev, data.doc_name])
    } catch (err) {
      setMessage('Gagal upload dokumen')
    } finally {
      setUploading(false)
    }
  }

  const handleDelete = async (docName) => {
    await fetch(`/api/rag/documents/${sessionId}/${docName}`, { method: 'DELETE' })
    setDocs(prev => prev.filter(d => d !== docName))
  }

  return (
    <div className={`p-3 border-t ${isDark ? 'border-gray-800' : 'border-gray-100'}`}>
      <p className={`text-xs font-semibold mb-2 ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
        DOKUMEN
      </p>

      {/* Upload Button */}
      <label className={`flex items-center gap-2 px-3 py-2 rounded-lg cursor-pointer text-sm transition-colors ${
        isDark ? 'hover:bg-gray-800 text-gray-400' : 'hover:bg-gray-50 text-gray-500'
      }`}>
        <Upload size={14} />
        {uploading ? 'Mengupload...' : 'Upload PDF'}
        <input type="file" accept=".pdf" onChange={handleUpload} className="hidden" disabled={uploading} />
      </label>

      {message && (
        <p className="text-xs text-indigo-500 mt-1 px-3">{message}</p>
      )}

      {/* Doc List */}
      {docs.map(doc => (
        <div key={doc} className={`group flex items-center gap-2 px-3 py-2 rounded-lg ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
          <FileText size={13} className="shrink-0 text-indigo-400" />
          <span className="text-xs truncate flex-1">{doc}</span>
          <button
            onClick={() => handleDelete(doc)}
            className="opacity-0 group-hover:opacity-100 hover:text-red-500 transition-all"
          >
            <Trash2 size={12} />
          </button>
        </div>
      ))}
    </div>
  )
}