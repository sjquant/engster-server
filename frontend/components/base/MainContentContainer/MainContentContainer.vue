<template>
  <section class="main-content-container">
    <slot></slot>
  </section>
</template>

<style lang="scss">
@import "~styles/utils.scss";

.main-content-container {
  width: 100%;
  margin-left: 1.6rem;
  margin-right: 1.6rem;
  @include media(">=lg") {
    width: 60%;
    margin-left: 0;
    margin-right: 0;
  }
}
</style>

