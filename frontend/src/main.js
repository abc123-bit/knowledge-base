import Vue from 'vue'
import App from '@/App.vue'
import router from '@/router'
import store from '@/store'
import ElementUI from 'element-ui'
import 'element-ui/lib/theme-chalk/index.css'

Vue.use(ElementUI)

Vue.config.productionTip = false

// 添加路由守卫
router.beforeEach((to, from, next) => {
  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (!store.state.isAuthenticated) {
      next({
        path: '/login',
        query: { redirect: to.fullPath }
      })
    } else if (to.matched.some(record => record.meta.requiresAdmin) && !store.getters.isAdmin) {
      next({ path: '/kb' })
    } else {
      next()
    }
  } else {
    next()
  }
})

new Vue({
  router,
  store,
  render: h => h(App)
}).$mount('#app')