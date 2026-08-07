<template>
  <!-- 注册页面 -->
  <div class="flex justify-center items-center min-h-[80vh] p-3">
    <el-card title="用户注册" class="w-full max-w-[400px]">
      <el-form :model="form" label-width="80px">
        <el-form-item label="用户名"><el-input v-model="form.username" placeholder="请输入用户名" /></el-form-item>
        <el-form-item label="邮箱"><el-input v-model="form.email" type="email" placeholder="请输入邮箱" /></el-form-item>
        <el-form-item label="验证码"><div class="flex w-full gap-2"><el-input v-model="form.verification_code" maxlength="6" placeholder="请输入验证码" /><el-button :disabled="codeCountdown > 0" :loading="codeLoading" @click="sendCode">{{ codeCountdown > 0 ? `${codeCountdown}s后重发` : '获取验证码' }}</el-button></div></el-form-item>
        <el-form-item label="密码"><el-input v-model="form.password" type="password" show-password placeholder="请输入密码" /></el-form-item>
        <el-form-item label="确认密码"><el-input v-model="form.confirm_password" type="password" show-password placeholder="请再次输入密码" /></el-form-item>
        <el-form-item>
          <el-button type="primary" @click="register" :loading="loading" class="w-full md:w-auto">注册</el-button>
          <el-button @click="$router.push('/login')" class="mt-2 md:mt-0 md:ml-2">去登录</el-button>
        </el-form-item>
      </el-form>
      
      <!-- 注册成功后显示账号码 -->
      <div v-if="registeredAccountCode" class="mt-4 p-3 bg-green-100 rounded text-center">
        <div class="text-green-600 font-bold">注册成功！</div>
        <div class="text-sm mt-2">您的账号码是：<span class="text-lg font-bold text-green-700">{{ registeredAccountCode }}</span></div>
        <div class="text-xs text-gray-500 mt-1">请牢记此账号码，用于聊天搜索</div>
        <el-button type="primary" class="mt-3" @click="$router.push('/login')">前往登录</el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
// 导入响应式 API、路由和请求工具
import { ref, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from '../axios'
import { ElMessage } from 'element-plus'

const router = useRouter()
const form = ref({ username: '', email: '', password: '', confirm_password: '', verification_code: '' })
const loading = ref(false)  // 注册按钮加载状态
const codeLoading = ref(false)
const codeCountdown = ref(0)
let countdownTimer
const registeredAccountCode = ref('')  // 注册成功后返回的账号码

// 执行注册操作
const register = async () => {
  if (Object.values(form.value).some(value => !value)) {
    ElMessage.warning('请完整填写注册信息')
    return
  }
  if (form.value.password !== form.value.confirm_password) {
    ElMessage.warning('两次输入的密码不一致')
    return
  }
  loading.value = true
  try {
    const res = await axios.post('/api/register', form.value)
    if (res.data.code === 200) {
      registeredAccountCode.value = res.data.data.account_code  // 保存账号码用于展示
      ElMessage.success('注册成功')
    } else ElMessage.error(res.data.msg)  // 显示后端返回的错误信息（如用户名已存在）
  } finally { loading.value = false }
}

const sendCode = async () => {
  if (!form.value.email) return ElMessage.warning('请先输入邮箱')
  codeLoading.value = true
  try {
    const res = await axios.post('/api/auth/send-register-code', { email: form.value.email })
    if (res.data.code !== 200) return ElMessage.error(res.data.msg)
    ElMessage.success('验证码已发送，请查收邮件')
    codeCountdown.value = 60
    countdownTimer = setInterval(() => { codeCountdown.value -= 1; if (codeCountdown.value <= 0) clearInterval(countdownTimer) }, 1000)
  } finally { codeLoading.value = false }
}

onUnmounted(() => { if (countdownTimer) clearInterval(countdownTimer) })
</script>
