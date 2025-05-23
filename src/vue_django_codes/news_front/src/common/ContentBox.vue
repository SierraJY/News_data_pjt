<template>
  <div class="box">
    <slot />
  </div>
</template>

<style scoped lang="scss">
.box {
  background-color: white;
  border: 1px solid #eaedf1;
  border-radius: 12px;
  box-shadow:
    0px 2px 6px rgba(0, 0, 0, 0.05),
    0px 1px 3px rgba(0, 0, 0, 0.03);
  width: 100%;
  padding: 20px;
  transition: box-shadow 0.3s ease, background-color 0.3s ease, border-color 0.3s ease;
  
  .dark-mode & {
    background-color: var(--c-card-bg);
    border-color: var(--c-border);
    box-shadow:
      0px 2px 6px rgba(0, 0, 0, 0.15),
      0px 1px 3px rgba(0, 0, 0, 0.1);
  }
  
  &:hover {
    box-shadow:
      0px 4px 12px rgba(0, 0, 0, 0.08),
      0px 2px 6px rgba(0, 0, 0, 0.04);
    
    .dark-mode & {
      box-shadow:
        0px 4px 12px rgba(0, 0, 0, 0.2),
        0px 2px 6px rgba(0, 0, 0, 0.15);
    }
  }
}
</style>
