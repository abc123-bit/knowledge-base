const path = require('path')

module.exports = {
  configureWebpack: {
    resolve: {
      alias: {
        '@': path.resolve(__dirname, 'src'), // 设置别名
        'views': '@/views',
        'components': '@/components'
      }
    }
  },
  lintOnSave: false // 暂时关闭 lint 检查
}