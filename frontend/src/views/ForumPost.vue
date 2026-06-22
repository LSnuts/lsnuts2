<template>
  <!-- 发布新帖页面 -->
  <div class="p-3 md:p-5">
    <el-card title="发布新帖" class="max-w-[800px] mx-auto">
      <el-form :model="form" label-width="80px">
        <el-form-item label="标题">
          <el-input v-model="form.title" placeholder="请输入帖子标题" />
        </el-form-item>
        <el-form-item label="分类">
          <el-radio-group v-model="form.tag" size="small">
            <el-radio-button value="">📂 其他</el-radio-button>
            <el-radio-button value="tech">💻 技术分享</el-radio-button>
            <el-radio-button value="help">❓ 提问求助</el-radio-button>
            <el-radio-button value="chat">💬 闲聊灌水</el-radio-button>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="内容">
          <RichEditor v-model="form.content" placeholder="请输入帖子内容... 支持 Markdown 格式" :rows="6" />
        </el-form-item>
        <!-- 上传图片 -->
        <el-form-item label="图片">
          <div class="flex flex-col gap-2">
            <div class="flex items-center gap-2">
              <el-button type="primary" size="small" @click="triggerImageInput">📷 选择图片</el-button>
              <input ref="imageInput" type="file" accept="image/png,image/jpeg,image/jpg,image/gif,image/webp" class="hidden" @change="onImageChange" />
              <el-button v-if="imageFile" type="danger" size="small" @click="removeImage">取消</el-button>
            </div>
            <div v-if="imageFile" class="text-sm text-gray-500">{{ imageFile.name }}</div>
            <img v-if="imagePreview" :src="imagePreview" class="max-w-[200px] max-h-[150px] object-contain border rounded" />
          </div>
        </el-form-item>
        <!-- 上传附件 -->
        <el-form-item label="附件">
          <div class="flex items-center gap-2">
            <el-button type="primary" size="small" @click="triggerAttachInput">📎 选择附件</el-button>
            <input ref="attachInput" type="file" class="hidden" @change="onAttachChange" />
            <el-button v-if="attachFile" type="danger" size="small" @click="removeAttach">取消</el-button>
            <span v-if="attachFile" class="text-sm text-gray-500 ml-2">{{ attachFile.name }}</span>
          </div>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="submit" :loading="loading" size="small">发布帖子</el-button>
          <el-button @click="$router.back()" size="small">返回</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
// 导入响应式 API、路由、请求工具和消息提示
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from '../axios'
import { ElMessage } from 'element-plus'
import RichEditor from '../components/RichEditor.vue'

const router = useRouter()
const form = ref({ title: '', content: '', tag: '' })  // 帖子表单数据
const loading = ref(false)  // 提交按钮加载状态
const imageFile = ref(null)  // 选中的图片文件
const imagePreview = ref('')  // 图片预览 URL
const attachFile = ref(null)  // 选中的附件文件
const imageInput = ref(null)  // 图片文件选择器 DOM 引用
const attachInput = ref(null)  // 附件文件选择器 DOM 引用

// 触发图片文件选择器
const triggerImageInput = () => {
  imageInput.value?.click()
}

// 触发附件文件选择器
const triggerAttachInput = () => {
  attachInput.value?.click()
}

// 选择图片时生成预览
const onImageChange = (e) => {
  const file = e.target.files[0]
  if (!file) return
  if (file.size > 10 * 1024 * 1024) {
    ElMessage.warning('图片大小不能超过10M')
    return
  }
  imageFile.value = file
  imagePreview.value = URL.createObjectURL(file)
}

// 取消图片
const removeImage = () => {
  imageFile.value = null
  imagePreview.value = ''
}

// 选择附件
const onAttachChange = (e) => {
  const file = e.target.files[0]
  if (!file) return
  if (file.size > 10 * 1024 * 1024) {
    ElMessage.warning('附件大小不能超过10M')
    return
  }
  attachFile.value = file
}

// 取消附件
const removeAttach = () => {
  attachFile.value = null
}

// 提交发布帖子（使用 FormData 支持文件上传）
const submit = async () => {
  if (!form.value.title || !form.value.content) {
    ElMessage.warning('标题和内容不能为空')
    return
  }
  loading.value = true
  try {
    const formData = new FormData()
    formData.append('title', form.value.title)
    formData.append('content', form.value.content)
    formData.append('tag', form.value.tag)
    if (imageFile.value) {
      formData.append('image', imageFile.value)
    }
    if (attachFile.value) {
      formData.append('attachment', attachFile.value)
    }
    
    const res = await axios.post('/api/forum/post', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    if (res.data.code === 200) {
      ElMessage.success('发布成功')
      router.push('/forum')  // 发布成功跳转到论坛列表
    } else {
      ElMessage.error(res.data.msg)
    }
  } finally {
    loading.value = false
  }
}
</script>