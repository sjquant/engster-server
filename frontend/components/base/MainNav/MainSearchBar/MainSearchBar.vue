<template>
  <div class="search-bar-container">
    <input type="text" placeholder="찾고싶은 표현을 입력하세요!">
    <SearchGlass @click="sayHi"/>
  </div>
</template>

<script>
import SearchGlass from "./SearchGlass.vue";
export default {
  components: {
    SearchGlass
  },
  methods: {
    sayHi() {
      console.log("Hi");
    }
  }
};
</script>

<style lang='scss'>
@import "./MainSearchBar.scss";
</style>