<template>
  <div class="column q-my-sm flex-center full-width">
    <span class="sub-text-size">Machine Position</span>
    <div class="row full-width justify-evenly">
      <div class="column col-xs-12 col-sm-6 col-md-4 items-center">
        <span class="sub-text-size">X</span
        ><span class="position-metric">{{
          machinePosition?.x?.toFixed(2)
        }}</span>
      </div>
      <div class="column col-xs-12 col-sm-6 col-md-4 items-center">
        <span class="sub-text-size">Y</span
        ><span class="position-metric">{{
          machinePosition?.y?.toFixed(2)
        }}</span>
      </div>
      <div
        v-if="config?.machine_type !== Constants.MACHINE_TYPE.VINYL_CUTTER"
        class="column col-xs-12 col-sm-6 col-md-4 items-center"
      >
        <span class="sub-text-size">Z</span
        ><span class="position-metric">{{
          machinePosition?.z?.toFixed(2)
        }}</span>
      </div>
    </div>
  </div>
  <hr class="full-width" />
</template>

<script setup lang="ts">
import { storeToRefs } from 'pinia';
import { Config } from 'src/interfaces/configSettings.interface';
import { useMachineStatusStore } from 'src/stores/machine-status';
import { Constants } from 'src/constants';

const store = useMachineStatusStore();
const { machinePosition } = storeToRefs(store);

defineProps<{
  config: Config | null;
}>();
</script>
<style scoped>
.position-metric {
  font-size: 2vh;
  font-weight: 500;
}
</style>
