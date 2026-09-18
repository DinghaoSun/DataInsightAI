<template>
  <aside class="sidebar">
    <!-- Logo -->
    <div class="logo-area">
      <div class="logo-icon">D</div>

      <div class="logo-text">
        <div class="logo-title">DataInsightAI</div>
        <div class="logo-subtitle">智能数据分析平台</div>
      </div>
    </div>

    <!-- Navigation -->
    <nav class="nav-menu">
      <div class="nav-section-title">工作台</div>

      <RouterLink to="/" class="nav-item">
        <span class="nav-icon">📊</span>
        <span>数据总览</span>
      </RouterLink>

      <RouterLink to="/datasets" class="nav-item">
        <span class="nav-icon">📁</span>
        <span>数据集</span>
      </RouterLink>
    </nav>

    <!-- Bottom -->
    <div class="sidebar-bottom">
      <div class="project-info">
        <div class="project-dot"></div>

        <div>
          <div class="project-name">DataInsightAI</div>
          <div class="project-version">V1.0</div>
        </div>
      </div>
    </div>
  </aside>
</template>

<style scoped>
.sidebar {
  width: 240px;
  height: 100vh;
  background: #ffffff;
  border-right: 1px solid #eaeaea;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
  flex-shrink: 0;
}

/* Logo */

.logo-area {
  height: 80px;
  display: flex;
  align-items: center;
  padding: 0 20px;
  border-bottom: 1px solid #f0f0f0;
  box-sizing: border-box;
}

.logo-icon {
  width: 38px;
  height: 38px;
  border-radius: 11px;
  background: linear-gradient(135deg, #aa3bff, #7c3aed);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  font-weight: 700;
  margin-right: 11px;
}

.logo-title {
  font-size: 15px;
  font-weight: 700;
  color: #222222;
}

.logo-subtitle {
  font-size: 11px;
  color: #999999;
  margin-top: 3px;
}

/* Navigation */

.nav-menu {
  padding: 24px 14px;
}

.nav-section-title {
  font-size: 11px;
  color: #999999;
  margin: 0 10px 10px;
  letter-spacing: 0.5px;
}

.nav-item {
  height: 44px;
  display: flex;
  align-items: center;
  padding: 0 12px;
  margin-bottom: 6px;
  border-radius: 10px;
  text-decoration: none;
  color: #555555;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s ease;
  box-sizing: border-box;
}

.nav-item:hover {
  background: #f7f3ff;
  color: #7c3aed;
}

.nav-item.router-link-active {
  background: #f3eaff;
  color: #7c3aed;
  font-weight: 600;
}

.nav-icon {
  width: 28px;
  font-size: 17px;
}

/* Bottom */

.sidebar-bottom {
  margin-top: auto;
  padding: 18px;
  border-top: 1px solid #f0f0f0;
}

.project-info {
  display: flex;
  align-items: center;
}

.project-dot {
  width: 9px;
  height: 9px;
  border-radius: 50%;
  background: #22c55e;
  margin-right: 9px;
}

.project-name {
  font-size: 12px;
  font-weight: 600;
  color: #555555;
}

.project-version {
  font-size: 10px;
  color: #aaaaaa;
  margin-top: 2px;
}
</style>