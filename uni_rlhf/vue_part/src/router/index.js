import Vue from 'vue'
import VueRouter from 'vue-router'
import Login from '../views/Login.vue'
import Homepage from '../views/Homepage.vue'
import Project from '../views/Project.vue'
import Comparative from '../views/Comparative.vue'
import Attribute from '../views/Attribute.vue'
import Keypoint from '../views/Keypoint.vue'
import Evaluative from '../views/Evaluative.vue'
import Visual from '../views/Visual.vue'

Vue.use(VueRouter)

const routes = [
  {
    path: '/',
    name: 'home',
    component: Login
  },
  {
    path: '/homepage',
    name: 'homepage',
    component: Homepage
  },  
  {
    path: '/project',
    name: 'project',
    component: Project
  },
  {
    path: '/comparative',
    name: 'comparative',
    component: Comparative,
    props:true
  },
  {
    path: '/attribute',
    name: 'attribute',
    component: Attribute,
    props:true
  },
  {
    path: '/keypoint',
    name: 'keypoint',
    component: Keypoint,
    props:true
  },
  {
    path: '/evaluative',
    name: 'evaluative',
    component: Evaluative,
    props:true
  },
  {
    path: '/visual',
    name: 'visual',
    component: Visual,
    props:true
  },
]

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
})

export default router
