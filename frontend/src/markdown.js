function escapeAttr(str) {
  if (!str) return ''
  return str
    .replace(/&/g, '&amp;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
}

function isSafeUrl(url) {
  const lower = (url || '').toLowerCase()
  return !(lower.startsWith('javascript:') ||
           lower.startsWith('data:') ||
           lower.startsWith('vbscript:'))
}

export function renderMarkdown(text) {
  if (!text) return ''
  let html = text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
  // 图片链接过滤：只允许 http/https 协议，并对属性做严格转义
  html = html.replace(/!\[([^\]]*)\]\(([^)]+)\)/g, (match, alt, url) => {
    if (!isSafeUrl(url)) return escapeAttr(alt)
    return `<img src="${escapeAttr(url)}" alt="${escapeAttr(alt)}" class="max-w-full rounded my-2">`
  })
  // 链接过滤：只允许 http/https 协议，防止 javascript: 协议攻击
  html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, (match, text, url) => {
    if (!isSafeUrl(url) || (url || '').toLowerCase().startsWith('file:')) return escapeAttr(text)
    return `<a href="${escapeAttr(url)}" target="_blank" rel="noopener noreferrer" class="text-blue-500 hover:text-blue-700 underline">${escapeAttr(text)}</a>`
  })
  html = html.replace(/\*\*\*(.+?)\*\*\*/g, '<strong><em>$1</em></strong>')
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
  html = html.replace(/~~(.+?)~~/g, '<del>$1</del>')
  html = html.replace(/\*(.+?)\*/g, '<em>$1</em>')
  html = html.replace(/`([^`]+)`/g, '<code class="bg-gray-200 dark:bg-gray-700 px-1 py-0.5 rounded text-sm">$1</code>')
  html = html.replace(/@(\w{2,20})/g, '<span class="text-purple-500 dark:text-purple-400 font-medium">@$1</span>')
  html = html.replace(/\n/g, '<br>')
  return html
}
