<template>
  <div class="tieba-home">
    <!-- 横幅区 -->
    <div class="home-banner">
      <div class="banner-content">
        <h1 class="banner-title">☁️ lsnuts 云端平台</h1>
        <p class="banner-sub">网盘 · 论坛 · 聊天 — 简洁高效的云端社区</p>
      </div>
    </div>

    <!-- 快捷入口 -->
    <div class="quick-nav">
      <div class="quick-item" @click="$router.push('/drive')">
        <span class="quick-icon">💾</span>
        <span class="quick-label">网盘</span>
      </div>
      <div class="quick-item" @click="$router.push('/forum')">
        <span class="quick-icon">📝</span>
        <span class="quick-label">论坛</span>
      </div>
      <div class="quick-item" @click="$router.push('/about')">
        <span class="quick-icon">ℹ️</span>
        <span class="quick-label">关于</span>
      </div>
      <div v-if="!userStore.isLoggedIn" class="quick-item" @click="$router.push('/login')">
        <span class="quick-icon">🔑</span>
        <span class="quick-label">登录</span>
      </div>
      <div v-else class="quick-item" @click="$router.push('/profile')">
        <span class="quick-icon">👤</span>
        <span class="quick-label">个人中心</span>
      </div>
    </div>

    <!-- 最新帖子 -->
    <div class="home-section">
      <div class="section-header">
        <span class="section-title">📋 最新帖子</span>
        <span class="section-more" @click="$router.push('/forum')">查看更多 ›</span>
      </div>
      <div class="recent-posts">
        <div
          v-for="post in recentPosts"
          :key="post.id"
          class="recent-row"
          @click="$router.push(`/forum/detail/${post.id}`)"
        >
          <span class="recent-title">
            <span v-if="post.tag" class="tag-mini" :class="'tag-' + post.tag">{{ tagLabel(post.tag) }}</span>
            {{ post.title }}
          </span>
          <span class="recent-meta">
            <span class="recent-author">{{ post.user }}</span>
            <span class="recent-time">{{ post.create_time }}</span>
          </span>
        </div>
        <div v-if="recentPosts.length === 0" class="recent-empty">
          暂无帖子，去发一个吧！
        </div>
      </div>
    </div>

    <!-- 公告区 -->
    <div v-if="announcements.length > 0" class="home-section">
      <div class="section-header">
        <span class="section-title">📢 公告</span>
      </div>
      <div class="announce-list">
        <div v-for="a in announcements" :key="a.id" class="announce-item">
          <span class="announce-dot">●</span>
          <span class="announce-text">{{ a.content }}</span>
          <span class="announce-time">{{ a.create_time }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useUserStore } from '../stores/user'
import axios from '../axios'

const userStore = useUserStore()
const recentPosts = ref([])
const announcements = ref([])

const tagLabel = (tag) => {
  const map = { tech: '技术', help: '求助', chat: '灌水', other: '其他' }
  return map[tag] || tag
}

const loadRecentPosts = async () => {
  try {
    const res = await axios.get('/api/forum/list', { params: { page: 1, per_page: 8 } })
    recentPosts.value = res.data.data || []
  } catch (e) {
    // ignore
  }
}

const loadAnnouncements = async () => {
  try {
    const res = await axios.get('/api/announcements/public')
    announcements.value = res.data.data || []
  } catch (e) {
    // ignore
  }
}

onMounted(() => {
  loadRecentPosts()
  loadAnnouncements()
})
</script>

<style scoped>
.tieba-home {
  max-width: 900px;
  margin: 0 auto;
}

/* ---- 横幅 ---- */
.home-banner {
  background: linear-gradient(135deg, #4879BD 0%, #3A6299 100%);
  padding: 32px 24px;
  text-align: center;
  border: 1px solid #3A6299;
  margin-bottom: 12px;
}

.banner-title {
  font-size: 24px;
  font-weight: bold;
  color: #fff;
  margin: 0 0 8px 0;
}

.banner-sub {
  font-size: 14px;
  color: rgba(255,255,255,0.8);
  margin: 0;
}

.dark .home-banner {
  background: linear-gradient(135deg, #2c5a8a 0%, #1e3a5f 100%);
  border-color: #2c5a8a;
}

.dark .banner-sub {
  color: rgba(255,255,255,0.7);
}

/* ---- 快捷入口 ---- */
.quick-nav {
  display: flex;
  gap: 0;
  border: 1px solid var(--tieba-border);
  background: var(--tieba-bg-white);
  margin-bottom: 12px;
}

.quick-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 14px 8px;
  cursor: pointer;
  border-right: 1px solid var(--tieba-border);
  transition: none;
}

.quick-item:last-child {
  border-right: none;
}

.quick-item:hover {
  background: #f0f5ff;
}

.quick-icon {
  font-size: 24px;
}

.quick-label {
  font-size: 13px;
  color: var(--tieba-text);
}

.dark .quick-nav {
  background: var(--tieba-bg-white);
  border-color: var(--tieba-border);
}

.dark .quick-item {
  border-right-color: var(--tieba-border);
}

.dark .quick-item:hover {
  background: #2a3a4a;
}

/* ---- 通用板块 ---- */
.home-section {
  border: 1px solid var(--tieba-border);
  background: var(--tieba-bg-white);
  margin-bottom: 12px;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 16px;
  background: #f5f5f5;
  border-bottom: 2px solid var(--tieba-blue);
}

.section-title {
  font-size: 14px;
  font-weight: bold;
  color: var(--tieba-text);
}

.section-more {
  font-size: 12px;
  color: var(--tieba-link);
  cursor: pointer;
}

.section-more:hover {
  text-decoration: underline;
}

.dark .home-section {
  background: var(--tieba-bg-white);
  border-color: var(--tieba-border);
}

.dark .section-header {
  background: #2a2a2a;
}

/* ---- 最新帖子 ---- */
.recent-posts {
  padding: 0;
}

.recent-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 16px;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
  font-size: 13px;
  gap: 12px;
}

.recent-row:last-child {
  border-bottom: none;
}

.recent-row:hover {
  background: #f0f5ff;
}

.recent-title {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: var(--tieba-text);
}

.recent-title:hover {
  color: var(--tieba-blue);
}

.recent-meta {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
  font-size: 12px;
  color: var(--tieba-text-muted);
}

.recent-author {
  color: var(--tieba-link);
}

.recent-empty {
  text-align: center;
  padding: 24px;
  color: var(--tieba-text-muted);
  font-size: 13px;
}

.dark .recent-row {
  border-bottom-color: #333;
}

.dark .recent-row:hover {
  background: #2a3a4a;
}

/* ---- 公告 ---- */
.announce-list {
  padding: 8px 16px;
}

.announce-item {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 6px 0;
  font-size: 13px;
  border-bottom: 1px dashed #eee;
}

.announce-item:last-child {
  border-bottom: none;
}

.announce-dot {
  color: #f97316;
  font-size: 8px;
  margin-top: 5px;
  flex-shrink: 0;
}

.announce-text {
  flex: 1;
  color: var(--tieba-text);
}

.announce-time {
  font-size: 12px;
  color: var(--tieba-text-muted);
  flex-shrink: 0;
}

.dark .announce-item {
  border-bottom-color: #333;
}

/* ---- 标签 ---- */
.tag-mini {
  display: inline-block;
  padding: 0 3px;
  font-size: 10px;
  line-height: 16px;
  border-radius: 2px;
  vertical-align: middle;
  margin-right: 4px;
}

.tag-tech { background: #e0f0ff; color: #2563eb; }
.tag-help { background: #fff3e0; color: #e65100; }
.tag-chat { background: #e8f5e9; color: #2e7d32; }
.tag-other { background: #f3f3f3; color: #666; }

.dark .tag-tech { background: #1e3a5f; color: #60a5fa; }
.dark .tag-help { background: #4a2c00; color: #fb923c; }
.dark .tag-chat { background: #1a3a1a; color: #4ade80; }
.dark .tag-other { background: #333; color: #aaa; }

/* ---- 移动端 ---- */
@media (max-width: 768px) {
  .home-banner {
    padding: 24px 16px;
  }

  .banner-title {
    font-size: 20px;
  }

  .recent-meta {
    display: none;
  }
}
</style>