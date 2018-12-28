<template>
  <span class="tag">
    <slot></slot>
  </span>
</template>

<style lang="scss" scoped>
@import "~styles/utils.scss";
.tag {
  border-radius: 3px;
  border: 1px solid $gray;
  background-color: $gray-lighter;

  color: $gray-dark;
  padding: 0 0.4rem;
  font-size: 1.4rem;

  &:hover {
    cursor: pointer;
  }

  &:active {
    background-color: $gray;
    color: $gray-lighter;
  }
}
</style>
