import React, { useState } from 'react';
import { Header } from '../components/Header';
import { api } from '../services/api';
import { Database, Upload, Search, BookOpen, Layers, CheckCircle2, Loader2, FileText } from 'lucide-react';

export const KnowledgeBaseRAGPage = () => {
  // Ingestion Form State
  const [title, setTitle] = useState('');
  const [fileType, setFileType] = useState('PDF');
  const [author, setAuthor] = useState('Logistics Operations');
  const [content, setContent] = useState('');
  const [uploading, setUploading] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState(null);

  // Vector Query State
  const [query, setQuery] = useState('');
  const [topK, setTopK] = useState(3);
  const [searching, setSearching] = useState(false);
  const [queryResults, setQueryResults] = useState([]);

  const handleUploadDocument = async (e) => {
    e.preventDefault();
    if (!title.trim() || !content.trim()) return;
    setUploading(true);
    setUploadSuccess(null);
    try {
      const res = await api.post('/ai/rag/upload', {
        title,
        file_type: fileType,
        author,
        content
      });
      setUploadSuccess(res.data);
      setTitle('');
      setContent('');
    } catch (err) {
      alert(err.message || 'Document ingestion failed');
    } finally {
      setUploading(false);
    }
  };

  const handleVectorSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;
    setSearching(true);
    try {
      const res = await api.post('/ai/rag/query', {
        query,
        top_k: parseInt(topK)
      });
      setQueryResults(res.data || []);
    } catch (err) {
      alert(err.message || 'Vector search query failed');
    } finally {
      setSearching(false);
    }
  };

  return (
    <div className="flex-1 pb-12">
      <Header
        title="Enterprise RAG Knowledge Base Console"
        subtitle="Ingest logistics manuals & SOPs, generate dense vector embeddings, and execute cosine similarity search"
      />

      <div className="p-8 max-w-7xl mx-auto space-y-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Document Ingestion & Chunking Panel */}
          <div className="glass-card rounded-2xl p-6 border border-slate-800 space-y-5">
            <h4 className="text-base font-bold text-slate-100 font-heading flex items-center space-x-2">
              <Upload className="w-5 h-5 text-indigo-400" />
              <span>Document Chunking & Ingestion</span>
            </h4>
            <p className="text-xs text-slate-400">
              Upload logistics operational policies, Cold Chain manuals, or delivery guidelines to auto-chunk (300 words) and vectorize into PostgreSQL.
            </p>

            {uploadSuccess && (
              <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs flex items-center space-x-2">
                <CheckCircle2 className="w-4 h-4 flex-shrink-0" />
                <span>Successfully indexed "{uploadSuccess.title}" into {uploadSuccess.chunk_count} vector chunks.</span>
              </div>
            )}

            <form onSubmit={handleUploadDocument} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Document Title *</label>
                <input
                  type="text"
                  required
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="Cold Chain Bio-Pharm SOP Manual"
                  className="w-full bg-slate-900/60 border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-slate-100 focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Format Type</label>
                  <select
                    value={fileType}
                    onChange={(e) => setFileType(e.target.value)}
                    className="w-full bg-slate-900/60 border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-slate-100 focus:outline-none focus:border-indigo-500"
                  >
                    <option value="PDF">PDF Manual</option>
                    <option value="TXT">TXT Plaintext</option>
                    <option value="MD">Markdown SOP</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Author Department</label>
                  <input
                    type="text"
                    value={author}
                    onChange={(e) => setAuthor(e.target.value)}
                    className="w-full bg-slate-900/60 border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-slate-100 focus:outline-none focus:border-indigo-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Full Document Text Content *</label>
                <textarea
                  required
                  rows={6}
                  value={content}
                  onChange={(e) => setContent(e.target.value)}
                  placeholder="Paste complete document text content here to ingest into vector storage..."
                  className="w-full bg-slate-900/60 border border-slate-800 rounded-xl p-3 text-xs text-slate-100 focus:outline-none focus:border-indigo-500 font-mono"
                />
              </div>

              <button
                type="submit"
                disabled={uploading || !title.trim() || !content.trim()}
                className="w-full py-3 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-bold text-xs shadow-lg shadow-indigo-600/30 flex items-center justify-center space-x-2 disabled:opacity-50"
              >
                {uploading ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Chunking Text & Vectorizing Embeddings...</span>
                  </>
                ) : (
                  <>
                    <Layers className="w-4 h-4" />
                    <span>Ingest into RAG Vector Base</span>
                  </>
                )}
              </button>
            </form>
          </div>

          {/* Semantic Vector Cosine Similarity Query Tester */}
          <div className="glass-card rounded-2xl p-6 border border-slate-800 space-y-5">
            <h4 className="text-base font-bold text-slate-100 font-heading flex items-center space-x-2">
              <Search className="w-5 h-5 text-cyan-400" />
              <span>Semantic Vector Search Tester</span>
            </h4>
            <p className="text-xs text-slate-400">
              Query indexed knowledge chunks using dense vector cosine similarity matching ($D=384$).
            </p>

            <form onSubmit={handleVectorSearch} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Natural Language Query *</label>
                <div className="relative">
                  <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-500" />
                  <input
                    type="text"
                    required
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="e.g. What is the required temperature for bio-pharmaceuticals?"
                    className="w-full bg-slate-900/60 border border-slate-800 rounded-xl pl-10 pr-4 py-2.5 text-sm text-slate-100 focus:outline-none focus:border-cyan-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Top-K Passages to Retrieve ({topK})</label>
                <input
                  type="range"
                  min={1}
                  max={5}
                  value={topK}
                  onChange={(e) => setTopK(e.target.value)}
                  className="w-full accent-cyan-500"
                />
              </div>

              <button
                type="submit"
                disabled={searching || !query.trim()}
                className="w-full py-3 rounded-xl bg-gradient-to-r from-cyan-600 to-blue-600 text-white font-bold text-xs shadow-lg shadow-cyan-600/30 flex items-center justify-center space-x-2 disabled:opacity-50"
              >
                {searching ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Searching Dense Embedding Space...</span>
                  </>
                ) : (
                  <>
                    <Database className="w-4 h-4" />
                    <span>Run Cosine Similarity Query</span>
                  </>
                )}
              </button>
            </form>

            {/* Results Feed */}
            <div className="pt-4 border-t border-slate-800 space-y-3">
              <h5 className="text-xs font-bold text-slate-300 uppercase tracking-wider">Retrieved Passages</h5>
              {queryResults.length === 0 ? (
                <p className="text-xs text-slate-500 text-center py-6">No vector search results yet.</p>
              ) : (
                queryResults.map((res, idx) => (
                  <div key={idx} className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-cyan-400 flex items-center">
                        <FileText className="w-3.5 h-3.5 mr-1" />
                        {res.document_title} (Chunk #{res.chunk_index})
                      </span>
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-300 border border-cyan-500/20 font-bold">
                        Score: {res.similarity_score.toFixed(4)}
                      </span>
                    </div>
                    <p className="text-xs text-slate-300 italic">{res.content}</p>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
