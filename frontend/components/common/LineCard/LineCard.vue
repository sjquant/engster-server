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
import Like from "../icons/like.vue";
import Pencil from "../icons/Pencil.vue";
import Share from "../icons/Share.vue";
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
@import "./LineCard.scss";
</style>
