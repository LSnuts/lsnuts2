<template>
  <div class="p-3 md:p-5">
    <div class="max-w-[600px] mx-auto mb-3">
      <el-button class="back-btn" @click="$router.push('/profile')">← 返回个人中心</el-button>
    </div>
    <el-card class="max-w-[600px] mx-auto dark:!bg-gray-800 dark:!border-gray-700 dark:!text-gray-200">
      <template v-if="activeSection === ''">
        <div class="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-4">账户设置</div>
        <div class="space-y-2">
          <div class="settings-entry" @click="activeSection = 'avatar'">
            <div class="flex items-center gap-3">
              <span class="text-2xl">📷</span>
              <div>
                <div class="text-sm font-medium text-gray-800 dark:text-gray-200">修改头像</div>
                <div class="text-xs text-gray-400 dark:text-gray-500">上传自定义头像</div>
              </div>
            </div>
            <span class="text-gray-400 text-lg">›</span>
          </div>
          <div class="settings-entry" @click="activeSection = 'username'">
            <div class="flex items-center gap-3">
              <span class="text-2xl">✏️</span>
              <div>
                <div class="text-sm font-medium text-gray-800 dark:text-gray-200">修改用户名</div>
                <div class="text-xs text-gray-400 dark:text-gray-500">当前：{{ userInfo.username }}</div>
              </div>
            </div>
            <span class="text-gray-400 text-lg">›</span>
          </div>
          <div class="settings-entry" @click="activeSection = 'password'">
            <div class="flex items-center gap-3">
              <span class="text-2xl">🔒</span>
              <div>
                <div class="text-sm font-medium text-gray-800 dark:text-gray-200">修改密码</div>
                <div class="text-xs text-gray-400 dark:text-gray-500">更新账户登录密码</div>
              </div>
            </div>
            <span class="text-gray-400 text-lg">›</span>
          </div>
        </div>
      </template>

      <template v-else-if="activeSection === 'avatar'">
        <el-button class="back-btn" @click="activeSection = ''">← 返回设置</el-button>
        <div class="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-4">修改头像</div>
        <div class="flex flex-col items-center mb-4">
          <div class="relative group cursor-pointer" @click="triggerAvatarInput">
            <img :src="avatarUrl" :alt="userInfo.username"
              class="w-[20vw] h-[20vw] max-w-[200px] max-h-[200px] min-w-[100px] min-h-[100px] object-cover rounded-lg shadow-md" />
            <div class="absolute inset-0 bg-black/40 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
              <span class="text-white text-sm font-medium">📷 更换头像</span>
            </div>
          </div>
          <input ref="avatarInput" type="file" accept="image/*" class="hidden" @change="onAvatarFile" />
          <div v-if="!uploadingAvatar" class="text-xs text-gray-400 dark:text-gray-500 mt-2">点击头像选择图片，自动裁剪为方形头像</div>
          <div v-else class="text-xs text-blue-500 mt-2">正在上传...</div>
        </div>
        <div v-if="previewUrl" class="flex flex-col items-center gap-3 mt-2">
          <div class="text-sm text-gray-600 dark:text-gray-400">预览：</div>
          <img :src="previewUrl" class="w-32 h-32 object-cover rounded-full shadow-md border-2 border-gray-200 dark:border-gray-600" />
          <div class="flex gap-2">
            <el-button size="small" @click="cancelPreview">取消</el-button>
            <el-button size="small" type="primary" :loading="uploadingAvatar" @click="doUpload">确认上传</el-button>
          </div>
        </div>
      </template>

      <template v-else-if="activeSection === 'username'">
        <el-button class="back-btn" @click="activeSection = ''">← 返回设置</el-button>
        <div class="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-4">修改用户名</div>
        <el-input v-model="newUsername" placeholder="输入新用户名（2-20字符）" :maxlength="20" show-word-limit />
        <div class="text-xs text-gray-400 dark:text-gray-500 mt-2">当前：{{ userInfo.username }}</div>
        <div class="mt-4">
          <el-button type="primary" @click="updateUsername" :loading="savingUsername" class="w-full">保存</el-button>
        </div>
      </template>

      <template v-else-if="activeSection === 'password'">
        <el-button class="back-btn" @click="activeSection = ''">← 返回设置</el-button>
        <div class="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-4">修改密码</div>
        <div class="space-y-3">
          <el-input v-model="oldPassword" type="password" placeholder="输入旧密码" show-password />
          <el-input v-model="newPassword" type="password" placeholder="输入新密码（6-30字符）" show-password />
          <el-input v-model="confirmPassword" type="password" placeholder="确认新密码" show-password />
          <el-button type="primary" @click="changePassword" :loading="savingPassword" class="w-full">保存</el-button>
        </div>
      </template>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from '../axios'
import { ElMessage } from 'element-plus'
import { DEFAULT_AVATAR_SVG } from '../utils/constants'
import { getAvatarUrl } from '../utils/helpers'

const emit = defineEmits(['avatar-change'])

const activeSection = ref('')
const userInfo = ref({})
const newUsername = ref('')
const savingUsername = ref(false)
const oldPassword = ref('')
const newPassword = ref('')
const confirmPassword = ref('')
const savingPassword = ref(false)

const avatarInput = ref(null)
const uploadingAvatar = ref(false)
const previewUrl = ref('')
const pendingBlob = ref(null)

const avatarUrl = computed(() => {
  return getAvatarUrl(userInfo.value.avatar) || DEFAULT_AVATAR_SVG
})

const loadUserInfo = async () => {
  try {
    const res = await axios.get('/api/user/info')
    userInfo.value = res.data.data
    newUsername.value = res.data.data.username
  } catch (e) {}
}

const updateUsername = async () => {
  if (!newUsername.value.trim() || newUsername.value.trim().length < 2) { ElMessage.warning('用户名至少2个字符'); return }
  savingUsername.value = true
  try {
    const res = await axios.put('/api/user/username', { username: newUsername.value.trim() })
    ElMessage.success(res.data.msg)
    loadUserInfo()
    emit('avatar-change')
    activeSection.value = ''
  } catch (e) { ElMessage.error(e.response?.data?.msg || '修改失败') }
  finally { savingUsername.value = false }
}

const changePassword = async () => {
  if (!oldPassword.value || !newPassword.value) { ElMessage.warning('请填写密码'); return }
  if (newPassword.value !== confirmPassword.value) { ElMessage.warning('两次新密码不一致'); return }
  savingPassword.value = true
  try {
    const res = await axios.put('/api/user/password', { old_password: oldPassword.value, new_password: newPassword.value })
    ElMessage.success(res.data.msg)
    oldPassword.value = ''; newPassword.value = ''; confirmPassword.value = ''
    activeSection.value = ''
  } catch (e) { ElMessage.error(e.response?.data?.msg || '修改失败') }
  finally { savingPassword.value = false }
}

const triggerAvatarInput = () => { avatarInput.value?.click() }

const processImage = (file) => {
  return new Promise((resolve, reject) => {
    const img = new Image()
    const url = URL.createObjectURL(file)
    img.onload = () => {
      URL.revokeObjectURL(url)
      const size = 300
      const canvas = document.createElement('canvas')
      canvas.width = size
      canvas.height = size
      const ctx = canvas.getContext('2d')
      const side = Math.min(img.width, img.height)
      const sx = (img.width - side) / 2
      const sy = (img.height - side) / 2
      ctx.drawImage(img, sx, sy, side, side, 0, 0, size, size)
      canvas.toBlob((blob) => {
        if (blob) resolve(blob)
        else reject(new Error('处理失败'))
      }, 'image/jpeg', 0.9)
    }
    img.onerror = reject
    img.src = url
  })
}

const onAvatarFile = async (e) => {
  const file = e.target.files[0]
  if (!file) return
  if (file.size > 10 * 1024 * 1024) { ElMessage.warning('图片大小不能超过10M'); return }
  try {
    const blob = await processImage(file)
    pendingBlob.value = blob
    previewUrl.value = URL.createObjectURL(blob)
  } catch {
    ElMessage.error('图片处理失败')
  }
  e.target.value = ''
}

const cancelPreview = () => {
  if (previewUrl.value) URL.revokeObjectURL(previewUrl.value)
  previewUrl.value = ''
  pendingBlob.value = null
}

const doUpload = async () => {
  if (!pendingBlob.value) return
  uploadingAvatar.value = true
  try {
    const formData = new FormData()
    formData.append('avatar', pendingBlob.value, 'avatar.jpg')
    await axios.post('/api/user/avatar', formData, { headers: { 'Content-Type': 'multipart/form-data' } })
    ElMessage.success('头像更新成功')
    if (previewUrl.value) URL.revokeObjectURL(previewUrl.value)
    previewUrl.value = ''
    pendingBlob.value = null
    loadUserInfo()
    emit('avatar-change')
  } catch (e) { ElMessage.error(e.response?.data?.msg || '上传失败') }
  finally { uploadingAvatar.value = false }
}

onMounted(loadUserInfo)
</script>

<style scoped>
.settings-entry {
  display: flex; align-items: center; justify-content: space-between;
  padding: 14px 16px; border-radius: 10px;
  border: 1px solid #e5e7eb; cursor: pointer;
  transition: all 0.2s ease;
  background: #fff;
}
.dark .settings-entry { background: #1f2937; border-color: #4b5563; }
.settings-entry:hover { border-color: #409eff; box-shadow: 0 2px 8px rgba(64,158,255,0.15); transform: translateY(-1px); }
.dark .settings-entry:hover { border-color: #60a5fa; box-shadow: 0 2px 8px rgba(96,165,250,0.2); }
</style>
