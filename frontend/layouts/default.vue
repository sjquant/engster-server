<template>
  <div>
    <MainHead/>
    <div class="container">
      <SideContentContainer>
        <div></div>
      </SideContentContainer>
      <MainContentContainer>
        <nuxt/>
      </MainContentContainer>
      <SideContentContainer>
        <div></div>
      </SideContentContainer>
    </div>
  </div>
</template>

<script>
import MainHead from "~/components/MainNav/MainHead.vue";
import MainContentContainer from "~/components/MainContentContainer/MainContentContainer.vue";
import SideContentContainer from "~/components/SideContentContainer/SideContentContainer.vue";
export default {
  components: {
    MainHead,
    MainContentContainer,
    SideContentContainer
  }
};
</script>

<style lang="scss" scoped>
.container {
  display: flex;
}
</style>


