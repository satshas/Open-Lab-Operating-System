<template>
  <div
    class="column col-lg col-md col-sm-12 col-xs-12 bg-grey-4 rounded-borders q-pa-sm"
  >
    <span class="text-bold" style="font-size: 2vh">Jog Step Size(mm)</span>
    <div class="row justify-between metrics-box">
      <span>0.1</span>
      <span>1</span>
      <span>10</span>
      <span>100</span>
    </div>
    <div class="row col">
      <div class="col-1">
        <x-y-lock-button :is-disabled="machineState !== Constants.IDLE" />
      </div>
      <div class="row col items-center">
        <x-step-slider :is-disabled="machineState !== Constants.IDLE" />
        <y-step-slider :is-disabled="machineState !== Constants.IDLE" />
        <z-step-slider
          v-if="config?.machine_type !== Constants.MACHINE_TYPE.VINYL_CUTTER"
          :is-disabled="machineState !== Constants.IDLE"
        />
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
import XStepSlider from './components/XStepSlider.vue';
import YStepSlider from './components/YStepSlider.vue';
import ZStepSlider from './components/ZStepSlider.vue';
import XYLockButton from './components/XYLockButton.vue';

import { storeToRefs } from 'pinia';
import { Constants } from 'src/constants';
import { useMachineStatusStore } from 'src/stores/machine-status';
import { Config } from 'src/interfaces/configSettings.interface';

const machineStatusStore = useMachineStatusStore();

const { machineState } = storeToRefs(machineStatusStore);

defineProps<{
  config: Config | null;
}>();
</script>

<style>
.metrics-box {
  position: relative;
  left: 13%;
  max-width: 60%;
  font-weight: bold;
}

.slider-width {
  max-width: 65%;
}
.sub-text-size {
  font-size: 1.5vh;
}
</style>
