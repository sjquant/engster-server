<template>
  <div class="main-head-container">
    <MainLogo/>
  </div>
</template>
<script>
import MainLogo from "./MainLogo.vue";
export default {
  components: {
    MainLogo
  }
};
</script>

<style lang="scss">
@import "~styles/utils.scss";

.main-head-container {
  border-bottom: 1px solid $gray-light;
  height: 5.6rem;
}
</style>
