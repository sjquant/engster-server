<template>
  <div class="line-card-container">
    <div class="line">
      <slot name="line"></slot>
    </div>
    <div class="line-info">
      <slot name="line-info"></slot>
    </div>
  </div>
</template>
<style lang="scss">
@import "~styles/utils.scss";
.line-card-container {
  border-bottom: 1px solid $gray-light;
  min-height: 8rem;
  padding-top: 4rem;
  padding-bottom: 4rem;

  &:first-child {
    padding-top: 0;
  }

  &:last-child {
    margin-bottom: 4rem;
  }

  .line {
    padding-left: 1.6rem;
    padding-right: 1.6rem;
  }

  .line-info {
    padding-top: 0.8em;
    padding-left: 1.6rem;
    color: $gray-dark;
    font-size: 1.6rem;
  }
}
</style>
