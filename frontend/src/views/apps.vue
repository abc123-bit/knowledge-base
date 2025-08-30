<template>
  <div class="home-container">
    <!-- 顶部导航栏 -->
    <el-header class="app-header">
      <div class="header-left">
        <h1 class="app-title">知识库智能助手</h1>
      </div>
      <div class="header-right">
        <el-dropdown>
          <span class="user-info">
            <el-avatar :src="userAvatar" size="small"></el-avatar>
            <span class="username">{{ username }}</span>
            <i class="el-icon-caret-bottom"></i>
          </span>
          <el-dropdown-menu slot="dropdown">
            <el-dropdown-item @click.native="goToAdmin" v-if="isAdmin">
              <i class="el-icon-s-custom"></i> 管理后台
            </el-dropdown-item>
            <el-dropdown-item @click.native="logout">
              <i class="el-icon-switch-button"></i> 退出登录
            </el-dropdown-item>
          </el-dropdown-menu>
        </el-dropdown>
      </div>
    </el-header>

    <div class="main-content">
      <!-- 左侧知识库管理区域 -->
      <div class="knowledge-section">
        <div class="section-header">
          <h2 class="section-title">知识库管理</h2>
          <el-button 
            type="primary" 
            icon="el-icon-plus" 
            @click="createKB"
            size="small"
            class="create-btn">
            新建
          </el-button>
        </div>
        
        <!-- 知识库选择 -->
        <div class="kb-selector">
          <el-select 
            v-model="currentKb" 
            placeholder="选择知识库" 
            class="kb-dropdown"
            @change="handleKbChange"
            filterable>
            <el-option
              v-for="kb in knowledgeBases"
              :key="kb.id"
              :label="kb.name"
              :value="kb.id">
              <div class="kb-option">
                <span>{{ kb.name }}</span>
                <span class="file-count">{{ kb.file_count }}个文件</span>
              </div>
            </el-option>
          </el-select>
        </div>
        
        <!-- 文件上传区域 -->
        <div class="upload-section" v-if="currentKbDetails">
          <div class="upload-header">
            <h3>上传文件</h3>
            <el-tooltip content="支持PDF、TXT、DOCX格式" placement="top">
              <i class="el-icon-question"></i>
            </el-tooltip>
          </div>
          <FileUpload :kb-id="currentKb" @uploaded="handleUploadSuccess"/>
        </div>
        
        <!-- 知识库文件列表 -->
        <div class="kb-files" v-if="currentKbDetails && currentKbDetails.files && currentKbDetails.files.length > 0">
          <div class="section-header">
            <h3>文件列表</h3>
            <span class="file-count">{{ currentKbDetails.files.length }}个文件</span>
          </div>
          
          <el-scrollbar class="file-list">
            <div 
              v-for="file in currentKbDetails.files" 
              :key="file.id" 
              class="file-item">
              <div class="file-info">
                <i class="el-icon-document" :class="getFileIcon(file.type)"></i>
                <div class="file-details">
                  <div class="file-name">{{ file.name }}</div>
                  <div class="file-meta">
                    <span>{{ formatSize(file.size) }}</span>
                    <span>•</span>
                    <span>{{ formatDate(file.upload_time) }}</span>
                  </div>
                </div>
              </div>
              <el-dropdown trigger="click" class="file-actions">
                <span class="el-dropdown-link">
                  <i class="el-icon-more"></i>
                </span>
                <el-dropdown-menu slot="dropdown">
                  <el-dropdown-item @click.native="downloadFile(file)">
                    <i class="el-icon-download"></i> 下载
                  </el-dropdown-item>
                  <el-dropdown-item @click.native="previewFile(file)" divided>
                    <i class="el-icon-view"></i> 预览
                  </el-dropdown-item>
                  <el-dropdown-item @click.native="deleteFile(file)" divided class="danger-item">
                    <i class="el-icon-delete"></i> 删除
                  </el-dropdown-item>
                </el-dropdown-menu>
              </el-dropdown>
            </div>
          </el-scrollbar>
        </div>
        
        <!-- 空状态 -->
        <div class="empty-state" v-if="knowledgeBases.length === 0">
          
          <p>您还没有创建任何知识库</p>
          <el-button type="primary" @click="createKB">创建第一个知识库</el-button>
        </div>
      </div>

      <!-- 右侧聊天区域 -->
      <div class="chat-section">
        <div class="section-header">
          <h2 class="section-title">智能对话</h2>
          <div class="kb-info" v-if="currentKbDetails">
            <el-tag type="info" size="small">{{ currentKbDetails.name }}</el-tag>
            <el-tooltip content="当前知识库">
              <i class="el-icon-info"></i>
            </el-tooltip>
          </div>
        </div>
        
        <div class="chat-container">
          <div v-if="currentKb" class="chat-wrapper">
            <ChatBox :kb-id="currentKb" class="chat-box"/>
          </div>
          <div v-else class="chat-empty">
            
            <p>请先选择或创建一个知识库开始对话</p>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 知识库编辑对话框 -->
    <el-dialog
      :title="editDialogTitle"
      :visible.sync="editDialogVisible"
      width="30%">
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

import axios from 'axios';

export default {
  name: 'HomePage',
  components: {
    FileUpload,
    ChatBox
  },
  data() {
    return {
      username: '',
      userAvatar: require('@/assets/logo.png'),
      isAdmin: false,
      knowledgeBases: [],
      currentKb: null,
      currentKbDetails: null,
      loading: false,
      editDialogVisible: false,
      editForm: {
        id: null,
        name: '',
        description: ''
      },
      editType: 'create', // 'create' 或 'edit'
      fileTypes: {
        pdf: 'pdf-color',
        txt: 'txt-color',
        doc: 'doc-color',
        docx: 'doc-color'
      }
    };
  },
  computed: {
    editDialogTitle() {
      return this.editType === 'create' ? '新建知识库' : '编辑知识库';
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
        if (user.avatar) {
          this.userAvatar = user.avatar;
        }
      }
    },
    
    async fetchKnowledgeBases() {
      this.loading = true;
      try {
        // API调用获取知识库列表
        const response = await axios.post('http://localhost:8001/login')  // 替换为实际API调用
        
        // 模拟数据
        this.knowledgeBases = [
          { id: 1, name: '产品手册', file_count: 8, description: '包含所有产品手册和说明文档', files: [
            { id: 101, name: '产品使用指南.pdf', type: 'pdf', size: 2456789, upload_time: '2023-06-15T08:30:00Z' },
            { id: 102, name: '安装说明.txt', type: 'txt', size: 12456, upload_time: '2023-06-18T14:20:00Z' }
          ]},
          { id: 2, name: '技术文档', file_count: 12, description: '技术规范和API文档', files: [
            { id: 201, name: 'API接口文档.docx', type: 'docx', size: 3456789, upload_time: '2023-06-20T10:45:00Z' }
          ]},
          { id: 3, name: '客户支持', file_count: 5, description: '常见问题解答和客户支持材料', files: [] }
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
    
    handleKbChange(kbId) {
      this.currentKbDetails = this.knowledgeBases.find(kb => kb.id === kbId) || null;
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
    
    editKB(kb) {
      this.editType = 'edit';
      this.editForm = {
        id: kb.id,
        name: kb.name,
        description: kb.description || ''
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
          files: []
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
    
    deleteKb(kb) {
      this.$confirm(`确定删除知识库 "${kb.name}"? 所有关联文件也将被删除`, '删除确认', {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning',
        confirmButtonClass: 'el-button--danger'
      }).then(() => {
        const kbIndex = this.knowledgeBases.findIndex(k => k.id === kb.id);
        if (kbIndex !== -1) {
          this.knowledgeBases.splice(kbIndex, 1);
          
          if (this.currentKb === kb.id) {
            this.currentKb = this.knowledgeBases.length > 0 ? this.knowledgeBases[0].id : null;
            this.currentKbDetails = this.currentKb ? this.knowledgeBases[0] : null;
          }
          
          this.$message.success('知识库已删除');
        }
      }).catch(() => {});
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
      this.$message.success(`文件"${fileData.filename}"上传成功`);
    },
    
    getFileIcon(fileType) {
      const type = fileType.toLowerCase();
      return this.fileTypes[type] || 'el-icon-document';
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
    
    downloadFile(file) {
      this.$message.info(`开始下载: ${file.name}`);
      // 实际应用中这里应调用API下载文件
    },
    
    previewFile(file) {
      this.$message.info(`预览文件: ${file.name}`);
      // 实际应用中这里应实现文件预览功能
    },
    
    deleteFile(file) {
      this.$confirm(`确定删除文件 "${file.name}"?`, '删除确认', {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        const fileIndex = this.currentKbDetails.files.findIndex(f => f.id === file.id);
        if (fileIndex !== -1) {
          this.currentKbDetails.files.splice(fileIndex, 1);
          this.currentKbDetails.file_count = this.currentKbDetails.files.length;
          this.$message.success('文件已删除');
        }
      }).catch(() => {});
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
  background: linear-gradient(135deg, #1e6bc6 0%, #0d4a9e 100%);
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 24px;
  z-index: 100;
  color: white;
}

.app-title {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
  letter-spacing: 0.5px;
}

.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
  color: white;
}

.username {
  margin-left: 10px;
  margin-right: 6px;
  font-weight: 500;
}

.main-content {
  display: flex;
  flex: 1;
  overflow: hidden;
  padding: 20px;
  gap: 24px;
  background-color: #f0f2f5;
}

.knowledge-section {
  flex: 0 0 380px;
  background-color: #fff;
  border-radius: 10px;
  padding: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.chat-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  background-color: #fff;
  border-radius: 10px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
  overflow: hidden;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 18px;
}

.section-title {
  margin: 0;
  font-size: 1.3rem;
  font-weight: 600;
  color: #1f2d3d;
  display: flex;
  align-items: center;
}

.kb-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.kb-selector {
  margin-bottom: 24px;
}

.kb-dropdown {
  width: 100%;
}

.kb-option {
  display: flex;
  justify-content: space-between;
  width: 100%;
}

.file-count {
  font-size: 0.85rem;
  color: #8492a6;
}

.upload-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.upload-header h3 {
  margin: 0;
  font-size: 1.1rem;
  color: #1f2d3d;
}

.kb-files {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.file-list {
  flex: 1;
  border: 1px solid #ebeef5;
  border-radius: 6px;
  padding: 8px 0;
  max-height: 300px;
}

.file-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 15px;
  border-bottom: 1px solid #f5f7fa;
  transition: background-color 0.2s;
}

.file-item:last-child {
  border-bottom: none;
}

.file-item:hover {
  background-color: #f8fafc;
}

.file-info {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}

.file-details {
  flex: 1;
  min-width: 0;
}

.file-name {
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.file-meta {
  font-size: 0.8rem;
  color: #99a9bf;
  display: flex;
  gap: 6px;
}

.file-actions {
  cursor: pointer;
  padding: 5px;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.file-actions:hover {
  background-color: #f0f2f5;
}

.danger-item {
  color: #f56c6c;
}

.chat-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background-color: #fafbfc;
  border-radius: 8px;
  border: 1px solid #ebeef5;
}

.chat-wrapper {
  flex: 1;
  display: flex;
  height: 100%;
}

.chat-box {
  flex: 1;
  border-radius: 8px;
  overflow: hidden;
}

.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 0;
  text-align: center;
  color: #99a9bf;
}

.chat-empty {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #99a9bf;
}

.empty-image {
  width: 180px;
  height: 180px;
  margin-bottom: 20px;
  opacity: 0.7;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .knowledge-section {
    flex: 0 0 320px;
  }
}

@media (max-width: 992px) {
  .main-content {
    flex-direction: column;
  }
  
  .knowledge-section {
    flex: 0 0 auto;
    margin-bottom: 20px;
    width: 100%;
  }
  
  .file-list {
    max-height: 200px;
  }
}

@media (max-width: 576px) {
  .app-header {
    padding: 0 15px;
  }
  
  .app-title {
    font-size: 1.2rem;
  }
  
  .username {
    display: none;
  }
  
  .main-content {
    padding: 15px;
    gap: 15px;
  }
}
</style>