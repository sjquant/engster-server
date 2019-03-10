<template>
  <div>
    <h1>{{$route.params.keyword}}</h1>
  </div>
</template>

<script>
import { mapActions } from "vuex";

export default {
  created() {
    this.FETCH_LINE_KOREAN(this.$route.params.keyword);
  },
  methods: {
    ...mapActions({
      FETCH_LINE_KOREAN: "lines/FETCH_LINE_KOREAN"
    })
  }
};
</script>
