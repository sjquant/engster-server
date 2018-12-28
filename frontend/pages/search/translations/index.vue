<template>
  <div>
    <h1>{{$route.query.line}}</h1>
  </div>
</template>

<script>
export default {
  created() {
    console.log(this.$route.query.line);
  }
};
</script>
