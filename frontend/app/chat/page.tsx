"use client"

import { useState, useRef, useEffect } from "react"
import { Send, User, Bot, Sparkles } from "lucide-react"
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

interface Message {
    role: "user" | "assistant"
    content: string
}

const SUGGESTED_PROMPTS = [
    "Summarize the key concepts",
    "Create a study schedule for next week",
    "What are the main deadlines?",
    "Generate 5 flashcards from this",
]

export default function Chat() {
    const [messages, setMessages] = useState<Message[]>([])
    const [input, setInput] = useState("")
    const [loading, setLoading] = useState(false)
    const messagesEndRef = useRef<HTMLDivElement>(null)

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
    }

    useEffect(() => {
        // Fetch history on mount
        fetch("http://localhost:8000/api/chat/history")
            .then(res => res.json())
            .then(data => {
                if (Array.isArray(data)) {
                    setMessages(data)
                }
            })
            .catch(err => console.error("Failed to fetch chat history", err))
    }, [])

    useEffect(() => {
        scrollToBottom()
    }, [messages])

    const handleSend = async (text: string) => {
        if (!text.trim() || loading) return

        setMessages(prev => [...prev, { role: "user", content: text }])
        setInput("")
        setLoading(true)

        try {
            const response = await fetch("http://localhost:8000/api/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: text, history: messages }),
            })

            if (!response.ok) {
                throw new Error("Failed to send message")
            }

            const data = await response.json()
            setMessages(prev => [...prev, { role: "assistant", content: data.response }])
        } catch (err) {
            console.error(err)
            setMessages(prev => [...prev, { role: "assistant", content: "Sorry, I encountered an error. Please try again." }])
        } finally {
            setLoading(false)
        }
    }

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault()
        handleSend(input)
    }

    return (
        <div className="flex flex-col h-[calc(100vh-8rem)] max-w-4xl mx-auto">
            <div className="flex-1 overflow-y-auto p-4 space-y-6 scrollbar-hide">
                {messages.length === 0 ? (
                    <div className="flex flex-col items-center justify-center h-full text-center space-y-8">
                        <div className="p-4 bg-primary/5 rounded-full">
                            <Sparkles className="h-12 w-12 text-primary" />
                        </div>
                        <div className="space-y-2">
                            <h2 className="text-2xl font-semibold">How can I help you study?</h2>
                            <p className="text-muted-foreground">Ask questions about your uploaded documents.</p>
                        </div>

                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 w-full max-w-2xl">
                            {SUGGESTED_PROMPTS.map((prompt, i) => (
                                <button
                                    key={i}
                                    onClick={() => handleSend(prompt)}
                                    className="p-4 text-left border rounded-xl hover:bg-muted/50 hover:border-primary/50 transition-all text-sm font-medium"
                                >
                                    {prompt}
                                </button>
                            ))}
                        </div>
                    </div>
                ) : (
                    messages.map((msg, i) => (
                        <div
                            key={i}
                            className={`flex items-start gap-4 ${msg.role === "user" ? "flex-row-reverse" : ""
                                }`}
                        >
                            <div
                                className={`p-2 rounded-full shrink-0 border ${msg.role === "user" ? "bg-primary text-primary-foreground" : "bg-background"
                                    }`}
                            >
                                {msg.role === "user" ? <User className="h-5 w-5" /> : <Bot className="h-5 w-5" />}
                            </div>
                            <div
                                className={`p-4 rounded-2xl max-w-[80%] leading-relaxed ${msg.role === "user"
                                    ? "bg-primary text-primary-foreground rounded-tr-none"
                                    : "bg-muted rounded-tl-none"
                                    }`}
                            >
                                {msg.role === "user" ? (
                                    <p className="whitespace-pre-wrap text-sm">{msg.content}</p>
                                ) : (
                                    <div className="prose dark:prose-invert prose-sm max-w-none">
                                        <ReactMarkdown remarkPlugins={[remarkGfm]}>
                                            {msg.content}
                                        </ReactMarkdown>
                                    </div>
                                )}
                            </div>
                        </div>
                    ))
                )}

                {loading && (
                    <div className="flex items-start gap-4">
                        <div className="p-2 rounded-full shrink-0 border bg-background">
                            <Bot className="h-5 w-5" />
                        </div>
                        <div className="p-4 rounded-2xl rounded-tl-none bg-muted">
                            <div className="flex gap-1">
                                <span className="w-2 h-2 bg-foreground/50 rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
                                <span className="w-2 h-2 bg-foreground/50 rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
                                <span className="w-2 h-2 bg-foreground/50 rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
                            </div>
                        </div>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            <div className="p-4 border-t bg-background">
                <form onSubmit={handleSubmit} className="flex gap-2 relative">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder="Ask a question..."
                        className="flex-1 pl-4 pr-12 py-3 rounded-xl border bg-background focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all shadow-sm"
                        disabled={loading}
                    />
                    <button
                        type="submit"
                        disabled={!input.trim() || loading}
                        className="absolute right-2 top-2 p-1.5 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 disabled:opacity-50 transition-colors"
                    >
                        <Send className="h-5 w-5" />
                    </button>
                </form>
            </div>
        </div>
    )
}
