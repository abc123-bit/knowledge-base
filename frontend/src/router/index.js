import Vue from 'vue'
import Router from 'vue-router'
import Login from '@/views/Login.vue'
import KnowledgeBase from '@/views/KnowledgeBase.vue'
import Admin from '@/views/Admin.vue'
import Apps from '@/views/apps.vue'

Vue.use(Router)

export default new Router({
  mode: 'history',
  base: process.env.BASE_URL,
  routes: [
    {
      path: '/',
      redirect: '/login'
    },
    {
      path: '/login',
      name: 'Login',
      component: Login
    },
    {
      path: '/apps',
      name: 'Apps',
      component: Apps
    },
    {
      path: '/knowledge-base',
      name: 'KnowledgeBase',
      component: KnowledgeBase,
      meta: { requiresAuth: true }
    },
    {
      path: '/admin',
      name: 'Admin',
      component: Admin,
      meta: { requiresAuth: true, requiresAdmin: true }
    }
  ],

  
})