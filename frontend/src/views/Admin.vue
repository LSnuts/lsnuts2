<template>
  <!-- 管理员后台页面 -->
  <div class="p-3 md:p-5 dark:bg-gray-900 min-h-screen">
    <!-- 标签页切换：数据统计 / 用户管理 / 帖子管理 -->
    <el-tabs v-model="activeTab" class="mb-4">
      <el-tab-pane label="📊 数据统计" name="dashboard">
        <el-card shadow="hover" class="dark:!bg-gray-800 dark:!border-gray-700">
          <template #header>
            <div class="flex items-center justify-between">
              <span class="font-bold text-lg dark:text-gray-200">📊 数据概览</span>
              <el-button @click="loadStats()" size="small">🔄 刷新</el-button>
            </div>
          </template>
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div class="bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg p-4 text-white">
              <div class="text-3xl font-bold">{{ stats.total_users }}</div>
              <div class="text-sm opacity-80">总用户数</div>
              <div class="text-xs mt-2">今日 +{{ stats.today_users }}</div>
            </div>
            <div class="bg-gradient-to-br from-green-500 to-green-600 rounded-lg p-4 text-white">
              <div class="text-3xl font-bold">{{ stats.total_posts }}</div>
              <div class="text-sm opacity-80">总帖子数</div>
              <div class="text-xs mt-2">今日 +{{ stats.today_posts }}</div>
            </div>
            <div class="bg-gradient-to-br from-orange-500 to-orange-600 rounded-lg p-4 text-white">
              <div class="text-3xl font-bold">{{ stats.total_comments }}</div>
              <div class="text-sm opacity-80">总评论数</div>
              <div class="text-xs mt-2">今日 +{{ stats.today_comments }}</div>
            </div>
            <div class="bg-gradient-to-br from-purple-500 to-purple-600 rounded-lg p-4 text-white">
              <div class="text-3xl font-bold">{{ stats.total_files }}</div>
              <div class="text-sm opacity-80">总文件数</div>
            </div>
          </div>
        </el-card>
      </el-tab-pane>
      
      <el-tab-pane label="👥 用户管理" name="users">
        <!-- 用户管理卡片 -->
        <el-card shadow="hover" class="dark:!bg-gray-800 dark:!border-gray-700 dark:!text-gray-200">
          <template #header>
            <div class="flex items-center justify-between">
              <span class="font-bold text-lg dark:text-gray-200">👥 用户管理</span>
              <el-button @click="loadUsers()" size="small">🔄 刷新列表</el-button>
            </div>
          </template>
          <el-table :data="users" class="w-full" stripe>
            <el-table-column prop="id" label="ID" width="60" />
            <el-table-column prop="account_code" label="账号码" width="100" />
            <el-table-column prop="username" label="用户名" min-width="100" />
            <el-table-column prop="create_time" label="注册时间" width="160" />
            <el-table-column label="权限" width="90">
              <template #default="{ row }">
                <el-tag type="danger" v-if="row.is_admin === 1">管理员</el-tag>
                <el-tag type="success" v-else>普通用户</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="220" fixed="right">
              <template #default="{ row }">
                <el-button-group>
                  <el-button type="primary" size="small" @click="showEditDialog(row)">编辑</el-button>
                  <el-button type="warning" size="small" @click="resetAvatar(row.id)">重置头像</el-button>
                  <el-button type="danger" size="small" :disabled="row.id === myId" @click="del(row.id)">删除</el-button>
                </el-button-group>
              </template>
            </el-table-column>
          </el-table>
          <div v-if="users.length === 0" class="text-center text-gray-400 py-10">暂无用户</div>
        </el-card>
      </el-tab-pane>
      
      <el-tab-pane label="帖子管理" name="posts">
        <!-- 帖子管理卡片 -->
        <el-card shadow="hover" class="dark:!bg-gray-800 dark:!border-gray-700 dark:!text-gray-200">
          <template #header>
            <div class="flex items-center justify-between">
              <span class="font-bold text-lg dark:text-gray-200">📝 帖子管理</span>
              <el-button @click="loadPosts()" size="small">🔄 刷新列表</el-button>
            </div>
          </template>
          <el-table :data="posts" class="w-full" stripe>
            <el-table-column prop="id" label="ID" width="60" />
            <el-table-column prop="title" label="标题" min-width="150" show-overflow-tooltip />
            <el-table-column prop="user" label="作者" width="100" />
            <el-table-column prop="create_time" label="发布时间" width="160" />
            <el-table-column prop="comment_count" label="评论数" width="80" />
            <el-table-column label="置顶" width="70">
              <template #default="{ row }">
                <span v-if="row.is_pinned" class="text-orange-500 text-sm">📌 已置顶</span>
                <span v-else class="text-gray-300 dark:text-gray-600 text-sm">-</span>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="230" fixed="right">
              <template #default="{ row }">
                <el-button-group>
                  <el-button :type="row.is_pinned ? 'warning' : 'default'" size="small" @click="togglePin(row)">{{ row.is_pinned ? '取消置顶' : '置顶' }}</el-button>
                  <el-button type="primary" size="small" @click="viewPost(row.id)">查看详情</el-button>
                  <el-button type="danger" size="small" @click="delPost(row.id)">删除</el-button>
                </el-button-group>
              </template>
            </el-table-column>
          </el-table>
          <div v-if="posts.length === 0" class="text-center text-gray-400 py-10">暂无帖子</div>
        </el-card>
      </el-tab-pane>

      <el-tab-pane label="📢 公告管理" name="announcements">
        <el-card shadow="hover" class="dark:!bg-gray-800 dark:!border-gray-700 dark:!text-gray-200">
          <template #header>
            <div class="flex items-center justify-between">
              <span class="font-bold text-lg dark:text-gray-200">📢 公告管理</span>
              <el-button type="primary" size="small" @click="showAnnDialog()">发布公告</el-button>
            </div>
          </template>
          <el-table :data="announcements" class="w-full" stripe>
            <el-table-column prop="id" label="ID" width="60" />
            <el-table-column prop="title" label="标题" min-width="150">
              <template #default="{ row }">
                <span :class="{'text-red-500 font-bold': row.priority === 2, 'text-orange-500': row.priority === 1}">{{ row.title }}</span>
                <el-tag v-if="row.is_pinned" size="small" type="warning" class="ml-2">置顶</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="create_time" label="发布时间" width="160" />
            <el-table-column label="优先级" width="100">
              <template #default="{ row }">
                <el-tag v-if="row.priority === 2" type="danger" size="small">紧急</el-tag>
                <el-tag v-else-if="row.priority === 1" type="warning" size="small">重要</el-tag>
                <el-tag v-else type="info" size="small">普通</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="180" fixed="right">
              <template #default="{ row }">
                <el-button type="primary" size="small" @click="editAnn(row)">编辑</el-button>
                <el-button type="danger" size="small" @click="delAnn(row.id)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
          <div v-if="announcements.length === 0" class="text-center text-gray-400 py-10">暂无公告</div>
        </el-card>
      </el-tab-pane>
    </el-tabs>
    
    <!-- 编辑用户对话框 -->
    <el-dialog title="编辑用户" v-model="dialogVisible" width="90% max-w-[400px]">
      <el-form :model="editForm" label-width="80px">
        <el-form-item label="账号码">
          <el-input :value="editForm.account_code" disabled />
        </el-form-item>
        <el-form-item label="用户名">
          <el-input v-model="editForm.username" />
        </el-form-item>
        <el-form-item label="新密码">
          <el-input v-model="editForm.password" type="password" placeholder="不填则不修改密码" />
        </el-form-item>
        <el-form-item label="权限">
          <el-select v-model="editForm.is_admin">
            <el-option :value="0" label="普通用户" />
            <el-option :value="1" label="管理员" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveEdit">保存</el-button>
      </template>
    </el-dialog>

    <!-- 公告编辑对话框 -->
    <el-dialog title="发布/编辑公告" v-model="annDialogVisible" width="90% max-w-[500px]">
      <el-form :model="annForm" label-width="80px">
        <el-form-item label="标题" required>
          <el-input v-model="annForm.title" placeholder="请输入公告标题" />
        </el-form-item>
        <el-form-item label="内容" required>
          <el-input v-model="annForm.content" type="textarea" :rows="5" placeholder="请输入公告内容" />
        </el-form-item>
        <el-form-item label="优先级">
          <el-select v-model="annForm.priority">
            <el-option :value="0" label="普通" />
            <el-option :value="1" label="重要" />
            <el-option :value="2" label="紧急" />
          </el-select>
        </el-form-item>
        <el-form-item label="置顶">
          <el-switch v-model="annForm.is_pinned" :active-value="1" :inactive-value="0" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="annDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveAnn">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
// 导入响应式 API、请求工具、消息提示和路由
import { ref, onMounted } from 'vue'
import axios from '../axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRouter } from 'vue-router'

const router = useRouter()
const activeTab = ref('dashboard')  // 当前激活的标签页
const users = ref([])  // 用户列表数据
const posts = ref([])  // 帖子列表数据
const stats = ref({
  total_users: 0,
  total_posts: 0,
  total_comments: 0,
  total_files: 0,
  today_users: 0,
  today_posts: 0,
  today_comments: 0
})  // 统计数据
const myId = ref(null)  // 当前管理员自己的ID（用于禁止删除自己）
const dialogVisible = ref(false)  // 编辑用户对话框是否显示
const announcements = ref([])
const annDialogVisible = ref(false)
const annForm = ref({
  id: null,
  title: '',
  content: '',
  priority: 0,
  is_pinned: 0
})

const loadStats = async () => {
  try {
    const res = await axios.get('/api/admin/stats')
    stats.value = res.data.data
  } catch (e) {}
}
const editForm = ref({
  id: null,
  account_code: '',
  username: '',
  password: '',
  is_admin: 0
})

// 获取所有用户列表
const getUsers = async () => {
  const res = await axios.get('/api/admin/users')
  users.value = res.data.data
}

// 获取所有帖子列表
const getPosts = async () => {
  const res = await axios.get('/api/admin/posts')
  posts.value = res.data.data
}

// 获取当前管理员自己的ID
const getMyId = async () => {
  const res = await axios.get('/api/user/info')
  myId.value = res.data.data.id
}

// 删除指定用户
const del = async (id) => {
  try {
    await ElMessageBox.confirm('删除用户将同时删除其所有帖子、评论、文件和消息，此操作不可恢复，确定继续吗？', '确认删除用户', { type: 'warning', confirmButtonText: '删除', cancelButtonText: '取消' })
    await axios.delete(`/api/admin/delete/${id}`)
    ElMessage.success('删除成功')
    getUsers()
  } catch (e) { if (e !== 'cancel') throw e }
}

// 重置用户头像为默认
const resetAvatar = async (id) => {
  try {
    await ElMessageBox.confirm('确定重置该用户的头像为默认头像吗？', '确认重置头像', { type: 'warning' })
    const res = await axios.post(`/api/admin/reset_avatar/${id}`)
    if (res.data.code === 200) {
      ElMessage.success('头像已重置为默认')
      getUsers()
    } else {
      ElMessage.error(res.data.msg)
    }
  } catch (e) { if (e !== 'cancel') throw e }
}

// 查看帖子详情（跳转到论坛详情页）
const viewPost = (id) => {
  router.push(`/forum/detail/${id}`)
}

// 删除帖子
const delPost = async (id) => {
  try {
    await ElMessageBox.confirm('删除帖子将同时删除其所有评论和点赞，此操作不可恢复，确定继续吗？', '确认删除帖子', { type: 'warning', confirmButtonText: '删除', cancelButtonText: '取消' })
    await axios.delete(`/api/admin/delete_post/${id}`)
    ElMessage.success('删除成功')
    getPosts()
  } catch (e) { if (e !== 'cancel') throw e }
}

// 置顶/取消置顶帖子
const togglePin = async (row) => {
  const res = await axios.post(`/api/admin/toggle_pin/${row.id}`)
  if (res.data.code === 200) {
    ElMessage.success(res.data.msg)
    getPosts()  // 刷新列表
  } else {
    ElMessage.error(res.data.msg)
  }
}

// 打开编辑用户对话框并填充表单
const showEditDialog = (row) => {
  editForm.value = {
    id: row.id,
    account_code: row.account_code,
    username: row.username,
    password: '',
    is_admin: row.is_admin
  }
  dialogVisible.value = true
}

// 保存用户编辑信息
const saveEdit = async () => {
  if (!editForm.value.username) {
    ElMessage.warning('用户名不能为空')
    return
  }
  
  const data = {
    username: editForm.value.username,
    is_admin: editForm.value.is_admin
  }
  if (editForm.value.password) {
    data.password = editForm.value.password
  }
  
  const res = await axios.post(`/api/admin/update/${editForm.value.id}`, data)
  if (res.data.code === 200) {
    ElMessage.success('修改成功')
    dialogVisible.value = false
    getUsers()
  } else {
    ElMessage.error(res.data.msg)
  }
}

// 刷新用户列表（供模板调用）
const loadUsers = () => {
  getUsers()
}

// 刷新帖子列表（供模板调用）
const loadPosts = () => {
  getPosts()
}

// 公告相关
const getAnnouncements = async () => {
  try {
    const res = await axios.get('/api/admin/announcements')
    announcements.value = res.data.data
  } catch (e) {}
}

const showAnnDialog = (row = null) => {
  if (row) {
    annForm.value = { ...row }
  } else {
    annForm.value = { id: null, title: '', content: '', priority: 0, is_pinned: 0 }
  }
  annDialogVisible.value = true
}

const editAnn = (row) => {
  showAnnDialog(row)
}

const saveAnn = async () => {
  if (!annForm.value.title || !annForm.value.content) {
    ElMessage.warning('标题和内容不能为空')
    return
  }
  try {
    if (annForm.value.id) {
      await axios.put(`/api/admin/announcement/${annForm.value.id}`, annForm.value)
      ElMessage.success('公告更新成功')
    } else {
      await axios.post('/api/admin/announcement', annForm.value)
      ElMessage.success('公告发布成功')
    }
    annDialogVisible.value = false
    getAnnouncements()
  } catch (e) {
    ElMessage.error(e.response?.data?.msg || '操作失败')
  }
}

const delAnn = async (id) => {
  try {
    await ElMessageBox.confirm('确定删除该公告吗？', '确认删除', { type: 'warning' })
    await axios.delete(`/api/admin/announcement/${id}`)
    ElMessage.success('删除成功')
    getAnnouncements()
  } catch (e) { if (e !== 'cancel') throw e }
}

// 页面加载时初始化所有数据（并行请求优化）
onMounted(() => {
  Promise.all([loadStats(), getUsers(), getPosts(), getMyId(), getAnnouncements()])
})
</script>