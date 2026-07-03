<template>
  <div class="chat-container">
    <div v-if="!userStore.isLoggedIn" class="chat-login-required">
      <div class="login-icon">💬</div>
      <h3>请先登录</h3>
      <p>登录后可以搜索用户、添加好友</p>
      <el-button type="primary" @click="$router.push('/login')">去登录</el-button>
    </div>

    <div v-else class="chat-main">
      <div class="mobile-user-list-btn" @click="showUserList = true">
        ☰ 好友列表
      </div>

      <div class="chat-sidebar">
        <div class="chat-sidebar-header">
          <h3>💬 聊天</h3>
        </div>

        <div class="chat-tabs">
          <button 
            v-for="tab in tabs" 
            :key="tab.key" 
            :class="['tab-btn', { active: activeTab === tab.key }]"
            @click="activeTab = tab.key"
          >
            {{ tab.label }}
            <span v-if="tab.count > 0" class="tab-badge">{{ tab.count }}</span>
          </button>
        </div>

        <div v-if="activeTab === 'search'" class="search-section">
          <el-input 
            v-model="searchQuery" 
            placeholder="搜索用户名或账号"
            prefix-icon="Search"
            @keyup.enter="doSearch"
            class="search-input"
          />
          <el-button type="primary" @click="doSearch" style="width:100%;margin-top:8px;">搜索</el-button>
          
          <div v-if="searchResults.length > 0" class="search-results">
            <div 
              v-for="user in searchResults" 
              :key="user.id" 
              class="search-item"
            >
              <el-avatar :size="40" :src="user.avatar ? `https://api.118201820.xyz/api/uploads/${user.avatar}` : ''" :icon="!user.avatar ? 'User' : null">
                {{ user.username.charAt(0) }}
              </el-avatar>
              <div class="search-info">
                <div class="search-name">{{ user.username }}</div>
                <div class="search-code">{{ user.account_code }}</div>
              </div>
              <el-button 
                v-if="user.id !== userStore.userInfo.id && !isFriend(user.id) && !isPendingRequest(user.id)" 
                type="primary" 
                size="small" 
                @click="sendFriendRequest(user)"
              >
                添加好友
              </el-button>
              <div v-else-if="isPendingRequest(user.id)" class="pending-tag">等待同意</div>
              <div v-else-if="isFriend(user.id)" class="friend-tag">已好友</div>
              <div v-else-if="user.id === userStore.userInfo.id" class="self-tag">自己</div>
            </div>
          </div>
        </div>

        <div v-else-if="activeTab === 'friends'" class="friends-list">
          <div v-if="friends.length === 0" class="empty-friends">
            <div class="empty-icon">👥</div>
            <p>暂无好友</p>
            <p>去搜索添加好友吧</p>
          </div>
          <div 
            v-for="friend in friends" 
            :key="friend.id" 
            class="friend-item"
            :class="{ active: selectedUserId === friend.id }"
            @click="selectUser(friend)"
          >
            <div class="friend-avatar">
              <el-avatar :size="40" :src="friend.avatar ? `https://api.118201820.xyz/api/uploads/${friend.avatar}` : ''" :icon="!friend.avatar ? 'User' : null">
                {{ friend.username.charAt(0) }}
              </el-avatar>
            </div>
            <div class="friend-info">
              <div class="friend-name">{{ friend.username }}</div>
              <div class="friend-code">{{ friend.account_code }}</div>
            </div>
          </div>
        </div>

        <div v-else-if="activeTab === 'pending'" class="pending-list">
          <div v-if="pendingRequests.length === 0" class="empty-pending">
            <div class="empty-icon">📭</div>
            <p>暂无待处理请求</p>
          </div>
          <div 
            v-for="req in pendingRequests" 
            :key="req.id" 
            class="pending-item"
          >
            <div class="pending-avatar">
              <el-avatar :size="40" :src="req.avatar ? `https://api.118201820.xyz/api/uploads/${req.avatar}` : ''" :icon="!req.avatar ? 'User' : null">
                {{ req.username.charAt(0) }}
              </el-avatar>
            </div>
            <div class="pending-info">
              <div class="pending-name">{{ req.username }}</div>
              <div class="pending-code">{{ req.account_code }}</div>
            </div>
            <div class="pending-actions">
              <el-button type="success" size="small" @click="acceptFriendRequest(req)">接受</el-button>
              <el-button type="danger" size="small" @click="rejectFriendRequest(req)">拒绝</el-button>
            </div>
          </div>
        </div>
      </div>

      <div class="chat-area">
        <div v-if="!selectedUser" class="chat-empty">
          <div class="empty-icon">💬</div>
          <h3>选择一个好友开始聊天</h3>
          <p>从左侧好友列表选择好友</p>
        </div>

        <div v-else class="chat-room">
          <div class="chat-room-header">
            <el-avatar :size="40" :src="selectedUser.avatar ? `/api/uploads/${selectedUser.avatar}` : ''" icon="User">
              {{ selectedUser.username.charAt(0) }}
            </el-avatar>
            <div class="chat-room-info">
              <div class="chat-room-name">{{ selectedUser.username }}</div>
              <div class="chat-room-code">{{ selectedUser.account_code }}</div>
              <div v-if="!isFriend(selectedUser.id)" class="chat-room-status">
                <span class="status-warning">临时聊天（{{ tempMsgCount }}/5）</span>
              </div>
              <div v-else class="chat-room-status">
                <span class="status-success">已好友</span>
              </div>
            </div>
            <div class="chat-room-actions">
              <el-button circle size="small" @click="clearHistory">🗑</el-button>
            </div>
          </div>

          <div class="chat-messages" ref="messagesContainer">
            <div
              v-for="(msg, index) in messages"
              :key="index"
              class="message-item"
              :class="{ 'self': msg.sender_id === userStore.userInfo.id }"
            >
              <div class="message-avatar">
                <el-avatar :size="32" icon="User">
                  {{ msg.sender.charAt(0) }}
                </el-avatar>
              </div>
              <div class="message-content">
                <div class="message-header">
                  <span class="message-sender">{{ msg.sender }}</span>
                  <span class="message-time">{{ msg.send_time }}</span>
                </div>
                <div class="message-text">{{ msg.content }}</div>
              </div>
            </div>
          </div>

          <div class="chat-input-area">
            <el-input
              v-model="messageInput"
              :placeholder="!isFriend(selectedUser.id) && tempMsgCount >= 5 ? '临时聊天已达上限，请添加好友' : '输入消息...'"
              :disabled="!isFriend(selectedUser.id) && tempMsgCount >= 5"
              @keyup.enter="sendMessage"
              class="message-input"
            />
            <el-button 
              type="primary" 
              @click="sendMessage" 
              :disabled="!messageInput.trim() || (!isFriend(selectedUser.id) && tempMsgCount >= 5)"
            >发送</el-button>
          </div>
        </div>
      </div>
    </div>

    <el-drawer v-model="showUserList" direction="ltr" size="280px" :with-header="false">
      <div class="drawer-content">
        <div class="drawer-header">
          <h3>💬 聊天</h3>
        </div>

        <div class="drawer-tabs">
          <button 
            v-for="tab in tabs" 
            :key="tab.key" 
            :class="['tab-btn', { active: activeTab === tab.key }]"
            @click="activeTab = tab.key"
          >
            {{ tab.label }}
            <span v-if="tab.count > 0" class="tab-badge">{{ tab.count }}</span>
          </button>
        </div>

        <div v-if="activeTab === 'search'" class="search-section">
          <el-input 
            v-model="searchQuery" 
            placeholder="搜索用户名或账号"
            prefix-icon="Search"
            @keyup.enter="doSearch"
            class="search-input"
          />
          <el-button type="primary" @click="doSearch" style="width:100%;margin-top:8px;">搜索</el-button>
          
          <div v-if="searchResults.length > 0" class="search-results">
            <div 
              v-for="user in searchResults" 
              :key="user.id" 
              class="search-item"
            >
              <el-avatar :size="48" :src="user.avatar ? `https://api.118201820.xyz/api/uploads/${user.avatar}` : ''" :icon="!user.avatar ? 'User' : null">
                {{ user.username.charAt(0) }}
              </el-avatar>
              <div class="search-info">
                <div class="search-name">{{ user.username }}</div>
                <div class="search-code">{{ user.account_code }}</div>
              </div>
              <el-button 
                v-if="user.id !== userStore.userInfo.id && !isFriend(user.id) && !isPendingRequest(user.id)" 
                type="primary" 
                size="small" 
                @click="sendFriendRequest(user)"
              >
                添加好友
              </el-button>
              <div v-else-if="isPendingRequest(user.id)" class="pending-tag">等待同意</div>
              <div v-else-if="isFriend(user.id)" class="friend-tag">已好友</div>
              <div v-else-if="user.id === userStore.userInfo.id" class="self-tag">自己</div>
            </div>
          </div>
        </div>

        <div v-else-if="activeTab === 'friends'" class="friends-list">
          <div v-if="friends.length === 0" class="empty-friends">
            <div class="empty-icon">👥</div>
            <p>暂无好友</p>
            <p>去搜索添加好友吧</p>
          </div>
          <div 
            v-for="friend in friends" 
            :key="friend.id" 
            class="friend-item"
            :class="{ active: selectedUserId === friend.id }"
            @click="selectUserAndClose(friend)"
          >
            <div class="friend-avatar">
              <el-avatar :size="48" :src="friend.avatar ? `https://api.118201820.xyz/api/uploads/${friend.avatar}` : ''" :icon="!friend.avatar ? 'User' : null">
                {{ friend.username.charAt(0) }}
              </el-avatar>
            </div>
            <div class="friend-info">
              <div class="friend-name">{{ friend.username }}</div>
              <div class="friend-code">{{ friend.account_code }}</div>
            </div>
          </div>
        </div>

        <div v-else-if="activeTab === 'pending'" class="pending-list">
          <div v-if="pendingRequests.length === 0" class="empty-pending">
            <div class="empty-icon">📭</div>
            <p>暂无待处理请求</p>
          </div>
          <div 
            v-for="req in pendingRequests" 
            :key="req.id" 
            class="pending-item"
          >
            <div class="pending-avatar">
              <el-avatar :size="48" :src="req.avatar ? `https://api.118201820.xyz/api/uploads/${req.avatar}` : ''" :icon="!req.avatar ? 'User' : null">
                {{ req.username.charAt(0) }}
              </el-avatar>
            </div>
            <div class="pending-info">
              <div class="pending-name">{{ req.username }}</div>
              <div class="pending-code">{{ req.account_code }}</div>
            </div>
            <div class="pending-actions">
              <el-button type="success" size="small" @click="acceptFriendRequest(req)">接受</el-button>
              <el-button type="danger" size="small" @click="rejectFriendRequest(req)">拒绝</el-button>
            </div>
          </div>
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import { useUserStore } from '../stores/user';
import axios from '../axios';

const userStore = useUserStore();
const router = useRouter();

const searchQuery = ref('');
const searchResults = ref([]);
const friends = ref([]);
const pendingRequests = ref([]);
const pendingSentRequests = ref([]);
const activeTab = ref('friends');

const selectedUser = ref(null);
const selectedUserId = ref(null);
const messages = ref([]);
const messageInput = ref('');
const messagesContainer = ref(null);
const showUserList = ref(false);
const tempMsgCount = ref(0);

const tabs = computed(() => [
  { key: 'friends', label: '好友', count: friends.value.length },
  { key: 'pending', label: '待处理', count: pendingRequests.value.length },
  { key: 'search', label: '搜索', count: 0 }
]);

const fetchFriends = async () => {
  try {
    const response = await axios.get('/api/friends/list');
    if (response.data.code === 200) {
      friends.value = response.data.data;
    }
  } catch (error) {
    console.error('获取好友列表失败:', error);
  }
};

const fetchPendingRequests = async () => {
  try {
    const response = await axios.get('/api/friends/pending');
    if (response.data.code === 200) {
      pendingRequests.value = response.data.data;
    }
  } catch (error) {
    console.error('获取待处理请求失败:', error);
  }
};

const doSearch = async () => {
  if (!searchQuery.value.trim()) return;
  
  try {
    const response = await axios.get(`/api/users/search?q=${encodeURIComponent(searchQuery.value)}`);
    if (response.data.code === 200) {
      searchResults.value = response.data.data;
    }
  } catch (error) {
    console.error('搜索用户失败:', error);
  }
};

const isFriend = (userId) => {
  return friends.value.some(f => f.id === userId);
};

const isPendingRequest = (userId) => {
  return pendingSentRequests.value.includes(userId);
};

const sendFriendRequest = async (user) => {
  try {
    const response = await axios.post('/api/friends/request', {
      user_id: user.id
    });
    if (response.data.code === 200) {
      ElMessage.success('好友请求已发送');
      if (!pendingSentRequests.value.includes(user.id)) {
        pendingSentRequests.value.push(user.id);
      }
    } else {
      ElMessage.error(response.data.msg || '发送失败');
    }
  } catch (error) {
    ElMessage.error('发送失败');
  }
};

const acceptFriendRequest = async (req) => {
  try {
    const response = await axios.post('/api/friends/accept', {
      user_id: req.id
    });
    if (response.data.code === 200) {
      ElMessage.success('已添加好友');
      fetchFriends();
      fetchPendingRequests();
    } else {
      ElMessage.error(response.data.msg || '操作失败');
    }
  } catch (error) {
    ElMessage.error('操作失败');
  }
};

const rejectFriendRequest = async (req) => {
  try {
    const response = await axios.post('/api/friends/reject', {
      user_id: req.id
    });
    if (response.data.code === 200) {
      ElMessage.success('已拒绝');
      fetchPendingRequests();
    } else {
      ElMessage.error(response.data.msg || '操作失败');
    }
  } catch (error) {
    ElMessage.error('操作失败');
  }
};

const selectUser = (user) => {
  selectedUser.value = user;
  selectedUserId.value = user.id;
  messages.value = [];
  tempMsgCount.value = 0;
  fetchChatHistory(user.id);
};

const selectUserAndClose = (user) => {
  selectUser(user);
  showUserList.value = false;
};

const fetchChatHistory = async (otherId) => {
  try {
    const response = await axios.get(`/api/chat/history/${otherId}`);
    if (response.data.code === 200) {
      messages.value = response.data.data;
      if (!isFriend(otherId)) {
        const selfMsgCount = messages.value.filter(m => m.sender_id === userStore.userInfo.id).length;
        tempMsgCount.value = selfMsgCount;
      }
      scrollToBottom();
    }
  } catch (error) {
    console.error('获取聊天记录失败:', error);
  }
};

const sendMessage = async () => {
  if (!messageInput.value.trim() || !selectedUser.value) return;
  
  if (!isFriend(selectedUser.value.id) && tempMsgCount.value >= 5) {
    ElMessage.warning('临时聊天已达上限，请添加好友');
    return;
  }

  const content = messageInput.value.trim();
  messageInput.value = '';

  try {
    const response = await axios.post('/api/chat/send', {
      receiver_id: selectedUser.value.id,
      content
    });
    if (response.data.code === 200) {
      messages.value.push({
        sender: userStore.userInfo.username,
        sender_id: userStore.userInfo.id,
        content,
        send_time: new Date().toLocaleString()
      });
      if (!isFriend(selectedUser.value.id)) {
        tempMsgCount.value++;
      }
      scrollToBottom();
    } else {
      ElMessage.error(response.data.msg || '发送失败');
    }
  } catch (error) {
    ElMessage.error('发送失败');
  }
};

const scrollToBottom = () => {
  setTimeout(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
    }
  }, 100);
};

const clearHistory = () => {
  messages.value = [];
};

onMounted(() => {
  if (userStore.isLoggedIn) {
    fetchFriends();
    fetchPendingRequests();
  }
});
</script>

<style scoped>
.chat-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 500px;
}

.chat-login-required {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 500px;
  text-align: center;
}

.login-icon {
  font-size: 64px;
  margin-bottom: 20px;
}

.chat-login-required h3 {
  font-size: 20px;
  margin-bottom: 8px;
  color: var(--tieba-blue);
}

.chat-login-required p {
  color: #999;
  margin-bottom: 20px;
}

.mobile-user-list-btn {
  display: none;
}

.chat-main {
  display: flex;
  height: 100%;
  min-height: 500px;
  border: 1px solid var(--tieba-border);
  border-radius: 8px;
  overflow: hidden;
}

.chat-sidebar {
  width: 280px;
  background: #f7f7f7;
  border-right: 1px solid var(--tieba-border);
  display: flex;
  flex-direction: column;
}

.dark .chat-sidebar {
  background: #222;
  border-right-color: #444;
}

.chat-sidebar-header {
  padding: 16px;
  border-bottom: 1px solid var(--tieba-border);
}

.chat-sidebar-header h3 {
  font-size: 16px;
  margin: 0;
  color: var(--tieba-blue);
}

.chat-tabs {
  display: flex;
  padding: 8px;
  gap: 4px;
  border-bottom: 1px solid var(--tieba-border);
}

.tab-btn {
  flex: 1;
  padding: 8px;
  border: none;
  border-radius: 4px;
  background: transparent;
  font-size: 13px;
  cursor: pointer;
  transition: background 0.2s;
  color: #666;
}

.dark .tab-btn {
  color: #ccc;
}

.tab-btn:hover {
  background: rgba(72, 121, 189, 0.1);
}

.tab-btn.active {
  background: rgba(72, 121, 189, 0.2);
  color: var(--tieba-blue);
}

.tab-badge {
  background: #f56c6c;
  color: #fff;
  font-size: 10px;
  padding: 1px 5px;
  border-radius: 10px;
  margin-left: 4px;
}

.search-section {
  padding: 12px;
}

.search-input {
  margin-bottom: 8px;
}

.search-results {
  margin-top: 12px;
}

.search-item {
  display: flex;
  align-items: center;
  padding: 10px;
  border-radius: 6px;
  margin-bottom: 8px;
  background: #fff;
}

.dark .search-item {
  background: #333;
}

.search-info {
  flex: 1;
  margin-left: 12px;
}

.search-name {
  font-size: 14px;
  font-weight: 500;
  color: #333;
}

.dark .search-name {
  color: #fff;
}

.search-code {
  font-size: 12px;
  color: #999;
}

.friend-tag, .self-tag, .pending-tag {
  font-size: 12px;
  padding: 4px 8px;
  border-radius: 4px;
}

.friend-tag {
  background: #e8f5e9;
  color: #2e7d32;
}

.dark .friend-tag {
  background: #1b5e20;
  color: #81c784;
}

.self-tag {
  background: #e3f2fd;
  color: #1565c0;
}

.dark .self-tag {
  background: #0d47a1;
  color: #90caf9;
}

.pending-tag {
  background: #fff3e0;
  color: #e65100;
}

.dark .pending-tag {
  background: #bf360c;
  color: #ffcc80;
}

.friends-list, .pending-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.friend-item {
  display: flex;
  align-items: center;
  padding: 10px;
  cursor: pointer;
  border-radius: 6px;
  margin-bottom: 4px;
  transition: background 0.2s;
}

.friend-item:hover {
  background: rgba(72, 121, 189, 0.1);
}

.friend-item.active {
  background: rgba(72, 121, 189, 0.2);
}

.friend-avatar {
  margin-right: 12px;
}

.friend-info {
  flex: 1;
}

.friend-name {
  font-size: 14px;
  font-weight: 500;
  color: #333;
}

.dark .friend-name {
  color: #fff;
}

.friend-code {
  font-size: 12px;
  color: #999;
}

.empty-friends, .empty-pending {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  text-align: center;
}

.empty-friends .empty-icon, .empty-pending .empty-icon {
  font-size: 48px;
  margin-bottom: 12px;
}

.empty-friends p, .empty-pending p {
  color: #999;
  font-size: 14px;
  margin: 4px 0;
}

.pending-item {
  display: flex;
  align-items: center;
  padding: 10px;
  border-radius: 6px;
  margin-bottom: 8px;
  background: #fff;
}

.dark .pending-item {
  background: #333;
}

.pending-avatar {
  margin-right: 12px;
}

.pending-info {
  flex: 1;
}

.pending-name {
  font-size: 14px;
  font-weight: 500;
  color: #333;
}

.dark .pending-name {
  color: #fff;
}

.pending-code {
  font-size: 12px;
  color: #999;
}

.pending-actions {
  display: flex;
  gap: 4px;
}

.chat-area {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.chat-empty {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: #fff;
}

.dark .chat-empty {
  background: #1a1a1a;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 20px;
}

.chat-empty h3 {
  font-size: 18px;
  margin-bottom: 8px;
  color: #666;
}

.chat-empty p {
  color: #999;
  font-size: 14px;
}

.chat-room {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.chat-room-header {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  background: #f7f7f7;
  border-bottom: 1px solid var(--tieba-border);
}

.dark .chat-room-header {
  background: #222;
  border-bottom-color: #444;
}

.chat-room-info {
  margin-left: 12px;
  flex: 1;
}

.chat-room-name {
  font-size: 15px;
  font-weight: 500;
  color: #333;
}

.dark .chat-room-name {
  color: #fff;
}

.chat-room-code {
  font-size: 12px;
  color: #999;
}

.chat-room-status {
  font-size: 11px;
  margin-top: 2px;
}

.status-warning {
  color: #e6a23c;
}

.status-success {
  color: #67c23a;
}

.chat-room-actions {
  margin-left: auto;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  background: #fff;
}

.dark .chat-messages {
  background: #1a1a1a;
}

.message-item {
  display: flex;
  margin-bottom: 16px;
}

.message-item.self {
  flex-direction: row-reverse;
}

.message-avatar {
  flex-shrink: 0;
  margin-right: 12px;
}

.message-item.self .message-avatar {
  margin-right: 0;
  margin-left: 12px;
}

.message-content {
  max-width: 70%;
}

.message-item.self .message-content {
  text-align: right;
}

.message-header {
  display: flex;
  align-items: center;
  margin-bottom: 4px;
}

.message-item.self .message-header {
  flex-direction: row-reverse;
}

.message-sender {
  font-size: 12px;
  color: #666;
  font-weight: 500;
}

.message-time {
  font-size: 11px;
  color: #bbb;
  margin-left: 8px;
}

.message-item.self .message-time {
  margin-left: 0;
  margin-right: 8px;
}

.message-text {
  padding: 8px 12px;
  border-radius: 8px;
  background: #f0f0f0;
  color: #333;
  font-size: 14px;
  line-height: 1.5;
  word-break: break-word;
}

.dark .message-text {
  background: #333;
  color: #fff;
}

.message-item.self .message-text {
  background: #4879BD;
  color: #fff;
}

.dark .message-item.self .message-text {
  background: #2c5a8a;
}

.chat-input-area {
  display: flex;
  gap: 12px;
  padding: 12px 16px;
  background: #f7f7f7;
  border-top: 1px solid var(--tieba-border);
}

.dark .chat-input-area {
  background: #222;
  border-top-color: #444;
}

.message-input {
  flex: 1;
}

.drawer-content {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.drawer-header {
  padding: 20px;
  border-bottom: 1px solid var(--tieba-border);
}

.drawer-header h3 {
  font-size: 18px;
  margin: 0;
  color: var(--tieba-blue);
}

.drawer-tabs {
  display: flex;
  padding: 8px;
  gap: 4px;
  border-bottom: 1px solid var(--tieba-border);
}

@media (max-width: 768px) {
  .mobile-user-list-btn {
    display: block;
    position: fixed;
    bottom: 20px;
    left: 50%;
    transform: translateX(-50%);
    z-index: 100;
    background: rgba(72, 121, 189, 0.95);
    color: #fff;
    padding: 12px 24px;
    border-radius: 24px;
    font-size: 14px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    cursor: pointer;
  }

  .chat-main {
    flex-direction: column;
    border: none;
    border-radius: 0;
  }

  .chat-sidebar {
    display: none;
  }

  .chat-area {
    height: calc(100vh - 60px);
  }

  .chat-messages {
    flex: 1;
  }

  .message-content {
    max-width: 85%;
  }

  .chat-room-header {
    padding: 10px 12px;
  }

  .chat-input-area {
    padding: 10px 12px;
    gap: 8px;
  }

  .drawer-content {
    padding: 0;
  }

  .drawer-tabs {
    padding: 6px;
  }

  .drawer-tabs .tab-btn {
    padding: 10px 6px;
    font-size: 12px;
  }

  .search-item, .friend-item, .pending-item {
    padding: 12px;
    margin-bottom: 6px;
  }

  .search-avatar, .friend-avatar, .pending-avatar {
    margin-right: 10px;
  }

  .search-info, .friend-info, .pending-info {
    flex: 1;
    min-width: 0;
  }

  .search-name, .friend-name, .pending-name {
    font-size: 14px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .search-code, .friend-code, .pending-code {
    font-size: 11px;
  }

  .pending-actions {
    flex-shrink: 0;
  }

  .pending-actions .el-button {
    padding: 4px 8px;
    font-size: 11px;
  }
}

@media (min-width: 769px) {
  .mobile-user-list-btn {
    display: none;
  }
}
</style>
