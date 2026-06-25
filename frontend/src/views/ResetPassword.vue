<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-100 dark:bg-gray-900 p-4">
    <el-card class="w-full max-w-md">
      <template #header>
        <div class="text-center text-xl font-bold">重置密码</div>
      </template>
      
      <div v-if="!tokenValid" class="text-center py-8">
        <div class="text-red-500 text-lg mb-4">{{ errorMsg }}</div>
        <el-button type="primary" @click="$router.push('/forgot-password')">重新申请</el-button>
      </div>
      
      <el-form v-else :model="form" :rules="rules" ref="formRef" label-width="80px">
        <el-form-item label="用户名">
          <span class="font-bold">{{ username }}</span>
        </el-form-item>
        <el-form-item label="新密码" prop="password">
          <el-input v-model="form.password" type="password" placeholder="请输入新密码(6-30位)" show-password />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input v-model="form.confirmPassword" type="password" placeholder="请再次输入新密码" show-password />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" class="w-full" :loading="loading" @click="submit">
            重置密码
          </el-button>
        </el-form-item>
      </el-form>
      
      <div class="text-center mt-4">
        <router-link to="/login" class="text-blue-500 hover:underline">返回登录</router-link>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from '../axios'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const formRef = ref(null)
const loading = ref(false)
const tokenValid = ref(false)
const errorMsg = ref('')
const username = ref('')

const form = reactive({
  password: '',
  confirmPassword: ''
})

const validatePass2 = (rule, value, callback) => {
  if (value !== form.password) {
    callback(new Error('两次输入密码不一致'))
  } else {
    callback()
  }
}

const rules = {
  password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, max: 30, message: '密码需6-30个字符', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
    { validator: validatePass2, trigger: 'blur' }
  ]
}

onMounted(async () => {
  const token = route.query.token
  if (!token) {
    tokenValid.value = false
    errorMsg.value = '无效的链接'
    return
  }
  
  try {
    const res = await axios.get('/api/auth/verify-token', { params: { token } })
    tokenValid.value = true
    username.value = res.data.data.username
  } catch (e) {
    tokenValid.value = false
    errorMsg.value = e.response?.data?.msg || '链接已失效'
  }
})

const submit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  
  loading.value = true
  try {
    const res = await axios.post('/api/auth/reset-password', {
      token: route.query.token,
      new_password: form.password
    })
    ElMessage.success(res.data.msg)
    router.push('/login')
  } catch (e) {
    ElMessage.error(e.response?.data?.msg || '重置失败')
  } finally {
    loading.value = false
  }
}
</script>
