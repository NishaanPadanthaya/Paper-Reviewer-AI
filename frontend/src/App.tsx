import React, { useState } from 'react'
import axios from 'axios'
import { Search, FileText, Users, Calendar, ExternalLink, Loader2, AlertCircle, Brain, Lightbulb, Target, AlertTriangle } from './icons'

type Paper = {
  title: string
  authors: string[]
  abstract: string
  link: string
  published?: string
  summary: {
    problem: string
    methodology: string
    findings: string
    limitations: string
  }
}

type ApiResponse = {
  topic: string
  model: string
  papers: Paper[]
}

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

export default function App() {
  const [topic, setTopic] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [data, setData] = useState<ApiResponse | null>(null)
  const [expandedAbstracts, setExpandedAbstracts] = useState<Set<number>>(new Set())

  const generate = async () => {
    setLoading(true)
    setError(null)
    setData(null)
    setExpandedAbstracts(new Set())
    try {
      const res = await axios.post(`${API_BASE}/api/summarize`, { topic, top_n: 5 })
      setData(res.data)
    } catch (e: any) {
      setError(e?.response?.data?.detail || e.message)
    } finally {
      setLoading(false)
    }
  }

  const toggleAbstract = (index: number) => {
    const newExpanded = new Set(expandedAbstracts)
    if (newExpanded.has(index)) {
      newExpanded.delete(index)
    } else {
      newExpanded.add(index)
    }
    setExpandedAbstracts(newExpanded)
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && topic && !loading) {
      generate()
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      <div className="max-w-6xl mx-auto px-6 py-8">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="flex items-center justify-center gap-3 mb-4">
            <div className="p-3 bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl">
              <Brain className="w-8 h-8 text-white" />
            </div>
            <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              PaperReviewer AI
            </h1>
          </div>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Discover and analyze research papers with AI-powered summaries. Enter any research topic to get structured insights from arXiv.
          </p>
        </div>

        {/* Search Section */}
        <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-8 mb-8">
          <div className="flex gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                onKeyDown={handleKeyPress}
                placeholder="e.g., diffusion models for image generation, quantum computing, CRISPR gene editing..."
                className="w-full pl-12 pr-4 py-4 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none text-lg transition-all"
                disabled={loading}
              />
            </div>
            <button
              onClick={generate}
              disabled={!topic || loading}
              className="px-8 py-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-xl font-semibold disabled:opacity-50 disabled:cursor-not-allowed hover:shadow-lg transition-all duration-200 flex items-center gap-2"
            >
              {loading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Analyzing...
                </>
              ) : (
                <>
                  <Search className="w-5 h-5" />
                  Generate Summaries
                </>
              )}
            </button>
          </div>
        </div>

        {/* Error State */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-xl p-6 mb-8 flex items-start gap-3">
            <AlertCircle className="w-6 h-6 text-red-500 flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="font-semibold text-red-800 mb-1">Error occurred</h3>
              <p className="text-red-700">{error}</p>
            </div>
          </div>
        )}

        {/* Results */}
        {data && (
          <div className="space-y-6">
            {/* Results Header */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
              <div className="flex items-center gap-3 mb-2">
                <FileText className="w-5 h-5 text-blue-600" />
                <h2 className="text-xl font-semibold text-gray-800">Research Results</h2>
              </div>
              <p className="text-gray-600">
                Found <span className="font-semibold text-blue-600">{data.papers.length}</span> papers on{' '}
                <span className="font-semibold">"{data.topic}"</span>
                <span className="text-sm text-gray-500 ml-2">• Powered by {data.model}</span>
              </p>
            </div>

            {/* Papers Grid */}
            <div className="grid gap-6">
              {data.papers.map((paper, idx) => (
                <div key={idx} className="bg-white rounded-xl shadow-lg border border-gray-100 overflow-hidden hover:shadow-xl transition-shadow duration-300">
                  {/* Paper Header */}
                  <div className="p-6 border-b border-gray-100">
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1">
                        <a
                          href={paper.link}
                          target="_blank"
                          rel="noreferrer"
                          className="text-xl font-semibold text-gray-800 hover:text-blue-600 transition-colors duration-200 flex items-start gap-2 group"
                        >
                          <span className="flex-1">{paper.title}</span>
                          <ExternalLink className="w-5 h-5 text-gray-400 group-hover:text-blue-600 flex-shrink-0 mt-0.5" />
                        </a>
                        <div className="flex items-center gap-4 mt-3 text-sm text-gray-600">
                          <div className="flex items-center gap-1">
                            <Users className="w-4 h-4" />
                            <span>{paper.authors.slice(0, 3).join(', ')}{paper.authors.length > 3 ? ` +${paper.authors.length - 3} more` : ''}</span>
                          </div>
                          {paper.published && (
                            <div className="flex items-center gap-1">
                              <Calendar className="w-4 h-4" />
                              <span>{paper.published}</span>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Paper Content */}
                  <div className="p-6 space-y-6">
                    {/* Abstract */}
                    <div>
                      <button
                        onClick={() => toggleAbstract(idx)}
                        className="flex items-center gap-2 text-lg font-semibold text-gray-800 hover:text-blue-600 transition-colors mb-3"
                      >
                        <FileText className="w-5 h-5" />
                        Abstract
                        <span className="text-sm font-normal text-gray-500">
                          {expandedAbstracts.has(idx) ? '(click to collapse)' : '(click to expand)'}
                        </span>
                      </button>
                      {expandedAbstracts.has(idx) && (
                        <div className="bg-gray-50 rounded-lg p-4 text-gray-700 leading-relaxed">
                          {paper.abstract}
                        </div>
                      )}
                    </div>

                    {/* AI Summary */}
                    <div>
                      <div className="flex items-center gap-2 text-lg font-semibold text-gray-800 mb-4">
                        <Brain className="w-5 h-5 text-purple-600" />
                        AI-Generated Summary
                      </div>
                      <div className="grid md:grid-cols-2 gap-4">
                        <div className="bg-blue-50 rounded-lg p-4">
                          <div className="flex items-center gap-2 mb-2">
                            <Target className="w-4 h-4 text-blue-600" />
                            <h4 className="font-semibold text-blue-800">Problem</h4>
                          </div>
                          <p className="text-blue-700 text-sm leading-relaxed">
                            {paper.summary?.problem || 'Not available'}
                          </p>
                        </div>
                        <div className="bg-green-50 rounded-lg p-4">
                          <div className="flex items-center gap-2 mb-2">
                            <Lightbulb className="w-4 h-4 text-green-600" />
                            <h4 className="font-semibold text-green-800">Methodology</h4>
                          </div>
                          <p className="text-green-700 text-sm leading-relaxed">
                            {paper.summary?.methodology || 'Not available'}
                          </p>
                        </div>
                        <div className="bg-purple-50 rounded-lg p-4">
                          <div className="flex items-center gap-2 mb-2">
                            <Brain className="w-4 h-4 text-purple-600" />
                            <h4 className="font-semibold text-purple-800">Key Findings</h4>
                          </div>
                          <p className="text-purple-700 text-sm leading-relaxed">
                            {paper.summary?.findings || 'Not available'}
                          </p>
                        </div>
                        <div className="bg-orange-50 rounded-lg p-4">
                          <div className="flex items-center gap-2 mb-2">
                            <AlertTriangle className="w-4 h-4 text-orange-600" />
                            <h4 className="font-semibold text-orange-800">Limitations</h4>
                          </div>
                          <p className="text-orange-700 text-sm leading-relaxed">
                            {paper.summary?.limitations || 'Not available'}
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Footer */}
        <footer className="mt-16 text-center text-sm text-gray-500">
          <p>Powered by CrewAI - Gemini-2.5</p>
        </footer>
      </div>

    </div>
  )
}

