<template>
  <div class="search-bar-container">
    <input type="text" placeholder="찾고싶은 표현을 입력하세요!">
    <SearchGlass/>
  </div>
</template>

<script>
import SearchGlass from "./SearchGlass.vue";
export default {
  components: {
    SearchGlass
  }
};
</script>

<style lang='scss'>
@import "./MainSearchBar.scss";
</style>