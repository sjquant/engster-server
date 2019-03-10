<template>
  <div>
    <div
      style="padding-left:1.6rem; font-size:16px; margin: 3.2rem 0; color: gray"
    >"what you do" 에 대한 검색 결과 (총: 10건)</div>
    <section>
      <LineCard v-for="i in 10" :key="i">
        <template slot="line">
          <a
            href="#"
          >When I saw what you do to Tony Stark on that track how you stepped up to him in front of god and everybody, that was wow!</a>
        </template>
        <template slot="line-info">
          <div>
            <span>IronMan3</span> /
            <span>Film</span>
          </div>
          <div>
            <Tag>#Action</Tag>
            <Tag>#Fantasy</Tag>
            <Tag>#Horror</Tag>
          </div>
        </template>
      </LineCard>
    </section>
  </div>
</template>

<script>
import LineCard from "~/components/common/LineCard.vue";
import Tag from "~/components/common/Tag.vue";

export default {
  components: {
    LineCard,
    Tag
  }
};
</script>

<style lang="scss">
@import "~styles/utils.scss";
.line {
  a {
    &:hover {
      color: $key-color;
      font-weight: 600;
    }
  }
}
</style>

