<template>
<div id="sidebar" class="ui left vertical menu thin sidebar">
  <a class="item" href="/m">
    首页
  </a>
</div>
<div id="menu" class="ui inverted fixed menu" v-if="config.menu">
  <div class="header item" @click="toggleSidebar">
    <i class="content icon no-margin"></i>
  </div>
  <a class="header ui borderless item" href="/m">
    <img src="/static/logo.png" class="logo" />
  </a>
  <div class="right menu">
    <div class="borderless item">
      <div class="ui buttons">
        <a href="/m/login" class="ui button login">登录</a>
        <div class="or"></div>
        <a href="/signup" class="ui button login">注册</a>
      </div>
    </div>
  </div>
</div>
<div id="float-menu" class="ui black right attached big fixed button" v-if="config.floatMenu" @click="toggleSidebar">
  <i class="content icon"></i>
</div>
<div id="page" class="pusher">
    <div class="page">
      <slot></slot>
    </div>
</div>
</template>

<script>
export default {
  data () {
    return {
    }
  },
  props: ['reset'],
  computed: {
    config (){
      var _config = {
        menu: true,
        floatMenu: false
      };

      return this.$utils.update(_config, this.reset); 
    }
  },
  components: {
  },
  methods: {
    toggleSidebar (){
      this.sideBar.sidebar('toggle');
    }
  },
  ready (){
    this.sideBar = this.$utils.$('#sidebar');
    this.menu = this.$utils.$('#menu');
    this.page = this.$utils.$('#page');

    var that = this;
    this.$utils.$(window).load(function(){
      that.page.css('margin-top', that.menu.height());
    });
  }
}
</script>

<style lang="sass">
@import "../assets/sass/ws-base.scss";
html.ios {
  overflow-x: hidden;
  -webkit-overflow-scrolling: touch;
}
html.ios,
html.ios body {
  height: initial !important;
}
#sidebar {
  font-size: rem(20);
}
#menu {
  font-size: rem(16);
  .logo {
    width: 2.5rem;
  }
  .login:hover{
  color:#fff;
  background:#ffc700;
  }
}
#float-menu {
  z-index: 10;
  display: block;
  position: fixed;
  top: rem(62);
  left: rem(0);
  white-space: nowrap;
  overflow: hidden;
  font-size: rem(20);
  padding: rem(16) rem(24);
  opacity: 0.38;
  i.icon {
    margin: 0;
  }
  &:hover {
    opacity: 1;
  }
}
#page {
}
</style>
