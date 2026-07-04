import { API_BASE, TAG_TYPES, TAG_LABELS } from './constants'

export function formatCount(num) {
  if (num >= 1000) return '999+'
  return num
}

export function tagType(tag) {
  return TAG_TYPES[tag] || 'info'
}

export function tagLabel(tag) {
  return TAG_LABELS[tag] || tag
}

export function getAvatarUrl(avatarPath) {
  if (avatarPath) {
    if (avatarPath.startsWith('http')) return avatarPath
    if (avatarPath.startsWith('/uploads/')) return API_BASE + avatarPath
    return API_BASE + '/uploads/' + avatarPath
  }
  return ''
}
