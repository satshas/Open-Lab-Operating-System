<template>
  <div class="column full-width bg-grey-4 q-gutter-sm rounded-borders">
    <span class="text-bold" style="font-size: 2vh">Override Settings</span>
    <div class="row q-gutter-sm full-width justify-around">
      <feed-rate />
      <spindle-power />
    </div>
  </div>
</template>
<script setup lang="ts">
import FeedRate from './components/FeedRate.vue';
import SpindlePower from './components/SpindlePower.vue';
</script>
<style>
.button-size {
  font-size: 1.5vh;
  width: 7vh;
  height: 7vh;
  padding: 0.5vh 0.5vh 0.5vh 0.5vh;
}

.small-font {
  font-size: 1.5vh;
}
.large-font {
  font-size: 2vh;
  font-weight: bold;
}
</style>
