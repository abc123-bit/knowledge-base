<template>
  <div class="home-container">
    <!-- 顶部导航栏 -->
    <div class="app-header">
      <div class="header-content">
        <div class="logo-section">
          <span class="logo-icon">📚</span>
          <h1 class="app-title">智能知识库助手</h1>
        </div>
        
        <div class="search-section">
          <el-select v-model="searchScope" class="scope-select" size="small">
            <el-option label="全部" value="all"></el-option>
            <el-option label="知识库" value="kb"></el-option>
            <el-option label="文件" value="files"></el-option>
          </el-select>
          <el-input
            v-model="globalSearch"
            placeholder="搜索知识库内容..."
            class="global-search"
            size="small"
            clearable
          >
            <template #prefix>
              <i class="el-icon-search"></i>
            </template>
          </el-input>
        </div>
        
        <div class="user-section">
          <el-dropdown>
            <div class="user-info">
              <el-avatar :size="32" :src="userAvatar"></el-avatar>
              <span class="username">{{ username }}</span>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="goToProfile">
                  <i class="el-icon-user"></i> 个人中心
                </el-dropdown-item>
                <el-dropdown-item @click="goToAdmin" v-if="isAdmin">
                  <i class="el-icon-settings"></i> 管理后台
                </el-dropdown-item>
                <el-dropdown-item divided @click="logout">
                  <i class="el-icon-switch-button"></i> 退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>
    </div>

    <div class="main-content">
      <!-- 左侧知识库管理区域 -->
      <div class="sidebar">
        <div class="sidebar-header">
          <h2>知识库</h2>
          <el-button 
            type="primary" 
            icon="el-icon-plus" 
            @click="createKB"
            size="small"
            class="create-btn">
            新建
          </el-button>
        </div>
        
        <div class="search-box">
          <el-input
            placeholder="搜索知识库..."
            prefix-icon="el-icon-search"
            v-model="kbSearchQuery"
            clearable
            size="small"
          ></el-input>
        </div>
        
        <div class="kb-list">
          <div 
            v-for="kb in filteredKnowledgeBases" 
            :key="kb.id" 
            class="kb-item"
            :class="{ active: currentKb === kb.id }"
            @click="selectKb(kb)">
            <div class="kb-icon">
              <i class="el-icon-folder"></i>
            </div>
            <div class="kb-info">
              <div class="kb-name">{{ kb.name }}</div>
              <div class="kb-desc">{{ kb.description || '暂无描述' }}</div>
              <div class="kb-meta">
                <span class="file-count">{{ kb.file_count }}个文件</span>
                <span class="update-time">更新于{{ formatRelativeTime(kb.update_time) }}</span>
              </div>
            </div>
          </div>
        </div>
        
        <div class="empty-state" v-if="knowledgeBases.length === 0">
          <div class="empty-icon">📁</div>
          <p class="empty-text">您还没有创建任何知识库</p>
          <el-button type="primary" @click="createKB">创建知识库</el-button>
        </div>
      </div>

      <!-- 中间聊天区域 -->
      <div class="chat-area">
        <div class="chat-header">
          <div class="current-kb-info" v-if="currentKbDetails">
            <div class="kb-badge">
              <i class="el-icon-folder"></i>
              <span>{{ currentKbDetails.name }}</span>
            </div>
            <el-tag size="small">
              {{ currentKbDetails.file_count }}个文件
            </el-tag>
          </div>
        </div>
        
        <div class="chat-container">
          <div class="welcome-screen" v-if="!currentChatId">
            <div class="welcome-content">
              <div class="welcome-icon">💬</div>
              <h2>欢迎使用智能知识库助手</h2>
              <p>选择或创建一个知识库开始智能对话</p>
              <div class="suggested-questions">
                <div 
                  v-for="(question, index) in suggestedQuestions" 
                  :key="index" 
                  class="question-card"
                  @click="askSuggestedQuestion(question.text)">
                  {{ question.text }}
                </div>
              </div>
            </div>
          </div>
          
          <div class="chat-main" v-else>
            <!-- 使用ChatBox组件 -->
            <ChatBox :kb-id="currentKb" ref="chatBox" class="chat-box"/>
          </div>
        </div>
        
        <div class="input-area">
          <div class="input-container">
            <el-input
              v-model="userMessage"
              placeholder="输入问题或@知识库进行提问"
              @keyup.enter.native="sendMessage"
              class="message-input"
            >
              <template #append>
                <el-button 
                  icon="el-icon-s-promotion" 
                  @click="sendMessage"
                  :disabled="!userMessage.trim()"
                ></el-button>
              </template>
            </el-input>
          </div>
          <div class="input-options">
            <el-select v-model="selectedModel" size="small" placeholder="模型">
              <el-option label="DeepSeek V3" value="deepseek-v3"></el-option>
              <el-option label="GPT-4" value="gpt-4"></el-option>
              <el-option label="Claude 3" value="claude-3"></el-option>
            </el-select>
            <el-switch
              v-model="webSearchEnabled"
              active-text="联网搜索"
              size="small">
            </el-switch>
          </div>
        </div>
      </div>

      <!-- 右侧文件管理区域 -->
      <div class="file-sidebar">
        <div class="sidebar-header">
          <h2>文件管理</h2>
          <el-button 
            type="primary" 
            icon="el-icon-upload" 
            @click="showUploadDialog"
            size="small"
            :disabled="!currentKb"
          >
            上传
          </el-button>
        </div>
        
        <div class="file-list">
          <div 
            v-for="file in currentKbDetails.files" 
            :key="file.id" 
            class="file-item"
            @dblclick="previewFile(file)">
            <div class="file-icon">
              <i class="el-icon-document"></i>
            </div>
            <div class="file-info">
              <div class="file-name">{{ file.name }}</div>
              <div class="file-meta">
                <span>{{ formatSize(file.size) }}</span>
                <span>•</span>
                <span>{{ formatDate(file.upload_time) }}</span>
              </div>
            </div>
            <div class="file-actions">
              <el-tooltip content="预览">
                <el-button icon="el-icon-view" circle size="mini" @click="previewFile(file)"></el-button>
              </el-tooltip>
              <el-tooltip content="下载">
                <el-button icon="el-icon-download" circle size="mini" @click="downloadFile(file)"></el-button>
              </el-tooltip>
            </div>
          </div>
        </div>
        
        <div class="empty-state" v-if="!currentKbDetails.files || currentKbDetails.files.length === 0">
          <div class="empty-icon">📄</div>
          <p class="empty-text">当前知识库暂无文件</p>
          <el-button type="primary" @click="showUploadDialog">上传文件</el-button>
        </div>
      </div>
    </div>
    
    <!-- 上传文件对话框 -->
    <el-dialog
      title="上传文件"
      :visible.sync="uploadDialogVisible"
      width="500px">
      <FileUpload :kb-id="currentKb" @uploaded="handleUploadSuccess"/>
    </el-dialog>
    
    <!-- 知识库编辑对话框 -->
    <el-dialog
      :title="editDialogTitle"
      :visible.sync="editDialogVisible"
      width="500px">
      <el-form :model="editForm" label-width="80px">
        <el-form-item label="名称">
          <el-input v-model="editForm.name" autocomplete="off"></el-input>
        </el-form-item>
        <el-form-item label="描述">
          <el-input 
            type="textarea" 
            v-model="editForm.description" 
            :autosize="{ minRows: 2, maxRows: 4 }"
            placeholder="请输入知识库描述"></el-input>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmEdit">确 定</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import FileUpload from '@/components/FileUpload.vue';
import ChatBox from '@/components/ChatBox.vue';

export default {
  name: 'HomePage',
  components: {
    FileUpload,
    ChatBox
  },
  data() {
    return {
      username: '管理员',
      userAvatar: '',
      isAdmin: false,
      knowledgeBases: [],
      currentKb: null,
      currentKbDetails: null,
      currentChatId: null,
      kbSearchQuery: '',
      globalSearch: '',
      searchScope: 'all',
      loading: false,
      editDialogVisible: false,
      uploadDialogVisible: false,
      userMessage: '',
      selectedModel: 'deepseek-v3',
      webSearchEnabled: false,
      editForm: {
        id: null,
        name: '',
        description: ''
      },
      editType: 'create',
      suggestedQuestions: [
        { text: '关于劳动争议案件适用法律的最新解释' },
        { text: '撰写一个「新闻价值」的名词解释' },
        { text: '分手了，恋爱期间的赠与还能要回吗?' }
      ]
    };
  },
  computed: {
    editDialogTitle() {
      return this.editType === 'create' ? '新建知识库' : '编辑知识库';
    },
    filteredKnowledgeBases() {
      if (!this.kbSearchQuery) {
        return this.knowledgeBases;
      }
      return this.knowledgeBases.filter(kb => 
        kb.name.toLowerCase().includes(this.kbSearchQuery.toLowerCase()) ||
        (kb.description && kb.description.toLowerCase().includes(this.kbSearchQuery.toLowerCase()))
      );
    }
  },
  created() {
    this.initUserData();
    this.fetchKnowledgeBases();
  },
  methods: {
    initUserData() {
      const userData = localStorage.getItem('user');
      if (userData) {
        const user = JSON.parse(userData);
        this.username = user.username || '管理员';
        this.isAdmin = user.is_admin || false;
      }
    },
    
    async fetchKnowledgeBases() {
      this.loading = true;
      try {
        // 模拟API调用获取知识库列表
        await new Promise(resolve => setTimeout(resolve, 800));
        
        // 模拟数据
        this.knowledgeBases = [
          { 
            id: 1, 
            name: '法律法规知识库', 
            file_count: 8, 
            description: '关于劳动争议案件适用法律的最新解释',
            update_time: '2023-06-15T08:30:00Z',
            files: [
              { id: 101, name: '劳动法解释.pdf', type: 'pdf', size: 2456789, upload_time: '2023-06-15T08:30:00Z' },
              { id: 102, name: '劳动合同范本.docx', type: 'docx', size: 12456, upload_time: '2023-06-18T14:20:00Z' }
            ]
          },
          { 
            id: 2, 
            name: '新闻传播学资料库', 
            file_count: 12, 
            description: '撰写一个「新闻价值」的名词解释',
            update_time: '2023-06-20T10:45:00Z',
            files: [
              { id: 201, name: '新闻学理论.pdf', type: 'pdf', size: 3456789, upload_time: '2023-06-20T10:45:00Z' }
            ]
          },
          { 
            id: 3, 
            name: '公益法律援助智库', 
            file_count: 5, 
            description: '分手了，恋爱期间的赠与还能要回吗?',
            update_time: '2023-06-22T16:15:00Z',
            files: []
          }
        ];
        
        if (this.knowledgeBases.length > 0 && !this.currentKb) {
          this.currentKb = this.knowledgeBases[0].id;
          this.currentKbDetails = this.knowledgeBases[0];
        }
      } catch (error) {
        this.$message.error('获取知识库失败: ' + (error.message || '未知错误'));
      } finally {
        this.loading = false;
      }
    },
    
    selectKb(kb) {
      this.currentKb = kb.id;
      this.currentKbDetails = kb;
      this.currentChatId = null;
    },
    
    createKB() {
      this.editType = 'create';
      this.editForm = {
        id: null,
        name: '',
        description: ''
      };
      this.editDialogVisible = true;
    },
    
    confirmEdit() {
      if (!this.editForm.name.trim()) {
        this.$message.warning('请输入知识库名称');
        return;
      }
      
      if (this.editType === 'create') {
        // 创建新知识库
        const newKb = {
          id: Date.now(),
          name: this.editForm.name,
          description: this.editForm.description,
          file_count: 0,
          files: [],
          update_time: new Date().toISOString()
        };
        
        this.knowledgeBases.push(newKb);
        this.currentKb = newKb.id;
        this.currentKbDetails = newKb;
        this.$message.success(`知识库"${newKb.name}"创建成功`);
      } else {
        // 编辑现有知识库
        const kbIndex = this.knowledgeBases.findIndex(kb => kb.id === this.editForm.id);
        if (kbIndex !== -1) {
          this.knowledgeBases[kbIndex].name = this.editForm.name;
          this.knowledgeBases[kbIndex].description = this.editForm.description;
          
          if (this.currentKb === this.editForm.id) {
            this.currentKbDetails = this.knowledgeBases[kbIndex];
          }
          
          this.$message.success('知识库更新成功');
        }
      }
      
      this.editDialogVisible = false;
    },
    
    handleUploadSuccess(fileData) {
      if (!this.currentKbDetails.files) {
        this.currentKbDetails.files = [];
      }
      
      this.currentKbDetails.files.push({
        id: Date.now(),
        name: fileData.filename,
        type: fileData.type || 'unknown',
        size: fileData.size || 0,
        upload_time: new Date().toISOString()
      });
      
      this.currentKbDetails.file_count = this.currentKbDetails.files.length;
      this.uploadDialogVisible = false;
      this.$message.success(`文件"${fileData.filename}"上传成功`);
    },
    
    formatSize(bytes) {
      if (bytes === 0) return '0 B';
      const k = 1024;
      const sizes = ['B', 'KB', 'MB', 'GB'];
      const i = Math.floor(Math.log(bytes) / Math.log(k));
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },
    
    formatDate(dateString) {
      const date = new Date(dateString);
      return `${date.getFullYear()}-${(date.getMonth()+1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')}`;
    },
    
    formatRelativeTime(dateString) {
      const date = new Date(dateString);
      const now = new Date();
      const diffTime = Math.abs(now - date);
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
      
      if (diffDays === 1) return '今天';
      if (diffDays === 2) return '昨天';
      if (diffDays < 7) return `${diffDays}天前`;
      if (diffDays < 30) return `${Math.floor(diffDays / 7)}周前`;
      return this.formatDate(dateString);
    },
    
    downloadFile(file) {
      this.$message.info(`开始下载: ${file.name}`);
    },
    
    previewFile(file) {
      this.$message.info(`预览文件: ${file.name}`);
    },
    
    showUploadDialog() {
      if (!this.currentKb) {
        this.$message.warning('请先选择一个知识库');
        return;
      }
      this.uploadDialogVisible = true;
    },
    
    sendMessage() {
      if (!this.userMessage.trim()) return;
      
      // 如果没有当前对话，创建一个新的
      if (!this.currentChatId) {
        this.currentChatId = 'chat_' + Date.now();
      }
      
      // 通过ref调用ChatBox组件的sendMessage方法
      if (this.$refs.chatBox) {
        this.$refs.chatBox.sendMessage(this.userMessage);
      }
      
      this.userMessage = '';
    },
    
    askSuggestedQuestion(question) {
      this.userMessage = question;
      this.sendMessage();
    },
    
    goToProfile() {
      this.$message.info('打开个人中心');
    },
    
    goToAdmin() {
      this.$router.push('/admin');
    },
    
    logout() {
      this.$confirm('确定要退出登录吗?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'info'
      }).then(() => {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        
        if (this.$store) {
          this.$store.commit('setToken', null);
          this.$store.commit('setUser', null);
        }
        
        this.$router.push('/login');
        this.$message.success('您已成功退出登录');
      }).catch(() => {});
    }
  }
};
</script>

<style scoped>
.home-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: #f5f7fa;
}

.app-header {
  background: #fff;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  padding: 0 20px;
}

.header-content {
  display: flex;
  align-items: center;
  height: 60px;
  justify-content: space-between;
}

.logo-section {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-icon {
  font-size: 24px;
}

.app-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #1f2d3d;
}

.search-section {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1;
  max-width: 500px;
  margin: 0 40px;
}

.scope-select {
  width: 100px;
}

.global-search {
  flex: 1;
}

.user-section .user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 6px;
  transition: background-color 0.2s;
}

.user-section .user-info:hover {
  background-color: #f5f7fa;
}

.username {
  font-weight: 500;
}

.main-content {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.sidebar {
  width: 320px;
  background: #fff;
  border-right: 1px solid #eaeef2;
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #eaeef2;
}

.sidebar-header h2 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
}

.search-box {
  padding: 16px;
  border-bottom: 1px solid #eaeef2;
}

.kb-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.kb-item {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  border-radius: 8px;
  margin-bottom: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.kb-item:hover {
  background-color: #f5f7fa;
}

.kb-item.active {
  background-color: #ecf5ff;
}

.kb-icon {
  margin-right: 12px;
  color: #5e7ce0;
  font-size: 18px;
}

.kb-info {
  flex: 1;
}

.kb-name {
  font-weight: 500;
  margin-bottom: 4px;
  color: #1f2d3d;
}

.kb-desc {
  font-size: 13px;
  color: #87909d;
  margin-bottom: 6px;
}

.kb-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: #99a9bf;
}

.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  text-align: center;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.empty-text {
  font-size: 14px;
  color: #99a9bf;
  margin-bottom: 20px;
}

.chat-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  background-color: #fafbfc;
}

.chat-header {
  display: flex;
  align-items: center;
  padding: 16px 24px;
  border-bottom: 1px solid #eaeef2;
  background-color: #fff;
}

.kb-badge {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  background-color: #f0f5ff;
  border-radius: 16px;
  color: #1e6bc6;
  font-size: 14px;
}

.chat-container {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.welcome-screen {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.welcome-content {
  text-align: center;
  max-width: 500px;
}

.welcome-icon {
  font-size: 64px;
  margin-bottom: 20px;
}

.welcome-content h2 {
  margin-bottom: 12px;
  color: #1f2d3d;
}

.welcome-content p {
  color: #99a9bf;
  margin-bottom: 32px;
}

.suggested-questions {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.question-card {
  border: 1px solid #eaeef2;
  border-radius: 8px;
  padding: 16px;
  background: #fff;
  cursor: pointer;
  transition: all 0.2s;
  text-align: left;
}

.question-card:hover {
  border-color: #b3d8ff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.input-area {
  padding: 16px 24px;
  background-color: #fff;
  border-top: 1px solid #eaee;
}

.input-container {
  margin-bottom: 12px;
}

.input-options {
  display: flex;
  align-items: center;
  gap: 12px;
}

.file-sidebar {
  width: 320px;
  background: #fff;
  border-left: 1px solid #eaeef2;
  display: flex;
  flex-direction: column;
}

.file-list {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.file-item {
  display: flex;
  align-items: center;
  padding: 12px;
  border-radius: 8px;
  margin-bottom: 8px;
  transition: background-color 0.2s;
}

.file-item:hover {
  background-color: #f5f7fa;
}

.file-icon {
  margin-right: 12px;
  color: #5e7ce0;
  font-size: 20px;
}

.file-info {
  flex: 1;
}

.file-name {
  font-weight: 500;
  margin-bottom: 4px;
}

.file-meta {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #99a9bf;
}

.file-actions {
  opacity: 0;
  transition: opacity 0.2s;
}

.file-item:hover .file-actions {
  opacity: 1;
}

@media (max-width: 1200px) {
  .sidebar, .file-sidebar {
    width: 280px;
  }
}

@media (max-width: 992px) {
  .file-sidebar {
    display: none;
  }
}

@media (max-width: 768px) {
  .sidebar {
    position: absolute;
    left: -280px;
    z-index: 1000;
    height: 100%;
    transition: left 0.3s;
    box-shadow: 2px 0 8px rgba(0, 0, 0, 0.1);
  }
  
  .sidebar.open {
    left: 0;
  }
  
  .search-section {
    display: none;
  }
}
</style>