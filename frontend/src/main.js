import { createApp } from 'vue'
import App from './App.vue'
import './theme.css'

// Theme is locked to light mode only
document.documentElement.setAttribute('data-theme', 'light')

const app = createApp(App)
app.mount('#app')

window.addEventListener('load', function () {
  setTimeout(function () {
    var ls = document.getElementById('loading-screen')
    if (ls) {
      ls.classList.add('fade-out')
      setTimeout(function () {
        ls.remove()
      }, 500)
    }
    document.body.style.overflow = 'auto'
  }, 800)
})
