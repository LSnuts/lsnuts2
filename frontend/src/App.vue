<template>
  <el-container :class="['app-container', { dark: isDark }]" style="min-height: 100vh">
    <!-- 桌面端顶部导航栏 -->
    <el-header class="header desktop-header">
      <div class="logo">☁️ lsnuts 云端平台</div>
      <el-menu mode="horizontal" :default-active="$route.path" class="nav" router>
        <el-menu-item index="/">首页</el-menu-item>
        <el-menu-item index="/drive">网盘</el-menu-item>
        <el-menu-item index="/forum">论坛</el-menu-item>
        <el-menu-item index="/about">关于本站</el-menu-item>
        <template v-if="!store.isLoggedIn">
          <el-menu-item index="/login">登录</el-menu-item>
          <el-menu-item index="/register">注册</el-menu-item>
        </template>
        <template v-else>
          <el-menu-item index="/profile">个人中心</el-menu-item>
          <el-menu-item v-if="store.userInfo.is_admin === 1" index="/admin">管理后台</el-menu-item>
          <el-menu-item @click="handleLogout">退出账户</el-menu-item>
        </template>
      </el-menu>
      <div class="flex items-center gap-2 ml-auto">
        <!-- 通知铃铛 -->
        <el-badge v-if="store.isLoggedIn" :value="store.unreadCount" :hidden="store.unreadCount === 0" class="mr-2">
          <el-button circle size="small" @click="showNotifications"><span class="text-lg">🔔</span></el-button>
        </el-badge>
        <!-- 深色模式切换 -->
        <el-button circle size="small" @click="toggleDark">
          <span class="text-lg">{{ isDark ? '☀️' : '🌙' }}</span>
        </el-button>
      </div>
    </el-header>

    <!-- 移动端顶部导航栏 -->
    <div class="mobile-header">
      <el-button class="menu-btn" @click="drawerVisible = true">☰</el-button>
      <div class="logo">☁️ lsnuts</div>
      <div class="flex items-center gap-1">
        <el-badge v-if="store.isLoggedIn" :value="store.unreadCount" :hidden="store.unreadCount === 0">
          <el-button circle size="small" @click="showNotifications"><span class="text-lg">🔔</span></el-button>
        </el-badge>
        <el-button circle size="small" @click="toggleDark">
          <span class="text-lg">{{ isDark ? '☀️' : '🌙' }}</span>
        </el-button>
      </div>
    </div>

    <!-- 移动端侧滑抽屉导航 -->
    <el-drawer v-model="drawerVisible" direction="ltr" size="220px" :with-header="false">
      <div class="drawer-nav">
        <div class="drawer-logo">☁️ lsnuts 云端平台</div>
        <el-menu :default-active="$route.path" @select="handleDrawerSelect">
          <el-menu-item index="/">🏠 首页</el-menu-item>
          <el-menu-item index="/drive">💾 网盘</el-menu-item>
          <el-menu-item index="/forum">📝 论坛</el-menu-item>
          <el-menu-item index="/about">ℹ️ 关于本站</el-menu-item>
          <template v-if="!store.isLoggedIn">
            <el-menu-item index="/login">🔑 登录</el-menu-item>
            <el-menu-item index="/register">📋 注册</el-menu-item>
          </template>
          <template v-else>
            <el-menu-item index="/profile">👤 个人中心</el-menu-item>
            <el-menu-item v-if="store.userInfo.is_admin === 1" index="/admin">⚙️ 管理后台</el-menu-item>
            <el-menu-item @click="handleLogout">🚪 退出账户</el-menu-item>
          </template>
        </el-menu>
      </div>
    </el-drawer>

    <!-- 通知弹窗 -->
    <el-dialog v-model="notifVisible" title="📬 消息通知" width="90% max-w-[420px]" @open="onNotifOpen">
      <div v-if="store.notifications.length === 0" class="text-center text-gray-400 py-6">暂无通知</div>
      <div v-else class="space-y-3">
        <div v-for="n in store.notifications" :key="n.id" class="p-3 rounded border relative group" :class="n.is_read ? 'bg-gray-50 dark:bg-gray-800 border-gray-200 dark:border-gray-700' : 'bg-blue-50 dark:bg-blue-900/30 border-blue-200 dark:border-blue-800'">
          <div class="text-sm font-medium text-gray-800 dark:text-gray-200">
            {{ n.replier }}
            <span class="text-blue-600 dark:text-blue-400">{{ n.type === 'post_reply' ? '回复了你的帖子' : n.type === 'mention' ? '在评论中@了你' : '回复了你的评论' }}</span>
          </div>
          <div class="text-xs text-gray-500 dark:text-gray-400 mt-1 truncate">{{ n.comment_content }}</div>
          <div class="flex items-center justify-between mt-2">
            <span class="text-xs text-gray-400 dark:text-gray-500">{{ n.post_title }} · {{ n.create_time }}</span>
            <div class="flex gap-1">
              <el-button v-if="!n.post_deleted" size="small" type="primary" @click="goToPost(n)">去看看 →</el-button>
              <el-button v-else size="small" disabled>帖子已删除</el-button>
              <el-button size="small" type="danger" text @click="deleteNotif(n.id)">🗑</el-button>
            </div>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button v-if="store.notifications.length > 0" size="small" @click="markAllRead">全部标为已读</el-button>
        <el-button size="small" @click="notifVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 主内容区域 -->
    <el-main class="main">
      <router-view @login="handleLogin" @avatar-change="store.fetchUserInfo" />
    </el-main>
  </el-container>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from './stores/user'

const store = useUserStore()
const router = useRouter()
const isDark = ref(localStorage.getItem('lsnuts_dark') === '1')
const drawerVisible = ref(false)
const notifVisible = ref(false)

const toggleDark = () => {
  isDark.value = !isDark.value
  localStorage.setItem('lsnuts_dark', isDark.value ? '1' : '0')
  document.documentElement.classList.toggle('dark', isDark.value)
}

const handleLogout = async () => {
  await store.logout()
  drawerVisible.value = false
  router.push('/login')
}

const handleDrawerSelect = (index) => {
  drawerVisible.value = false
  router.push(index)
}

const handleLogin = () => { store.fetchUserInfo() }

const showNotifications = () => {
  store.fetchNotifications()
  notifVisible.value = true
}

const onNotifOpen = () => {
  store.fetchNotifications()
  store.unreadCount = 0
}

const markAllRead = async () => {
  await store.markAllRead()
  notifVisible.value = false
}

const goToPost = (n) => {
  if (n.post_deleted) return
  markAllRead()
  notifVisible.value = false
  const anchor = n.comment_id ? `#comment-${n.comment_id}` : ''
  router.push(`/forum/detail/${n.post_id}${anchor}`)
}

const deleteNotif = async (id) => {
  try {
    await store.deleteNotification(id)
    ElMessage.success('已删除')
  } catch (e) {
    ElMessage.error('删除失败')
  }
}

watch(() => store.isLoggedIn, (val) => { if (val) store.fetchUnreadCount() })

onMounted(() => {
  document.documentElement.classList.toggle('dark', isDark.value)
  store.fetchUserInfo()
  store.fetchUnreadCount()
  setInterval(() => store.fetchUnreadCount(), 30000)
})
</script>

<style>
/* 桌面端导航栏 - 默认显示 */
.desktop-header {
  display: flex;
  align-items: center;
  background: var(--bg-card);
  border-bottom: 1px solid var(--border-color);
  padding: 0 20px;
}
.desktop-header .logo { font-size: 20px; font-weight: bold; color: #409eff; margin-right: 30px; white-space: nowrap; }
.desktop-header :deep(.el-menu) { flex: 1; border: none; background: transparent; }

/* 移动端导航栏 - 默认隐藏 */
.mobile-header {
  display: none;
  justify-content: space-between;
  align-items: center;
  background: var(--bg-card);
  padding: 0 10px;
  height: 50px;
  border-bottom: 1px solid var(--border-color);
}
.mobile-header .logo { font-size: 18px; font-weight: bold; color: #409eff; }
.menu-btn { border: none; background: transparent; font-size: 24px; color: var(--text-primary); }

.main { background: var(--bg-main); min-height: calc(100vh - 60px); padding: 0; }

.drawer-nav { padding-top: 20px; }
.drawer-logo { font-size: 18px; font-weight: bold; color: #409eff; text-align: center; margin-bottom: 16px; }

/* 响应式：移动端显示移动端导航，隐藏桌面端导航 */
@media (max-width: 768px) {
  :deep(.header.desktop-header) {
    display: none;
  }
  .mobile-header {
    display: flex;
  }
  .main { min-height: calc(100vh - 50px); }
}

.el-table { font-size: 12px; }
@media (max-width: 768px) { .el-table { font-size: 11px; } .el-card { border-radius: 0; } }

/* 全局返回按钮 */
.back-btn-sm {
  border-radius: 6px; border: 1px solid #d1d5db; background: #f9fafb;
  color: #6b7280; font-size: 13px; padding: 4px 14px;
}
.back-btn-sm:hover { border-color: #409eff; color: #409eff; background: #eff6ff; }
.dark .back-btn-sm { background: #1f2937; border-color: #4b5563; color: #d1d5db; }
.dark .back-btn-sm:hover { border-color: #60a5fa; color: #60a5fa; background: #1e3a5f; }

.back-btn {
  margin-bottom: 12px; width: 100%; justify-content: flex-start;
  border-radius: 8px; border: 1px solid #d1d5db; background: #f9fafb;
  color: #6b7280; font-size: 14px; padding: 8px 16px;
}
.back-btn:hover { border-color: #409eff; color: #409eff; background: #eff6ff; }
.dark .back-btn { background: #1f2937; border-color: #4b5563; color: #d1d5db; }
.dark .back-btn:hover { border-color: #60a5fa; color: #60a5fa; background: #1e3a5f; }
</style>
