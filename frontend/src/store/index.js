import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

export default new Vuex.Store({
  state: {
    // 安全地获取 localStorage 中的数据
    token: localStorage.getItem('token') || '',
    user: (() => {
      try {
        const userStr = localStorage.getItem('user')
        return userStr ? JSON.parse(userStr) : {}
      } catch (e) {
        console.error('解析用户数据失败:', e)
        return {}
      }
    })(),
    isAuthenticated: !!localStorage.getItem('token')
  },
  mutations: {
    setToken(state, token) {
      state.token = token
      // 安全地存储到 localStorage
      try {
        localStorage.setItem('token', token)
      } catch (e) {
        console.error('存储 token 失败:', e)
      }
    },
    setUser(state, user) {
      state.user = user
      // 安全地存储到 localStorage
      try {
        localStorage.setItem('user', JSON.stringify(user))
      } catch (e) {
        console.error('存储用户数据失败:', e)
      }
    },
    logout(state) {
      state.token = ''
      state.user = {}
      state.isAuthenticated = false
      // 安全地移除 localStorage 中的数据
      try {
        localStorage.removeItem('token')
        localStorage.removeItem('user')
      } catch (e) {
        console.error('清除存储失败:', e)
      }
    }
  },
  actions: {
    login({ commit }, { token, user }) {
      commit('setToken', token)
      commit('setUser', user)
    },
    logout({ commit }) {
      commit('logout')
    }
  },
  getters: {
    isAdmin: state => state.user.is_admin || false
  }
})