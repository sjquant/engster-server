<template>
  <div class="search-bar-container">
    <input
      id="main-search-bar"
      type="text"
      placeholder="찾고싶은 표현을 입력하세요!"
      @keyup.enter="onEnterSearch"
    >
    <SearchGlass @click="onClickSearch"/>
  </div>
</template>

<script>
import SearchGlass from "./SearchGlass.vue";
export default {
  components: {
    SearchGlass
  },
  methods: {
    onClickSearch() {
      let searchLine = document.querySelector("#main-search-bar").value;
      this.search(searchLine);
    },
    onEnterSearch(e) {
      let searchLine = e.target.value;
      this.search(searchLine);
    },
    search(searchLine) {
      if (searchLine.length < 2) {
        // doNothing
        return;
      }
      let krCheck = /[ㄱ-ㅎ|ㅏ-ㅣ|가-힣]/;
      if (krCheck.test(searchLine)) {
        this.$router.push({
          path: "/search/translations",
          query: { line: searchLine }
        });
      } else {
        this.$router.push({
          path: "/search/expressions",
          query: { line: searchLine }
        });
      }
    }
  }
};
</script>

<style lang='scss'>
@import "./MainSearchBar.scss";
</style>