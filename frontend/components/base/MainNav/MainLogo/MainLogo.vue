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
@import "./MainLogo.scss";
</style>
