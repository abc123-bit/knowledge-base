module.exports = {
  presets: [
    [
      '@vue/cli-plugin-babel/preset',
      {
        useBuiltIns: 'entry',
        corejs: 3,
        requireConfigFile: false // 解决 "No Babel config file detected" 错误
      }
    ]
  ]
}