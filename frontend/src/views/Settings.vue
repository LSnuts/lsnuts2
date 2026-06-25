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
                <div class="text-xs text-gray-400 dark:text-gray-500">裁剪并上传自定义头像</div>
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

      <!-- ====== 头像子页 ====== -->
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
          <div class="text-xs text-gray-400 dark:text-gray-500 mt-2">点击头像选择图片 · 支持裁剪</div>
        </div>
      </template>

      <!-- ====== 用户名子页 ====== -->
      <template v-else-if="activeSection === 'username'">
        <el-button class="back-btn" @click="activeSection = ''">← 返回设置</el-button>
        <div class="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-4">修改用户名</div>
        <el-input v-model="newUsername" placeholder="输入新用户名（2-20字符）" :maxlength="20" show-word-limit />
        <div class="text-xs text-gray-400 dark:text-gray-500 mt-2">当前：{{ userInfo.username }}</div>
        <div class="mt-4">
          <el-button type="primary" @click="updateUsername" :loading="savingUsername" class="w-full">保存</el-button>
        </div>
      </template>

      <!-- ====== 密码子页 ====== -->
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

    <!-- 头像裁剪弹窗 -->
    <el-dialog v-model="cropVisible" title="裁剪头像" width="90% max-w-[520px]" @close="resetCrop">
      <div class="flex flex-col items-center gap-4">
        <div class="text-xs text-gray-500 dark:text-gray-400 text-center">滚轮缩放图片 · 拖动蓝色方框选择头像区域</div>
        <div class="crop-stage relative overflow-hidden border-2 border-dashed border-gray-400 dark:border-gray-500 rounded-lg select-none" style="width:320px;height:320px;" @wheel.prevent="onWheel">
          <img ref="cropImage" :src="cropSrc" class="absolute select-none pointer-events-none"
            :style="{ left: cropX + 'px', top: cropY + 'px', width: cropW + 'px', height: cropH + 'px' }" />
          <div class="crop-box absolute cursor-move rounded-lg border-2 border-blue-500"
            :style="{ left: cropBoxX + 'px', top: cropBoxY + 'px', width: cropBoxSize + 'px', height: cropBoxSize + 'px' }"
            @mousedown.stop="startBoxDrag">
            <div class="absolute inset-0 bg-blue-500/10"></div>
            <div class="absolute top-0 left-0 w-full h-1 bg-blue-500/60"></div>
            <div class="absolute bottom-0 left-0 w-full h-1 bg-blue-500/60"></div>
            <div class="absolute top-0 left-0 w-1 h-full bg-blue-500/60"></div>
            <div class="absolute top-0 right-0 w-1 h-full bg-blue-500/60"></div>
            <div class="absolute -top-1 -left-1 w-3 h-3 border-t-2 border-l-2 border-blue-500 bg-white rounded-tl-sm"></div>
            <div class="absolute -top-1 -right-1 w-3 h-3 border-t-2 border-r-2 border-blue-500 bg-white rounded-tr-sm"></div>
            <div class="absolute -bottom-1 -left-1 w-3 h-3 border-b-2 border-l-2 border-blue-500 bg-white rounded-bl-sm"></div>
            <div class="absolute -bottom-1 -right-1 w-3 h-3 border-b-2 border-r-2 border-blue-500 bg-white rounded-br-sm"></div>
          </div>
        </div>
        <div class="flex items-center gap-4 w-full max-w-[320px]">
          <span class="text-xs text-gray-500 dark:text-gray-400 whitespace-nowrap">缩放</span>
          <el-slider v-model="cropScale" :min="50" :max="250" :step="1" class="flex-1" />
          <el-button size="small" @click="resetCrop">重置</el-button>
        </div>
        <div class="flex items-center gap-2">
          <el-button size="small" @click="cropVisible = false">取消</el-button>
          <el-button size="small" type="primary" @click="doCropAndUpload" :loading="uploadingAvatar">确认裁剪并上传</el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
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
const cropVisible = ref(false)
const cropSrc = ref('')
const cropImage = ref(null)
const cropScale = ref(100)
const cropX = ref(0)
const cropY = ref(0)
const cropW = ref(300)
const cropH = ref(300)
const cropBoxSize = 220
const cropBoxX = ref(50)
const cropBoxY = ref(50)
const dragStart = ref({ x: 0, y: 0, boxX: 0, boxY: 0 })
const isDragging = ref(false)
const uploadingAvatar = ref(false)
const naturalW = ref(0)
const naturalH = ref(0)

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

// 图片压缩：限制最大尺寸，减少内存占用和上传体积
const compressImage = (file, maxWidth = 1200, maxHeight = 1200, quality = 0.8) => {
  return new Promise((resolve, reject) => {
    const img = new Image()
    const url = URL.createObjectURL(file)
    img.onload = () => {
      URL.revokeObjectURL(url)
      let { width, height } = img
      if (width > maxWidth || height > maxHeight) {
        const ratio = Math.min(maxWidth / width, maxHeight / height)
        width *= ratio
        height *= ratio
      }
      const canvas = document.createElement('canvas')
      canvas.width = width
      canvas.height = height
      const ctx = canvas.getContext('2d')
      ctx.drawImage(img, 0, 0, width, height)
      canvas.toBlob((blob) => {
        if (blob) resolve(blob)
        else reject(new Error('压缩失败'))
      }, 'image/jpeg', quality)
    }
    img.onerror = reject
    img.src = url
  })
}

const onAvatarFile = async (e) => {
  const file = e.target.files[0]
  if (!file) return
  if (file.size > 5 * 1024 * 1024) { ElMessage.warning('图片大小不能超过5M'); return }
  try {
    const compressedBlob = await compressImage(file, 1200, 1200, 0.8)
    const reader = new FileReader()
    reader.onload = (ev) => { cropSrc.value = ev.target.result; cropVisible.value = true; nextTick(() => { resetCrop() }) }
    reader.readAsDataURL(compressedBlob)
  } catch {
    ElMessage.error('图片处理失败')
  }
  e.target.value = ''
}
const resetCrop = () => {
  cropScale.value = 100
  cropBoxX.value = (320 - cropBoxSize) / 2
  cropBoxY.value = (320 - cropBoxSize) / 2
  if (!cropImage.value) return
  naturalW.value = cropImage.value.naturalWidth
  naturalH.value = cropImage.value.naturalHeight
  const maxDim = 280
  const s = Math.min(maxDim / naturalW.value, maxDim / naturalH.value, 1)
  cropW.value = naturalW.value * s
  cropH.value = naturalH.value * s
  cropX.value = (320 - cropW.value) / 2
  cropY.value = (320 - cropH.value) / 2
}

const onWheel = (e) => { const delta = e.deltaY > 0 ? -10 : 10; cropScale.value = Math.max(50, Math.min(250, cropScale.value + delta)) }
const startBoxDrag = (e) => {
  isDragging.value = true
  dragStart.value = { x: e.clientX, y: e.clientY, boxX: cropBoxX.value, boxY: cropBoxY.value }
  const onMove = (ev) => {
    if (!isDragging.value) return
    const newX = dragStart.value.boxX + (ev.clientX - dragStart.value.x)
    const newY = dragStart.value.boxY + (ev.clientY - dragStart.value.y)
    cropBoxX.value = Math.max(0, Math.min(320 - cropBoxSize, newX))
    cropBoxY.value = Math.max(0, Math.min(320 - cropBoxSize, newY))
  }
  const onUp = () => { isDragging.value = false; document.removeEventListener('mousemove', onMove); document.removeEventListener('mouseup', onUp) }
  document.addEventListener('mousemove', onMove); document.addEventListener('mouseup', onUp)
}
const doCropAndUpload = () => {
  const img = cropImage.value
  if (!img) return
  const canvas = document.createElement('canvas'); canvas.width = 200; canvas.height = 200
  const ctx = canvas.getContext('2d')
  const scale = img.naturalWidth / cropW.value
  
  const sourceX = (cropBoxX.value - cropX.value) * scale
  const sourceY = (cropBoxY.value - cropY.value) * scale
  const sourceSize = cropBoxSize * scale
  
  ctx.fillStyle = '#e5e7eb'; ctx.fillRect(0, 0, 200, 200)
  
  ctx.drawImage(img, sourceX, sourceY, sourceSize, sourceSize, 0, 0, 200, 200)
  
  canvas.toBlob(async (blob) => {
    uploadingAvatar.value = true
    try {
      const formData = new FormData(); formData.append('avatar', blob, 'avatar.jpg')
      await axios.post('/api/user/avatar', formData, { headers: { 'Content-Type': 'multipart/form-data' } })
      ElMessage.success('头像更新成功')
      cropVisible.value = false; loadUserInfo(); emit('avatar-change')
    } catch (e) { ElMessage.error(e.response?.data?.msg || '上传失败') }
    finally { uploadingAvatar.value = false }
  }, 'image/jpeg', 0.85)
}
watch(cropScale, (val) => {
  if (!cropImage.value) return
  const scale = val / 100
  const maxDim = 280 * scale
  const s = Math.min(maxDim / naturalW.value, maxDim / naturalH.value)
  const newW = naturalW.value * s
  const newH = naturalH.value * s
  cropX.value += (cropW.value - newW) / 2
  cropY.value += (cropH.value - newH) / 2
  cropW.value = newW
  cropH.value = newH
})
onMounted(loadUserInfo)
</script>

<style scoped>
.crop-stage { background: repeating-conic-gradient(#ccc 0% 25%, #fff 0% 50%) 50% / 16px 16px; }
.dark .crop-stage { background: repeating-conic-gradient(#333 0% 25%, #222 0% 50%) 50% / 16px 16px; }
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
