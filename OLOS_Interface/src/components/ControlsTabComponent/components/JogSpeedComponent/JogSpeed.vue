<template>
  <div
    class="column col-lg-3 col-md-3 col-sm-12 col-xs-12 q-gutter-sm bg-grey-4 rounded-borders q-pb-sm"
  >
    <span class="text-bold" style="font-size: 2vh">Jog speed (mm/s)</span>
    <div class="column col justify-center q-gutter-y-md q-pb-sm">
      <xy-jog-speed :is-disabled="machineState !== Constants.IDLE" />
      <z-jog-speed
        v-if="config?.machine_type !== Constants.MACHINE_TYPE.VINYL_CUTTER"
        :is-disabled="machineState !== Constants.IDLE"
      />
    </div>
  </div>
</template>
<script setup lang="ts">
import xyJogSpeed from './components/XYJogSpeed.vue';
import ZJogSpeed from './components/ZJogSpeed.vue';
import { storeToRefs } from 'pinia';
import { Constants } from 'src/constants';
import { Config } from 'src/interfaces/configSettings.interface';
import { useMachineStatusStore } from 'src/stores/machine-status';

const machineStatusStore = useMachineStatusStore();

const { machineState } = storeToRefs(machineStatusStore);

defineProps<{
  config: Config | null;
}>();
</script>

<style>
.axis-title {
  font-weight: bold;
  font-size: 1.5vh;
}
.group-button-width {
  width: 30%;
  font-size: 1.2vh;
  height: fit-content;
}
</style>
