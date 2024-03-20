const { defineConfig } = require('@vue/cli-service')
module.exports = defineConfig({
  publicPath:'./',
  transpileDependencies: [
    'vuetify'
  ],
  devServer: { historyApiFallback: true}
  // devServer: {
  //   port:8502
    // proxy: {
    //   '/api': {
    //     target: 'http://127.0.0.1:5001',
    //     changeOrigin: true,
    //     pathRewrite: {
    //       '^/api': '', 
    //     },
    //   },
    // },
  // },
})
