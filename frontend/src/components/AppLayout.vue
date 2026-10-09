<template>
  <div class="app-layout">
    <Sidebar />

    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import Sidebar from './Sidebar.vue'
</script>

<style>
* {
  box-sizing: border-box;
}

html,
body,
#app {
  margin: 0;
  padding: 0;
  width: 100%;
  height: 100%;
  min-height: 100%;
}

body {
  background: #f7f7fb;
  font-family:
    Inter,
    -apple-system,
    BlinkMacSystemFont,
    "Segoe UI",
    sans-serif;
}

.app-layout {
  width: 100%;
  max-width: none;
  min-width: 0;
  min-height: 100vh;
  display: flex;
  background: #f7f7fb;
}

.main-content {
  flex: 1;
  flex-basis: 0;
  width: auto;
  min-width: 0;
  min-height: 100vh;
  overflow-x: hidden;
}
</style>
