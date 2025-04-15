<template>
  <div class="column q-pa-sm bg-white full-width job-box">
    <file-info :config />

    <q-separator class="q-my-md" />

    <machine-info :config />
  </div>
</template>

<script setup lang="ts">
import { Config } from 'src/interfaces/configSettings.interface';
import FileInfo from './components/FileInfo.vue';
import MachineInfo from './components/MachineInfo.vue';
import { Constants } from 'src/constants';

defineProps<{
  config: Config | null;
}>();
</script>

<style scoped>
.job-box {
  border-radius: 10px;
}
.sub-text-size {
  font-size: 1.5vh;
}
</style>
