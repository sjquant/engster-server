<template>
  <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" class="sidebar-open">
    <path
      class="heroicon-ui"
      d="M4 5h16a1 1 0 0 1 0 2H4a1 1 0 1 1 0-2zm0 6h16a1 1 0 0 1 0 2H4a1 1 0 0 1 0-2zm0 6h16a1 1 0 0 1 0 2H4a1 1 0 0 1 0-2z"
      fill="#b8c2cc"
    ></path>
  </svg>
</template>

<style lang="scss">
@import "~styles/utils.scss";
.sidebar-open {
  width: 2.4rem;
  height: 2.4rem;
  cursor: pointer;

  @include media(">=lg") {
    display: none;
  }
}
</style>
