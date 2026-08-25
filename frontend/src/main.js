import { createApp } from 'vue'
import App from './App.vue'
import './theme.css'

function readTheme() {
  try {
    const stored = localStorage.getItem('theme')
    if (stored === 'dark' || stored === 'light') {
      return stored
    }
  } catch (error) {
    // Ignore storage errors.
  }

  try {
    return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
  } catch (error) {
    return 'light'
  }
}

const savedTheme = readTheme()
document.documentElement.setAttribute('data-theme', savedTheme)

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
