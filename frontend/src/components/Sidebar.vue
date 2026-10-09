<template>
  <aside class="sidebar">
    <!-- Logo -->
    <div class="logo-area">
      <div class="logo-symbol">△<small>DIA</small></div>
    </div>

    <!-- Navigation -->
    <nav class="nav-menu">
      <RouterLink to="/" class="nav-item">
        <span class="nav-icon">⌂</span><span>总览</span>
      </RouterLink>

      <RouterLink to="/datasets" class="nav-item">
        <span class="nav-icon">▣</span><span>数据集</span>
      </RouterLink>
      <RouterLink to="/datasets" class="nav-item"><span class="nav-icon">⌁</span><span>分析</span></RouterLink>
      <RouterLink to="/datasets" class="nav-item"><span class="nav-icon">◉</span><span>洞察</span></RouterLink>
      <RouterLink to="/datasets" class="nav-item"><span class="nav-icon">⚙</span><span>设置</span></RouterLink>
    </nav>

    <!-- Bottom -->
    <div class="sidebar-bottom">
      <div class="project-info"><div class="project-dot"></div><div><div class="project-name">DIA 精灵</div></div></div>
    </div>
  </aside>
</template>

<style scoped>
.sidebar {
  width: 124px;
  min-width: 124px;
  max-width: 124px;
  flex: 0 0 124px;
  height: 100vh;
  background: #ffffff;
  border-right: 1px solid #edf0fa;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
  flex-shrink: 0;
}

/* Logo */

.logo-area {
  height: 128px; display:flex;
  align-items: center;
  justify-content:center; padding:0;
  box-sizing: border-box;
}

.logo-symbol{font-size:48px;font-weight:800;color:#6748ee;line-height:.7;text-align:center}.logo-symbol small{display:block;color:#394873;font-size:16px;letter-spacing:1px;margin-top:10px}

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
  padding: 22px 12px;
}

.nav-section-title {
  font-size: 11px;
  color: #999999;
  margin: 0 10px 10px;
  letter-spacing: 0.5px;
}

.nav-item {
  height: 48px;
  display: flex;
  align-items: center;
  padding: 0 12px;
  margin-bottom: 6px;
  border-radius: 10px;
  text-decoration: none;
  color: #566486;
  font-size: 13px;
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
  width: 26px;font-size: 19px;
}

/* Bottom */

.sidebar-bottom {
  margin-top: auto;
  padding: 16px 12px;
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
