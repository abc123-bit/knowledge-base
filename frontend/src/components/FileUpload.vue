<template>
  <div class="file-upload">
    <el-upload
      action="#"
      :multiple="true"
      :show-file-list="true"
      :http-request="handleUpload"
      :file-list="fileList">
      <el-button size="small" type="primary">选择文件</el-button>
      <div slot="tip" class="el-upload__tip">支持PDF、TXT、DOCX格式</div>
    </el-upload>
  </div>
</template>

<script>
export default {
  props: ['kbId'],
  data() {
    return {
      fileList: []
    }
  },
  methods: {
    async handleUpload(file) {
      const formData = new FormData()
      formData.append('file', file.file)
      
      try {
        const response = await this.$axios.post(`/upload?kb_id=${this.kbId}`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
            'Authorization': `Bearer ${this.$store.state.token}`
          }
        })
        
        this.$message.success(`上传成功: ${file.file.name}`)
        this.$emit('uploaded', response.data.filename)
      } catch (error) {
        this.$message.error(`上传失败: ${error.response?.data?.detail || error.message}`)
      }
    }
  }
}
</script>