<script setup></script>

<template>
  <div class="footer">
    <div class="footer-content">
      <div class="footer-links">
        <a href="#">이용약관</a>
        <a href="#">개인정보처리방침</a>
        <a href="#">고객지원</a>
      </div>
      <p class="copyright">© 2025 SSAFY NEWS. All rights reserved.</p>
    </div>
  </div>
</template>

<style scoped lang="scss">
.footer {
  margin: 80px 0 0 0;
  padding: 40px 0;
  text-align: center;
  position: relative;
  overflow: hidden;
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 1px;
    background: linear-gradient(90deg, 
      rgba(10, 77, 149, 0) 0%, 
      rgba(10, 77, 149, 0.2) 50%, 
      rgba(10, 77, 149, 0) 100%
    );
    
    .dark-mode & {
      background: linear-gradient(90deg, 
        rgba(30, 136, 229, 0) 0%, 
        rgba(30, 136, 229, 0.2) 50%, 
        rgba(30, 136, 229, 0) 100%
      );
    }
  }
  
  &-content {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 24px;
  }

  &-links {
    margin-bottom: 16px;
    
    a {
      color: var(--c-main);
      text-decoration: none;
      margin: 0 15px;
      font-size: 15px;
      transition: all 0.2s ease;
      position: relative;
      
      .dark-mode & {
        color: var(--c-main-light);
      }
      
      &:hover {
        color: var(--c-accent);
        
        &::after {
          transform: scaleX(1);
        }
      }
      
      &::after {
        content: '';
        position: absolute;
        bottom: -4px;
        left: 0;
        width: 100%;
        height: 1px;
        background: var(--gradient-accent);
        transform: scaleX(0);
        transform-origin: center;
        transition: transform 0.3s ease;
      }
    }
  }

  .copyright {
    font-size: 14px;
    color: #888;
    
    .dark-mode & {
      color: var(--c-gray-500);
    }
  }
}

@media (max-width: 768px) {
  .footer {
    margin-top: 60px;
    padding: 30px 0;
    
    &-links a {
      margin: 0 10px;
      font-size: 14px;
    }
    
    .copyright {
      font-size: 13px;
    }
  }
}
</style>
