<template>
    <div class="login-container">
        <el-form :model="loginForm" class="login-form" :rules="rules" ref="loginForm"
            @submit.native.prevent="handleLogin">
            <h2 class="login-title">知识库系统登录</h2>
            <el-form-item prop="username">
                <el-input v-model="loginForm.username" placeholder="用户名" prefix-icon="el-icon-user" clearable>
                </el-input>
            </el-form-item>
            <el-form-item prop="password">
                <el-input v-model="loginForm.password" type="password" placeholder="密码" prefix-icon="el-icon-lock"
                    show-password>
                </el-input>
            </el-form-item>
            <el-form-item>
                <el-checkbox v-model="rememberMe">记住我</el-checkbox>
            </el-form-item>
            <el-form-item>
                <el-button type="primary" native-type="submit" class="login-button" :loading="loading" round>
                    登录
                </el-button>
            </el-form-item>
            <div class="login-links">
                <a href="#" @click.prevent="forgotPassword">忘记密码?</a>
                <a href="#" @click.prevent="registerAccount">注册账号</a>
            </div>
        </el-form>
    </div>
</template>

<script>
import axios from 'axios';

export default {
    name: 'Login',
    data() {
        return {
            loginForm: {
                username: '',
                password: ''
            },
            rememberMe: false,
            loading: false,
            rules: {
                username: [
                    { required: true, message: '请输入用户名', trigger: 'blur' }
                ],
                password: [
                    { required: true, message: '请输入密码', trigger: 'blur' },
                    { min: 6, message: '密码长度不能少于6个字符', trigger: 'blur' }
                ]
            }
        };
    },
    methods: {
        async handleLogin() {
            this.$refs.loginForm.validate(async (valid) => {
                if (!valid) {
                    this.$message.error('请填写正确的登录信息');
                    return false;
                }

                this.loading = true;
                try {
                    const response = await axios.post('http://localhost:8001/knowledge/list', this.loginForm);

                    // 确保响应包含 token 和 user 数据
                    if (response.data && response.data.token) {
                        // 安全地设置 token
                        localStorage.setItem('token', response.data.token);

                        // 确保 user 数据有效
                        const userData = response.data.user || {};
                        localStorage.setItem('user', JSON.stringify(userData));

                        // 提交到 Vuex store
                        if (this.$store && this.$store.commit) {
                            this.$store.commit('setToken', response.data.token);
                            this.$store.commit('setUser', userData);
                        }

                        this.$message.success('登录成功');
                        this.$router.push('/apps');
                    } else {
                        this.$message.error('登录失败：服务器响应无效');
                    }
                } catch (error) {
                    // 增强错误处理
                    let errorMessage = '登录请求失败，请稍后重试';

                    if (error.response) {
                        if (error.response.status === 401) {
                            errorMessage = '用户名或密码错误';
                        } else if (error.response.data && error.response.data.detail) {
                            errorMessage = error.response.data.detail;
                        }
                    } else if (error.request) {
                        errorMessage = '无法连接到服务器';
                    }

                    this.$message.error(errorMessage);
                } finally {
                    this.loading = false;
                }
            });
        },
        forgotPassword() {
            this.$prompt('请输入您的邮箱', '重置密码', {
                confirmButtonText: '发送重置邮件',
                cancelButtonText: '取消',
                inputPattern: /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/,
                inputErrorMessage: '邮箱格式不正确'
            }).then(({ value }) => {
                this.$message.success(`重置密码链接已发送至: ${value}`);
            }).catch(() => { });
        },
        registerAccount() {
            this.$message.info('注册功能即将开放');
        }
    }
};
</script>

<style scoped>
.login-container {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.login-form {
    width: 400px;
    padding: 30px;
    background: #fff;
    border-radius: 8px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.login-title {
    text-align: center;
    margin-bottom: 30px;
    color: #303133;
    font-weight: 600;
}

.login-button {
    width: 100%;
    margin-top: 10px;
}

.login-links {
    display: flex;
    justify-content: space-between;
    margin-top: 15px;
}

.login-links a {
    color: #606266;
    text-decoration: none;
    font-size: 14px;
}

.login-links a:hover {
    color: #409EFF;
}
</style>