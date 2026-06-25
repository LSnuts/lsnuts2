<template>
  <!-- 登录页面 -->
  <div class="flex justify-center items-center min-h-[80vh] p-3">
    <el-card title="用户登录" class="w-full max-w-[400px]">
      <el-form :model="form" label-width="80px">
        <el-form-item label="用户名"><el-input v-model="form.username" placeholder="请输入用户名" /></el-form-item>
        <el-form-item label="密码"><el-input v-model="form.password" type="password" placeholder="请输入密码" @keyup.enter="login" /></el-form-item>
        <el-form-item>
          <el-button type="primary" @click="login" :loading="loading" class="w-full md:w-auto">登录</el-button>
          <el-button @click="$router.push('/register')" class="mt-2 md:mt-0 md:ml-2">去注册</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
// 导入响应式 API、路由和请求工具
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from '../axios'
import { ElMessage } from 'element-plus'
import { useUserStore } from '../stores/user'

const emit = defineEmits(['login'])  // 登录成功后通知父组件刷新用户信息
const router = useRouter()
const userStore = useUserStore()
const form = ref({ username: '', password: '' })  // 登录表单数据
const loading = ref(false)  // 登录按钮加载状态

// 执行登录操作
const login = async () => {
  if (!form.value.username || !form.value.password) {
    ElMessage.warning('请输入账号密码')
    return
  }
  loading.value = true
  try {
    const res = await axios.post('/api/login', form.value)
    if (res.data.code === 200) {
      ElMessage.success('登录成功')
      // 立即刷新用户信息
      await userStore.fetchUserInfo()
      emit('login')  // 通知父组件
      router.push('/')  // 跳转到首页
    } else ElMessage.error(res.data.msg)  // 显示后端返回的错误信息
  } catch (e) {
    ElMessage.error(e.response?.data?.msg || '登录失败')
  } finally { loading.value = false }
}
</script>
