<template>
  <div class="knowledge-base">
    <h2>知识库管理</h2>
    
    <el-button type="primary" @click="createKB">创建知识库</el-button>
    
    <div v-if="currentKb" class="kb-container">
      <h3>当前知识库: {{ currentKb.name }}</h3>
      
      <FileUpload :kb-id="currentKb.id" @uploaded="onUploaded"/>
      
      <div class="chat-container">
        <ChatBox :kb-id="currentKb.id"/>
      </div>
    </div>
  </div>
</template>

<script>
import FileUpload from '@/components/FileUpload.vue'
import ChatBox from '@/components/ChatBox.vue'

export default {
  components: { FileUpload, ChatBox },
  data() {
    return {
      kbs: [],
      currentKb: null
    }
  },
  async created() {
    await this.fetchKBs()
    if (this.kbs.length > 0) {
      this.currentKb = this.kbs[0]
    }
  },
  methods: {
    async fetchKBs() {
      try {
        const response = await this.$axios.get('/knowledge/list', {
          headers: {
            'Authorization': `Bearer ${this.$store.state.token}`
          }
        })
        this.kbs = response.data
      } catch (error) {
        this.$message.error('获取知识库失败')
      }
    },
    async createKB() {
      const name = prompt('请输入知识库名称:')
      if (name) {
        try {
          const response = await this.$axios.post('/knowledge/create', { name }, {
            headers: {
              'Authorization': `Bearer ${this.$store.state.token}`
            }
          })
          this.kbs.push(response.data)
          this.currentKb = response.data
        } catch (error) {
          this.$message.error('创建知识库失败')
        }
      }
    },
    onUploaded() {
      this.$message.success('文件处理完成！')
    }
  }
}
</script>