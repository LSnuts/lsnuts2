<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-100 dark:bg-gray-900 p-4">
    <el-card class="w-full max-w-md">
      <template #header>
        <div class="text-center text-xl font-bold">忘记密码</div>
      </template>
      
      <el-form :model="form" :rules="rules" ref="formRef" label-width="80px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="账号码" prop="account_code">
          <el-input v-model="form.account_code" placeholder="请输入6位账号码" maxlength="6" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="form.email" type="email" placeholder="请输入注册邮箱" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" class="w-full" :loading="loading" @click="submit">
          发送重置邮件
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
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import axios from '../axios'
import { ElMessage } from 'element-plus'

const router = useRouter()
const formRef = ref(null)
const loading = ref(false)

const form = reactive({
  username: '',
  account_code: '',
  email: ''
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  account_code: [
    { required: true, message: '请输入账号码', trigger: 'blur' },
    { len: 6, message: '账号码为6位数字', trigger: 'blur' }
  ],
  email: [{ required: true, message: '请输入邮箱', trigger: 'blur' }]
}

const submit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  
  loading.value = true
  try {
    const res = await axios.post('/api/auth/forgot-password', {
      username: form.username,
      account_code: form.account_code,
      email: form.email
    })
    ElMessage.success(res.data.msg)
  } catch (e) {
    ElMessage.error(e.response?.data?.msg || '验证失败')
  } finally {
    loading.value = false
  }
}
</script>
