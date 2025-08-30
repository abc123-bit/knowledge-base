<template>
  <div class="admin-page">
    <h2>用户管理</h2>
    
    <el-table :data="users" style="width: 100%">
      <el-table-column prop="id" label="ID"></el-table-column>
      <el-table-column prop="username" label="用户名"></el-table-column>
      <el-table-column prop="is_admin" label="管理员">
        <template slot-scope="scope">
          <el-tag v-if="scope.row.is_admin" type="success">是</el-tag>
          <el-tag v-else type="info">否</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作">
        <template slot-scope="scope">
          <el-button size="mini" @click="editUser(scope.row)">编辑</el-button>
          <el-button size="mini" type="danger" @click="deleteUser(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script>
export default {
  data() {
    return {
      users: []
    }
  },
  async created() {
    await this.fetchUsers()
  },
  methods: {
    async fetchUsers() {
      try {
        const response = await this.$axios.get('/admin/users', {
          headers: {
            'Authorization': `Bearer ${this.$store.state.token}`
          }
        })
        this.users = response.data
      } catch (error) {
        this.$message.error('获取用户列表失败')
      }
    },
    editUser(user) {
      this.$prompt('修改用户信息', '编辑用户', {
        inputValue: user.username,
        inputPattern: /^[a-zA-Z0-9]{3,20}$/,
        inputErrorMessage: '用户名格式不正确'
      }).then(async ({ value }) => {
        try {
          // 实际应用中调用API更新用户
          user.username = value
          this.$message.success('更新成功')
        } catch (error) {
          this.$message.error('更新失败')
        }
      })
    },
    deleteUser(user) {
      this.$confirm('确定删除此用户?', '警告', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(async () => {
        try {
          // 实际应用中调用API删除用户
          this.users = this.users.filter(u => u.id !== user.id)
          this.$message.success('删除成功')
        } catch (error) {
          this.$message.error('删除失败')
        }
      })
    }
  }
}
</script>