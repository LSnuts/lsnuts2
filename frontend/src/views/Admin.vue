<template>
  <!-- 管理员后台页面 -->
  <div class="p-3 md:p-5 dark:bg-gray-900 min-h-screen">
    <!-- 标签页切换：用户管理 / 帖子管理 -->
    <el-tabs v-model="activeTab" class="mb-4">
      <el-tab-pane label="用户管理" name="users">
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
  </div>
</template>

<script setup>
// 导入响应式 API、请求工具、消息提示和路由
import { ref, onMounted } from 'vue'
import axios from '../axios'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'

const router = useRouter()
const activeTab = ref('users')  // 当前激活的标签页
const users = ref([])  // 用户列表数据
const posts = ref([])  // 帖子列表数据
const myId = ref(null)  // 当前管理员自己的ID（用于禁止删除自己）
const dialogVisible = ref(false)  // 编辑用户对话框是否显示
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
  await axios.get(`/api/admin/delete/${id}`)
  ElMessage.success('删除成功')
  getUsers()
}

// 重置用户头像为默认
const resetAvatar = async (id) => {
  const res = await axios.post(`/api/admin/reset_avatar/${id}`)
  if (res.data.code === 200) {
    ElMessage.success('头像已重置为默认')
    getUsers()
  } else {
    ElMessage.error(res.data.msg)
  }
}

// 查看帖子详情（跳转到论坛详情页）
const viewPost = (id) => {
  router.push(`/forum/detail/${id}`)
}

// 删除帖子
const delPost = async (id) => {
  await axios.get(`/api/admin/delete_post/${id}`)
  ElMessage.success('删除成功')
  getPosts()
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

// 页面加载时初始化所有数据
onMounted(async () => {
  await getUsers()
  await getPosts()
  await getMyId()
})
</script>