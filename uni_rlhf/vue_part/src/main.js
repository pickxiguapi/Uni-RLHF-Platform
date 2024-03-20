import Vue from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import vuetify from './plugins/vuetify'
import VideoPlayer from 'vue-video-player'
import ViewUI from 'view-design';
import 'view-design/dist/styles/iview.css';
import draw from "./draw";
require('video.js/dist/video-js.css')
require('vue-video-player/src/custom-theme.css')
Vue.use(VideoPlayer)

Vue.config.productionTip = false

new Vue({
  router,
  store,
  vuetify,
  ViewUI,
  render: h => h(App)
}).$mount('#app')
