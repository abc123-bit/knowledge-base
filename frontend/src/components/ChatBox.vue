<template>
  <div class="chat-box">
    <div class="messages">
      <div v-for="(msg, index) in messages" :key="index" :class="['message', msg.role]">
        {{ msg.content }}
      </div>
    </div>
    
    <div class="input-area">
      <el-input v-model="input" placeholder="输入问题..." @keyup.enter="sendMessage"></el-input>
      <el-button type="primary" @click="sendMessage">发送</el-button>
    </div>
  </div>
</template>

<script>
export default {
  props: ['kbId'],
  data() {
    return {
      input: '',
      messages: [],
      eventSource: null
    }
  },
  methods: {
    sendMessage() {
      if (!this.input.trim()) return
      
      const question = this.input
      this.input = ''
      
      // 添加用户消息
      this.messages.push({ role: 'user', content: question })
      
      // 创建新消息占位符
      this.messages.push({ role: 'assistant', content: '' })
      const messageIndex = this.messages.length - 1
      
      // 连接SSE
      if (this.eventSource) this.eventSource.close()
      
      this.eventSource = new EventSource(
        `${this.$axios.defaults.baseURL}/ask?kb_id=${this.kbId}&question=${encodeURIComponent(question)}`,
        { withCredentials: true }
      )
      
      this.eventSource.onmessage = (event) => {
        this.messages[messageIndex].content += event.data
      }
      
      this.eventSource.onerror = () => {
        this.eventSource.close()
      }
    }
  },
  beforeDestroy() {
    if (this.eventSource) this.eventSource.close()
  }
}
</script>

<style scoped>
.chat-box {
  border: 1px solid #eee;
  border-radius: 5px;
  padding: 15px;
  height: 500px;
  display: flex;
  flex-direction: column;
}

.messages {
  flex: 1;
  overflow-y: auto;
  margin-bottom: 15px;
}

.message {
  padding: 10px;
  margin-bottom: 10px;
  border-radius: 5px;
}

.message.user {
  background-color: #f0f7ff;
  text-align: right;
}

.message.assistant {
  background-color: #f9f9f9;
}

.input-area {
  display: flex;
}

.input-area .el-input {
  flex: 1;
  margin-right: 10px;
}
</style>