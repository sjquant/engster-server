<template>
  <div class="main-logo-container">
    <MainMobileLogo/>
    <MainFullLogo/>
  </div>
</template>

<script>
import MainMobileLogo from "./MainMobileLogo.vue";
import MainFullLogo from "./MainFullLogo.vue";

export default {
  components: {
    MainMobileLogo,
    MainFullLogo
  }
};
</script>

<style lang='scss'>
@import "~styles/utils.scss";
.main-logo-container {
  min-width: 5.6rem;
  padding-left: 1.6rem;
  padding-right: 1.6rem;
  display: flex;
  align-items: center;

  @include media(">=lg") {
    width: 16rem;
  }

  .main-mobile-logo {
    width: 2.4rem;
    cursor: pointer;
    @include media(">=lg") {
      width: 0;
      height: 0;
    }
  }

  .main-full-logo {
    display: none;
    cursor: pointer;
    @include media(">=lg") {
      display: block;
      width: 16rem;
      height: 16rem * 0.27;
    }
  }
}
</style>
