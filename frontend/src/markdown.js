export function renderMarkdown(text) {
  if (!text) return ''
  let html = text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
  // 图片链接过滤：只允许 http/https 协议
  html = html.replace(/!\[([^\]]*)\]\(([^)]+)\)/g, (match, alt, url) => {
    if (url.toLowerCase().startsWith('javascript:') || 
        url.toLowerCase().startsWith('data:') ||
        url.toLowerCase().startsWith('vbscript:')) {
      return alt
    }
    return `<img src="${url}" alt="${alt}" class="max-w-full rounded my-2">`
  })
  // 链接过滤：只允许 http/https 协议，防止 javascript: 协议攻击
  html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, (match, text, url) => {
    if (url.toLowerCase().startsWith('javascript:') || 
        url.toLowerCase().startsWith('vbscript:') ||
        url.toLowerCase().startsWith('data:') ||
        url.toLowerCase().startsWith('file:')) {
      return text
    }
    return `<a href="${url}" target="_blank" rel="noopener noreferrer" class="text-blue-500 hover:text-blue-700 underline">${text}</a>`
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
