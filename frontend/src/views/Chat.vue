<template>
  <div class="chat-container">
    <div v-if="!userStore.isLoggedIn" class="chat-login-required">
      <div class="login-icon">💬</div>
      <h3>请先登录</h3>
      <p>登录后可以与其他用户聊天</p>
      <el-button type="primary" @click="$router.push('/login')">去登录</el-button>
    </div>

    <div v-else class="chat-main">
      <div class="mobile-user-list-btn" @click="showUserList = true">
        ☰ 在线 {{ onlineUsers.length }} 人
      </div>

      <div class="chat-sidebar">
        <div class="chat-sidebar-header">
          <h3>💬 聊天室</h3>
          <div class="online-count">在线 {{ onlineUsers.length }} 人</div>
        </div>
        <div class="chat-users-list">
          <div
            v-for="user in onlineUsers"
            :key="user.id"
            class="user-item"
            :class="{ active: selectedUserId === user.id }"
            @click="selectUser(user)"
          >
            <div class="user-avatar">
              <el-avatar :size="40" :src="user.avatar ? `/api/uploads/${user.avatar}` : ''" icon="User">
                {{ user.username.charAt(0) }}
              </el-avatar>
              <span class="online-dot"></span>
            </div>
            <div class="user-info">
              <div class="user-name">{{ user.username }}</div>
              <div class="user-code">{{ user.account_code }}</div>
            </div>
          </div>
        </div>
      </div>

      <div class="chat-area">
        <div v-if="!selectedUser" class="chat-empty">
          <div class="empty-icon">💬</div>
          <h3>选择一个用户开始聊天</h3>
          <p>点击左侧在线用户列表开始对话</p>
        </div>

        <div v-else class="chat-room">
          <div class="chat-room-header">
            <el-avatar :size="40" :src="selectedUser.avatar ? `/api/uploads/${selectedUser.avatar}` : ''" icon="User">
              {{ selectedUser.username.charAt(0) }}
            </el-avatar>
            <div class="chat-room-info">
              <div class="chat-room-name">{{ selectedUser.username }}</div>
              <div class="chat-room-code">{{ selectedUser.account_code }}</div>
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
              placeholder="输入消息..."
              @keyup.enter="sendMessage"
              class="message-input"
            />
            <el-button type="primary" @click="sendMessage" :disabled="!messageInput.trim()">发送</el-button>
          </div>
        </div>
      </div>
    </div>

    <el-drawer v-model="showUserList" direction="ltr" size="280px" :with-header="false">
      <div class="drawer-user-list">
        <div class="drawer-header">
          <h3>💬 聊天室</h3>
          <div class="online-count">在线 {{ onlineUsers.length }} 人</div>
        </div>
        <div class="drawer-users">
          <div
            v-for="user in onlineUsers"
            :key="user.id"
            class="drawer-user-item"
            :class="{ active: selectedUserId === user.id }"
            @click="selectUserAndClose(user)"
          >
            <div class="drawer-user-avatar">
              <el-avatar :size="48" :src="user.avatar ? `/api/uploads/${user.avatar}` : ''" icon="User">
                {{ user.username.charAt(0) }}
              </el-avatar>
              <span class="online-dot"></span>
            </div>
            <div class="drawer-user-info">
              <div class="drawer-user-name">{{ user.username }}</div>
              <div class="drawer-user-code">{{ user.account_code }}</div>
            </div>
          </div>
          <div v-if="onlineUsers.length === 0" class="drawer-empty">
            <div class="empty-icon">👥</div>
            <p>暂无在线用户</p>
          </div>
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<script setup>import { ref, onMounted, onUnmounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import { useUserStore } from '../stores/user';
import axios from '../axios';
const userStore = useUserStore();
const router = useRouter();
const onlineUsers = ref([]);
const selectedUser = ref(null);
const selectedUserId = ref(null);
const messages = ref([]);
const messageInput = ref('');
const messagesContainer = ref(null);
const showUserList = ref(false);
const fetchOnlineUsers = async () => {
 try {
 const response = await axios.get('/api/users/online');
 if (response.data.code === 200) {
 onlineUsers.value = response.data.data.filter(u => u.id !== userStore.userInfo.id);
 }
 }
 catch (error) {
 console.error('获取在线用户失败:', error);
 }
};
const selectUser = (user) => {
 selectedUser.value = user;
 selectedUserId.value = user.id;
 messages.value = [];
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
 scrollToBottom();
 }
 }
 catch (error) {
 console.error('获取聊天记录失败:', error);
 }
};
const sendMessage = async () => {
 if (!messageInput.value.trim() || !selectedUser.value)
 return;
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
 scrollToBottom();
 }
 else {
 ElMessage.error('发送失败');
 }
 }
 catch (error) {
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
watch(() => userStore.isLoggedIn, (val) => {
 if (val) {
 fetchOnlineUsers();
 }
});
onMounted(() => {
 if (userStore.isLoggedIn) {
 fetchOnlineUsers();
 }
 setInterval(fetchOnlineUsers, 15000);
});
onUnmounted(() => {
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
  width: 260px;
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
  margin: 0 0 8px 0;
  color: var(--tieba-blue);
}

.online-count {
  font-size: 12px;
  color: #666;
}

.chat-users-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.user-item {
  display: flex;
  align-items: center;
  padding: 10px;
  cursor: pointer;
  border-radius: 6px;
  margin-bottom: 4px;
  transition: background 0.2s;
}

.user-item:hover {
  background: rgba(72, 121, 189, 0.1);
}

.user-item.active {
  background: rgba(72, 121, 189, 0.2);
}

.user-avatar {
  position: relative;
  margin-right: 12px;
}

.online-dot {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 12px;
  height: 12px;
  background: #52c41a;
  border-radius: 50%;
  border: 2px solid #fff;
}

.dark .online-dot {
  border-color: #222;
}

.user-info {
  flex: 1;
}

.user-name {
  font-size: 14px;
  font-weight: 500;
  color: #333;
}

.dark .user-name {
  color: #fff;
}

.user-code {
  font-size: 12px;
  color: #999;
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

.drawer-user-list {
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
  margin: 0 0 8px 0;
  color: var(--tieba-blue);
}

.drawer-users {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
}

.drawer-user-item {
  display: flex;
  align-items: center;
  padding: 16px;
  cursor: pointer;
  border-radius: 12px;
  margin-bottom: 8px;
  transition: background 0.2s;
}

.drawer-user-item:hover {
  background: rgba(72, 121, 189, 0.1);
}

.drawer-user-item.active {
  background: rgba(72, 121, 189, 0.2);
}

.drawer-user-avatar {
  position: relative;
  margin-right: 16px;
}

.drawer-user-info {
  flex: 1;
}

.drawer-user-name {
  font-size: 16px;
  font-weight: 500;
  color: #333;
}

.dark .drawer-user-name {
  color: #fff;
}

.drawer-user-code {
  font-size: 13px;
  color: #999;
}

.drawer-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  text-align: center;
}

.drawer-empty .empty-icon {
  font-size: 48px;
  margin-bottom: 12px;
}

.drawer-empty p {
  color: #999;
  font-size: 14px;
}

@media (max-width: 768px) {
  .mobile-user-list-btn {
    display: block;
    position: fixed;
    top: 60px;
    left: 12px;
    z-index: 100;
    background: rgba(72, 121, 189, 0.95);
    color: #fff;
    padding: 10px 16px;
    border-radius: 20px;
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
}

@media (min-width: 769px) {
  .mobile-user-list-btn {
    display: none;
  }
}
</style>
