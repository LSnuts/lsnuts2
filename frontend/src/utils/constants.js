export const API_BASE = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:5000'

export const DEFAULT_AVATAR_SVG = 'data:image/svg+xml,' + encodeURIComponent('<svg xmlns="http://www.w3.org/2000/svg" width="256" height="256" viewBox="0 0 256 256"><rect fill="#9CA3AF" width="256" height="256" rx="16"/><text fill="white" font-family="sans-serif" font-size="120" font-weight="bold" x="50%" y="55%" dominant-baseline="middle" text-anchor="middle">U</text></svg>')

export const TAG_TYPES = { tech: '', help: 'warning', chat: 'success' }
export const TAG_LABELS = { tech: '技术分享', help: '提问求助', chat: '闲聊灌水' }
