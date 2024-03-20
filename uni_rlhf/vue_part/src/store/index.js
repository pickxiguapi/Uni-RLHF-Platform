import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)


const savedState = localStorage.getItem('vuex-state');
const initialState = savedState ? JSON.parse(savedState) : {
  baseUrl:'http://43.132.253.84:6002',
  username:'',
  password:'',
  email:'',
  url_doc:'',
  url_github:'',
};


const store = new Vuex.Store({
  state: initialState,
  getters: {
  },
  mutations: {
    setUsername(state, username) {
      state.username = username;
    },
    setEmail(state, email) {
      state.email = email;
    },
    setPassword(state, p) {
      state.password = p;
    },
    setDocUrl(state, p) {
      state.url_doc = p;
    },
    setGithubUrl(state, p) {
      state.url_github = p;
    }
  },
  actions: {
  },
  modules: {
  }
})
store.subscribe((mutation, state) => {
  localStorage.setItem('vuex-state', JSON.stringify(state));
});

export default store;