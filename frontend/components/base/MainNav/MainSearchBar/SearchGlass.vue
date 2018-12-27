<template>
  <svg
    enable-background="new 0 0 96 96"
    id="magnifying_glass"
    class="search-glass"
    version="1.1"
    viewBox="0 0 96 96"
    xml:space="preserve"
    xmlns="http://www.w3.org/2000/svg"
    xmlns:xlink="http://www.w3.org/1999/xlink"
    @click="onClick"
  >
    <path
      d="M90.63,84.971l-22.5-22.5C73.05,56.311,76,48.5,76,40C76,20.12,59.88,4,40,4S4,20.12,4,40  s16.12,36,36,36c8.5,0,16.311-2.95,22.471-7.87l22.5,22.5c0.779,0.78,1.812,1.17,2.829,1.17c1.021,0,2.05-0.39,2.83-1.17  C92.189,89.07,92.189,86.529,90.63,84.971z M40,68c-15.464,0-28-12.536-28-28s12.536-28,28-28s28,12.536,28,28S55.464,68,40,68z"
      id="_x3C_Path_x3E_"
      fill="#b8c2cc"
    ></path>
  </svg>
</template>

<script>
export default {
  methods: {
    onClick() {
      this.$emit("click");
    }
  }
};
</script>

