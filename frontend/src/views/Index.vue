<template>
  <!-- 首页：展示平台介绍和功能入口 -->
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900">
    <!-- 顶部欢迎区域 -->
    <div class="hero text-center px-4 py-10 md:py-16">
      <div class="max-w-3xl mx-auto">
        
        <h1 class="text-2xl md:text-5xl text-white font-bold mb-3">
          ☁️欢迎光临lsnuts
        </h1>
        <div class="text-white/70 text-sm md:text-base mb-4">{{ currentDate }}</div>
        <p class="text-base md:text-xl text-white/80 mb-8">
          今天，也是充满希望的一天
        </p>
        <div class="flex gap-4 justify-center flex-wrap">
          <!-- 未登录显示注册和登录按钮 -->
          <template v-if="!isLoggedIn">
            <el-button type="primary" size="large" @click="$router.push('/register')" class="!px-8 !py-3 !text-base !rounded-lg">
              立即注册
            </el-button>
            <el-button size="large" @click="$router.push('/login')" class="!px-8 !py-3 !text-base !rounded-lg !bg-white/15 !border-white !text-white hover:!bg-white/25">
              登录账号
            </el-button>
          </template>
          <template v-else>
            <el-button type="primary" size="large" @click="$router.push('/drive')" class="!px-8 !py-3 !text-base !rounded-lg">
              开始使用
            </el-button>
          </template>
        </div>
      </div>
    </div>
    <!-- 功能卡片展示区 -->
    <div class="max-w-5xl mx-auto px-4 -mt-6 pb-10">
      <el-row :gutter="20">
        <el-col :span="24" :md="8" class="mb-5">
          <div class="feature-card dark:!bg-gray-800 dark:!shadow-black/30" @click="$router.push('/drive')">
            <div class="feature-icon bg-blue-100 text-blue-600">
              <span class="text-4xl">💾</span>
            </div>
            <h3 class="text-lg font-bold text-gray-800 dark:text-gray-200 mb-2">安全网盘</h3>
            <p class="text-sm text-gray-500 dark:text-gray-400 leading-relaxed">
              文件加密存储，支持上传下载管理，数据安全可控，随时随地访问您的文件
            </p>
          </div>
        </el-col>
        <el-col :span="24" :md="8" class="mb-5">
          <div class="feature-card dark:!bg-gray-800 dark:!shadow-black/30" @click="$router.push('/forum')">
            <div class="feature-icon bg-green-100 text-green-600">
              <span class="text-4xl">📝</span>
            </div>
            <h3 class="text-lg font-bold text-gray-800 dark:text-gray-200 mb-2">轻量论坛</h3>
            <p class="text-sm text-gray-500 dark:text-gray-400 leading-relaxed">
              技术分享、问题求助、新鲜事，支持图片附件上传，一站式交流社区
            </p>
          </div>
        </el-col>
        <el-col :span="24" :md="8" class="mb-5">
          <div class="feature-card dark:!bg-gray-800 dark:!shadow-black/30" @click="$router.push('/profile')">
            <div class="feature-icon bg-purple-100 text-purple-600">
              <span class="text-4xl">👤</span>
            </div>
            <h3 class="text-lg font-bold text-gray-800 dark:text-gray-200 mb-2">个人中心</h3>
            <p class="text-sm text-gray-500 dark:text-gray-400 leading-relaxed">
              管理您的账户信息，查看注册详情，管理员可通过此处进入后台管理系统
            </p>
          </div>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup>
// 导入计算属性，根据登录状态显示不同按钮
import { computed } from 'vue'

// 判断是否已登录（通过 localStorage 中的 token）
const isLoggedIn = computed(() => !!localStorage.getItem('lsnuts_token'))

// 获取当前日期，格式为"今天是XXXX年X月X日"
const currentDate = computed(() => {
  const now = new Date()
  const year = now.getFullYear()
  const month = now.getMonth() + 1
  const day = now.getDate()
  return `今天是${year}年${month}月${day}日`
})
</script>

<style scoped>
.hero { 
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
  color: white;
}
.feature-card {
  background: white;
  border-radius: 12px;
  padding: 28px 24px;
  text-align: center;
  cursor: pointer;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
  transition: all 0.3s ease;
  height: 100%;
  color: #374151;
}
.feature-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.12);
}
.feature-icon {
  width: 72px;
  height: 72px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 16px;
}
</style>

<style>
.dark .feature-card {
  background: #1f2937 !important;
  color: #e5e7eb !important;
  box-shadow: 0 2px 12px rgba(0,0,0,0.3) !important;
}
.dark .feature-card:hover {
  box-shadow: 0 8px 25px rgba(0,0,0,0.4) !important;
}
.dark .feature-card h3 {
  color: #e5e7eb !important;
}
.dark .feature-card p {
  color: #9ca3af !important;
}
</style>