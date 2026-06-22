<template>
  <div class="flex flex-col items-center justify-center min-h-[60vh] p-5">
    <div class="text-8xl font-bold text-blue-500 mb-4">404</div>
    <div class="text-xl text-gray-600 dark:text-gray-400 mb-6">页面不存在或已被移除</div>
    <el-button type="primary" @click="$router.push('/')">🏠 返回首页</el-button>
  </div>
</template>
