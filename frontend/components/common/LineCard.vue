<template>
  <div class="line-card-container">
    <section class="content-container">
      <div class="line">
        <slot name="line"></slot>
      </div>
      <div class="line-info">
        <slot name="line-info"></slot>
      </div>
      <div class="line-action-container">
        <div class="action-box">
          <Like/>
          <span>{{numLike}}</span>
        </div>
        <div class="action-box">
          <Pencil/>
          <span>{{numTrans}}</span>
        </div>
        <div class="action-box">
          <Share/>
          <span>{{numShare}}</span>
        </div>
      </div>
    </section>
  </div>
</template>

<script>
import Like from "./icons/like.vue";
import Pencil from "./icons/Pencil.vue";
import Share from "./icons/Share.vue";
export default {
  components: {
    Like,
    Pencil,
    Share
  },
  props: {
    numLike: {
      type: Number,
      default: 0
    },
    numTrans: {
      type: Number,
      default: 0
    },
    numShare: {
      type: Number,
      default: 0
    }
  }
};
</script>

<style lang="scss">
@import "~styles/utils.scss";
.line-card-container {
  border-bottom: 1px solid $gray-light;
  min-height: 8rem;
  padding-top: 4rem;

  &:first-child {
    padding-top: 0;
  }

  &:last-child {
    margin-bottom: 4rem;
  }

  .content-container {
    padding-left: 1.6rem;
    padding-right: 1.6rem;
  }

  .line-info {
    padding-top: 1.6rem;
    padding-bottom: 2.4em;
    color: $gray-dark;
  }

  .line-action-container {
    padding-bottom: 1.6rem;
    display: flex;

    .action-box {
      margin-right: 3.2rem;
      color: #8795a1;
      display: flex;
      align-items: center;

      &:last-child {
        margin-right: 0;
      }

      &:hover {
        cursor: pointer;
      }

      > span {
        padding-left: 0.8rem;
      }
    }
  }
}
</style>
