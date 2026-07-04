<template>
  <el-container :class="['app-container', { dark: isDark }]" style="min-height: 100vh">
    <!-- ========== 桌面端顶部导航栏 ========== -->
    <el-header class="tieba-header desktop-header" ref="desktopHeaderRef">
      <div class="header-inner">
        <div class="logo" @click="$router.push('/')">
          <span class="logo-icon">☁️</span>
          <span class="logo-text">lsnuts 云端平台</span>
        </div>
        <el-menu
          :key="menuKey"
          mode="horizontal"
          :default-active="$route.path"
          class="tieba-nav"
          router
          :ellipsis="false"
        >
          <el-menu-item index="/">首页</el-menu-item>
          <el-menu-item index="/drive">网盘</el-menu-item>
          <el-menu-item index="/forum">论坛</el-menu-item>
          <el-menu-item index="/chat">聊天</el-menu-item>
          <el-menu-item index="/about">关于</el-menu-item>
          <template v-if="!userStore.isLoggedIn">
            <el-menu-item index="/login">登录</el-menu-item>
            <el-menu-item index="/register">注册</el-menu-item>
          </template>
          <template v-else>
            <el-menu-item index="/profile">个人中心</el-menu-item>
            <el-menu-item v-if="userStore.userInfo.is_admin === 1" index="/admin">管理</el-menu-item>
            <el-menu-item @click="handleLogout">退出</el-menu-item>
          </template>
        </el-menu>
        <div class="header-actions">
          <el-badge
            v-if="userStore.isLoggedIn"
            :value="notifStore.unreadCount"
            :hidden="notifStore.unreadCount === 0"
            class="notif-badge"
          >
            <el-button circle size="small" @click="showNotifications">
              <span class="text-base">🔔</span>
            </el-button>
          </el-badge>
          <el-button circle size="small" @click="toggleDark">
            <span class="text-base">{{ isDark ? '☀️' : '🌙' }}</span>
          </el-button>
        </div>
      </div>
    </el-header>

    <!-- ========== 移动端菜单按钮 ========== -->
    <div class="mobile-menu-btn" @click="drawerVisible = true">
      ☰
    </div>

    <!-- 移动端侧滑抽屉 -->
    <el-drawer v-model="drawerVisible" direction="ltr" size="220px" :with-header="false">
      <div class="drawer-nav">
        <div class="drawer-logo">☁️ lsnuts 云端平台</div>
        <el-menu :default-active="$route.path" @select="handleDrawerSelect">
          <el-menu-item index="/">🏠 首页</el-menu-item>
          <el-menu-item index="/drive">💾 网盘</el-menu-item>
          <el-menu-item index="/forum">📝 论坛</el-menu-item>
          <el-menu-item index="/chat">💬 聊天</el-menu-item>
          <el-menu-item index="/about">ℹ️ 关于</el-menu-item>
          <template v-if="!userStore.isLoggedIn">
            <el-menu-item index="/login">🔑 登录</el-menu-item>
            <el-menu-item index="/register">📋 注册</el-menu-item>
          </template>
          <template v-else>
            <el-menu-item index="/profile">👤 个人中心</el-menu-item>
            <el-menu-item v-if="userStore.userInfo.is_admin === 1" index="/admin">⚙️ 管理</el-menu-item>
            <el-menu-item @click="handleLogout">🚪 退出</el-menu-item>
          </template>
        </el-menu>
      </div>
    </el-drawer>

    <!-- 通知弹窗 -->
    <el-dialog v-model="notifVisible" title="📬 消息通知" width="90% max-w-[460px]" @open="onNotifOpen">
      <div v-if="notifStore.notifications.length === 0" class="text-center text-gray-400 py-6">
        暂无通知
      </div>
      <div v-else class="notif-list">
        <div
          v-for="n in notifStore.notifications"
          :key="n.id"
          class="notif-item"
          :class="{ 'unread': n.is_read === 0 }"
        >
          <div class="notif-avatar">
            <el-avatar :size="36" :src="n.avatar ? `https://api.118201820.xyz/uploads/${n.avatar}` : ''" :icon="!n.avatar ? 'User' : null">
              {{ n.username?.charAt(0) }}
            </el-avatar>
          </div>
          <div class="notif-content">
            <div class="notif-header">
              <span class="notif-user">{{ n.username }}</span>
              <span class="notif-time">{{ n.create_time }}</span>
            </div>
            <div class="notif-action">
              <span v-if="n.type === 'chat_message'" class="action-chat">发来了消息</span>
              <span v-else-if="n.type === 'post_reply'" class="action-reply">回复了你的帖子</span>
              <span v-else-if="n.type === 'mention'" class="action-mention">在评论中@了你</span>
              <span v-else class="action-comment">回复了你的评论</span>
            </div>
            <div class="notif-preview">
              <span v-if="n.type === 'chat_message'" class="preview-text">{{ n.message_content }}</span>
              <template v-else>
                <span class="preview-title">{{ n.post_title }}</span>
                <span v-if="n.comment_content" class="preview-dot">·</span>
                <span v-if="n.comment_content" class="preview-text">{{ n.comment_content }}</span>
              </template>
            </div>
          </div>
          <div class="notif-actions">
            <el-button 
              v-if="n.type === 'chat_message'" 
              size="small" 
              type="primary" 
              @click="goToChat(n)"
            >
              去聊天
            </el-button>
            <el-button 
              v-else-if="!n.post_deleted" 
              size="small" 
              type="primary" 
              @click="goToPost(n)"
            >
              去看看
            </el-button>
            <el-button v-else size="small" disabled>帖子已删</el-button>
            <el-button size="small" type="danger" text @click="deleteNotif(n.id)">🗑</el-button>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button v-if="notifStore.notifications.length > 0" size="small" @click="markAllRead">
          全部标为已读
        </el-button>
        <el-button size="small" @click="notifVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- ========== 主内容区 ========== -->
    <el-main class="tieba-main">
      <div class="tieba-content-wrapper">
        <router-view @login="handleLogin" @avatar-change="userStore.fetchUserInfo" />
      </div>
    </el-main>

    <!-- ========== 底部 ========== -->
    <footer class="tieba-footer">
      <span>© 2026 lsnuts 云端平台</span>
    </footer>
  </el-container>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from './stores/user'
import { useNotificationStore } from './stores/notification'

const userStore = useUserStore()
const notifStore = useNotificationStore()
const router = useRouter()
const isDark = ref(localStorage.getItem('lsnuts_dark') === '1')
const drawerVisible = ref(false)
const notifVisible = ref(false)
const isMobile = ref(false)
const menuKey = ref(0)

const checkMobile = () => {
  isMobile.value = window.innerWidth < 768
}

const toggleDark = () => {
  isDark.value = !isDark.value
  localStorage.setItem('lsnuts_dark', isDark.value ? '1' : '0')
  document.documentElement.classList.toggle('dark', isDark.value)
}

const handleLogout = async () => {
  await userStore.logout()
  notifStore.reset()
  drawerVisible.value = false
  router.push('/')
}

const handleDrawerSelect = (index) => {
  drawerVisible.value = false
  router.push(index)
}

const handleLogin = () => {
  userStore.fetchUserInfo()
  notifStore.fetchUnreadCount()
}

const showNotifications = () => {
  notifStore.fetchNotifications()
  notifVisible.value = true
}

const onNotifOpen = () => {
  notifStore.fetchNotifications()
  notifStore.markAllRead()
}

const markAllRead = async () => {
  await notifStore.markAllRead()
  notifVisible.value = false
}

const goToPost = (n) => {
  if (n.post_deleted) return
  markAllRead()
  notifVisible.value = false
  const anchor = n.comment_id ? `#comment-${n.comment_id}` : ''
  router.push(`/forum/detail/${n.post_id}${anchor}`)
}

const goToChat = (n) => {
  markAllRead()
  notifVisible.value = false
  router.push('/chat')
}

const deleteNotif = async (id) => {
  try {
    await notifStore.deleteNotification(id)
    ElMessage.success('已删除')
  } catch (e) {
    ElMessage.error('删除失败')
  }
}

watch(() => userStore.isLoggedIn, (val) => {
  if (val) notifStore.fetchUnreadCount()
})

onMounted(() => {
  checkMobile()
  window.addEventListener('resize', checkMobile)
  document.documentElement.classList.toggle('dark', isDark.value)
  userStore.fetchUserInfo()
  notifStore.fetchUnreadCount()
  setInterval(() => notifStore.fetchUnreadCount(), 30000)
})

onUnmounted(() => {
  window.removeEventListener('resize', checkMobile)
})
</script>

<style>
/* ============================================
   导航栏 - 贴吧蓝色
   ============================================ */
.tieba-header.desktop-header {
  display: flex !important;
  align-items: center;
  background: #4879BD;
  border-bottom: none !important;
  padding: 0;
  height: 44px !important;
  box-shadow: 0 1px 3px rgba(0,0,0,0.15);
}

.header-inner {
  display: flex;
  align-items: center;
  width: 100%;
  max-width: 1100px;
  margin: 0 auto;
  padding: 0 16px;
  height: 100%;
}

.tieba-header .logo {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  margin-right: 24px;
  white-space: nowrap;
  flex-shrink: 0;
}

.tieba-header .logo-icon {
  font-size: 18px;
}

.tieba-header .logo-text {
  font-size: 16px;
  font-weight: bold;
  color: #fff;
  letter-spacing: 1px;
}

/* 导航菜单 */
.tieba-nav {
  flex: 1;
  border: none !important;
  background: transparent !important;
  height: 44px !important;
}

.tieba-nav .el-menu-item {
  color: rgba(255,255,255,0.85) !important;
  font-size: 13px !important;
  height: 44px !important;
  line-height: 44px !important;
  padding: 0 14px !important;
  border-bottom: none !important;
  background: transparent !important;
}

.tieba-nav .el-menu-item:hover,
.tieba-nav .el-menu-item.is-active {
  color: #fff !important;
  background: rgba(255,255,255,0.15) !important;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-left: auto;
  flex-shrink: 0;
}

.header-actions .el-button {
  border-color: rgba(255,255,255,0.3) !important;
  background: transparent !important;
  color: #fff !important;
}

.header-actions .el-button:hover {
  background: rgba(255,255,255,0.15) !important;
}

.notif-badge .el-badge__content {
  font-size: 10px;
}

/* ============================================
   移动端菜单按钮
   ============================================ */
.mobile-menu-btn {
  display: none;
  position: fixed;
  top: 8px;
  left: 8px;
  width: 40px;
  height: 40px;
  background: rgba(72, 121, 189, 0.95);
  color: #fff;
  font-size: 22px;
  text-align: center;
  line-height: 40px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.2);
  z-index: 1000;
  cursor: pointer;
}

.mobile-menu-btn:hover {
  background: rgba(72, 121, 189, 1);
}

/* ============================================
   主内容区
   ============================================ */
.tieba-main {
  background: var(--tieba-bg);
  min-height: calc(100vh - 44px - 40px);
  padding: 0;
}

.tieba-content-wrapper {
  max-width: 1100px;
  margin: 0 auto;
  padding: 12px 16px;
}

/* ============================================
   底部
   ============================================ */
.tieba-footer {
  text-align: center;
  padding: 10px 0;
  font-size: 12px;
  color: #999;
  background: #f7f7f7;
  border-top: 1px solid var(--tieba-border);
}

.dark .tieba-footer {
  background: #1a1a1a;
  border-top-color: #333;
  color: #666;
}

/* ============================================
   抽屉导航
   ============================================ */
.drawer-nav {
  padding-top: 16px;
}

.drawer-logo {
  font-size: 16px;
  font-weight: bold;
  color: var(--tieba-blue);
  text-align: center;
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--tieba-border);
}

/* ============================================
   响应式
   ============================================ */
@media (max-width: 768px) {
  .desktop-header,
  .tieba-header.desktop-header,
  .app-container > .el-header.desktop-header {
    display: none !important;
    visibility: hidden !important;
    height: 0 !important;
    padding: 0 !important;
    border: none !important;
    overflow: hidden !important;
  }
  .mobile-menu-btn {
    display: block !important;
  }
  .tieba-main {
    min-height: calc(100vh - 36px);
  }
  .tieba-content-wrapper {
    padding: 8px;
  }
}

@media (min-width: 769px) {
  .mobile-menu-btn {
    display: none !important;
  }
}

/* ============================================
   Element Plus 深色模式覆盖
   ============================================ */
.dark .tieba-header.desktop-header {
  background: #2c5a8a;
}

.dark .mobile-menu-btn {
  background: rgba(44, 90, 138, 0.95);
}

.dark .tieba-main {
  background: #1a1a1a;
}

.dark .el-card {
  background: #222 !important;
  border-color: #444 !important;
}

.dark .el-card__header {
  background: #2a2a2a !important;
  border-bottom-color: #4879BD !important;
}

/* 通用工具类 */
.back-btn-sm {
  border-radius: 2px;
  border: 1px solid #d1d5db;
  background: #f9fafb;
  color: #6b7280;
  font-size: 13px;
  padding: 4px 14px;
}

.back-btn-sm:hover {
  border-color: var(--tieba-blue);
  color: var(--tieba-blue);
  background: #eff6ff;
}

.dark .back-btn-sm {
  background: #1f2937;
  border-color: #4b5563;
  color: #d1d5db;
}

.dark .back-btn-sm:hover {
  border-color: var(--tieba-blue);
  color: var(--tieba-blue-light);
}

.el-table { font-size: 12px; }
@media (max-width: 768px) { .el-table { font-size: 11px; } }

/* ============================================
   通知弹窗样式
   ============================================ */
.notif-list {
  max-height: 480px;
  overflow-y: auto;
  padding-right: 4px;
}

.notif-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 14px;
  margin-bottom: 10px;
  border-radius: 8px;
  background: #fafafa;
  border: 1px solid #eee;
  transition: all 0.2s;
}

.dark .notif-item {
  background: #2a2a2a;
  border-color: #444;
}

.notif-item.unread {
  background: #eff6ff;
  border-color: #bfdbfe;
}

.dark .notif-item.unread {
  background: #1e3a5f;
  border-color: #2c5a8a;
}

.notif-item:last-child {
  margin-bottom: 0;
}

.notif-avatar {
  flex-shrink: 0;
}

.notif-content {
  flex: 1;
  min-width: 0;
}

.notif-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 4px;
}

.notif-user {
  font-size: 14px;
  font-weight: 500;
  color: #333;
}

.dark .notif-user {
  color: #fff;
}

.notif-time {
  font-size: 12px;
  color: #999;
  flex-shrink: 0;
}

.dark .notif-time {
  color: #666;
}

.notif-action {
  margin-bottom: 6px;
}

.action-chat {
  font-size: 13px;
  color: #2563eb;
}

.action-reply {
  font-size: 13px;
  color: #16a34a;
}

.action-mention {
  font-size: 13px;
  color: #f59e0b;
}

.action-comment {
  font-size: 13px;
  color: #8b5cf6;
}

.notif-preview {
  display: flex;
  align-items: center;
  gap: 4px;
  flex-wrap: wrap;
}

.preview-title {
  font-size: 12px;
  color: #666;
  font-weight: 500;
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.dark .preview-title {
  color: #aaa;
}

.preview-dot {
  font-size: 12px;
  color: #999;
}

.preview-text {
  font-size: 12px;
  color: #999;
  max-width: 220px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.dark .preview-text {
  color: #666;
}

.notif-actions {
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex-shrink: 0;
}

.notif-actions .el-button {
  padding: 3px 8px;
  font-size: 11px;
}
</style>