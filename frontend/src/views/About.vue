<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900">
    <div class="hero text-center px-4 py-10 md:py-16">
      <div class="max-w-3xl mx-auto">
        <h1 class="text-2xl md:text-5xl text-white font-bold mb-3">🌐 关于本站</h1>
        <p class="text-base md:text-xl text-white/80">lsnuts 云端平台 - 安全、高效、一站式云端服务</p>
      </div>
    </div>
    <div class="max-w-4xl mx-auto px-4 -mt-6 pb-10">
      <div class="space-y-5">
        <div class="feature-card">
          <div class="flex items-center gap-3 mb-3">
            <span class="text-3xl">📖</span>
            <h2 class="text-xl font-bold text-gray-800 dark:text-gray-100">平台简介</h2>
          </div>
          <p class="text-gray-600 dark:text-gray-400 leading-relaxed">
            lsnuts 是一个集安全网盘存储与轻量论坛交流于一体的云端服务平台。我们致力于为用户提供安全可靠的文件存储和便捷高效的社区交流体验。
          </p>
        </div>
        <div class="feature-card">
          <div class="flex items-center gap-3 mb-3">
            <span class="text-3xl">🎯</span>
            <h2 class="text-xl font-bold text-gray-800 dark:text-gray-100">平台特色</h2>
          </div>
          <ul class="text-gray-600 dark:text-gray-400 leading-relaxed space-y-2 list-disc pl-5">
            <li>文件加密安全存储，支持上传下载管理</li>
            <li>轻量级社区论坛，支持图片附件上传</li>
            <li>帖子置顶、楼中楼回复等丰富交互功能</li>
            <li>响应式设计，桌面端与移动端完美适配</li>
            <li>暗色模式支持，保护夜间使用体验</li>
            <li>管理员后台，高效管理用户和内容</li>
          </ul>
        </div>
        <div class="feature-card">
          <div class="flex items-center gap-3 mb-3">
            <span class="text-3xl">🛠️</span>
            <h2 class="text-xl font-bold text-gray-800 dark:text-gray-100">技术栈</h2>
          </div>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
            <div class="bg-gray-50 dark:bg-gray-800 rounded-lg p-3 text-center">
              <div class="font-semibold text-blue-600 dark:text-blue-400">Flask</div>
              <div class="text-xs text-gray-500 dark:text-gray-400">后端框架</div>
            </div>
            <div class="bg-gray-50 dark:bg-gray-800 rounded-lg p-3 text-center">
              <div class="font-semibold text-green-600 dark:text-green-400">Vue 3</div>
              <div class="text-xs text-gray-500 dark:text-gray-400">前端框架</div>
            </div>
            <div class="bg-gray-50 dark:bg-gray-800 rounded-lg p-3 text-center">
              <div class="font-semibold text-purple-600 dark:text-purple-400">Element Plus</div>
              <div class="text-xs text-gray-500 dark:text-gray-400">UI 组件库</div>
            </div>
            <div class="bg-gray-50 dark:bg-gray-800 rounded-lg p-3 text-center">
              <div class="font-semibold text-orange-600 dark:text-orange-400">Tailwind CSS</div>
              <div class="text-xs text-gray-500 dark:text-gray-400">样式框架</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.hero { 
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}
.feature-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
}
.dark .feature-card {
  background: #1f2937;
  box-shadow: 0 2px 12px rgba(0,0,0,0.3);
}
</style>
