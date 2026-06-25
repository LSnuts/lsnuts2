<template>
  <div class="p-3 md:p-5">
    <el-card v-if="user">
      <div class="flex items-center gap-4 mb-6">
        <el-avatar :size="80" :src="user.avatar || '/default-avatar.png'" />
        <div>
          <div class="flex items-center gap-2">
            <h2 class="text-2xl font-bold">{{ user.username }}</h2>
            <el-tag v-if="user.is_admin === 1" type="danger" size="small">管理员</el-tag>
          </div>
          <div class="text-gray-500 mt-1">
            <span>注册于 {{ user.create_time }}</span>
            <span class="mx-2">|</span>
            <span>发帖 {{ user.post_count }}</span>
            <span class="mx-2">|</span>
            <span>评论 {{ user.comment_count }}</span>
          </div>
        </div>
      </div>

      <el-divider />

      <el-tabs v-model="activeTab">
        <el-tab-pane label="他的帖子" name="posts">
          <div v-if="posts.length === 0" class="text-center py-12 text-gray-400">
            暂无帖子
          </div>
          <div v-else class="space-y-4">
            <div 
              v-for="post in posts" 
              :key="post.id"
              class="border rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer"
              @click="$router.push(`/forum/detail/${post.id}`)"
            >
              <h3 class="font-semibold text-lg mb-2">{{ post.title }}</h3>
              <p class="text-gray-600 dark:text-gray-400 text-sm mb-2 line-clamp-2">{{ post.content }}</p>
              <div class="flex items-center gap-4 text-xs text-gray-500">
                <el-tag v-if="post.tag" size="small">{{ post.tag }}</el-tag>
                <span>📅 {{ post.create_time }}</span>
                <span>💬 {{ post.comment_count }}</span>
                <span>❤️ {{ post.like_count }}</span>
              </div>
            </div>
          </div>
          <div v-if="total > pageSize" class="flex justify-center mt-4">
            <el-pagination 
              v-model:current-page="currentPage" 
              :page-size="pageSize" 
              :total="total" 
              layout="prev, pager, next" 
              small 
              @current-change="loadPosts" 
            />
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <el-card v-else class="text-center py-12">
      <div class="text-6xl mb-4">🔍</div>
      <div class="text-gray-500">用户不存在</div>
      <el-button class="mt-4" @click="$router.push('/forum')">返回论坛</el-button>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from '../axios'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()

const user = ref(null)
const posts = ref([])
const activeTab = ref('posts')
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

const loadUser = async () => {
  try {
    const res = await axios.get(`/api/user/profile/${route.params.id}`)
    user.value = res.data.data
  } catch (e) {
    user.value = null
  }
}

const loadPosts = async () => {
  try {
    const res = await axios.get(`/api/user/profile/${route.params.id}/posts`, {
      params: { page: currentPage.value, per_page: pageSize.value }
    })
    posts.value = res.data.data
    total.value = res.data.total || 0
  } catch (e) {}
}

watch(() => route.params.id, () => {
  loadUser()
  loadPosts()
}, { immediate: true })
</script>
