<template>
  <q-card class="row fit" flat bordered>
    <transition
      appear
      enter-active-class="animated fadeIn"
      leave-active-class="animated fadeOut"
    >
      <div v-if="isGcodeError" class="q-pa-md">
        <p class="row fit flex-center message-text">
          {{ Constants.PREVIEWER_GCODE_ERROR_MESSAGE }}
        </p>
      </div>
      <div v-else-if="isGcodeBiggerThanPlatform" class="q-pa-md">
        <p class="row fit flex-center message-text">
          {{ Constants.PREVIEWER_BIG_GCODE_MESSAGE }}
        </p>
      </div>
      <div
        v-else
        ref="graphContainer"
        :style="{
          border: 'solid 1px black',
        }"
        class="row full-width"
      ></div>
    </transition>

    <q-inner-loading :showing="isGraphLoading">
      <q-spinner-gears size="100" color="primary" />
      <p class="loading-text">Please wait...</p>
    </q-inner-loading>
  </q-card>
</template>

<script setup lang="ts">
import { storeToRefs } from 'pinia';
import { Constants } from 'src/constants';
import { useGcodePreviewStore } from 'src/stores/gcode-preview';
import { useMachineStatusStore } from 'src/stores/machine-status';
import { onMounted, ref, watch } from 'vue';
import { Config } from 'src/interfaces/configSettings.interface';
import { configurationSettings } from 'src/services/configuration.loader.service';
import { reset2DGraphControls } from 'src/services/draw.gcode.service/draw.gcode.2D.service';
import { reset3DGraphControls } from 'src/services/draw.gcode.service/draw.gcode.3D.service';

const gcodePreviewStore = useGcodePreviewStore();
const machineStatusStore = useMachineStatusStore();

const config = ref<Config | null>(null);

const {
  graphContainer,
  isGraphLoading,
  isGcodeError,
  isGcodeBiggerThanPlatform,
} = storeToRefs(gcodePreviewStore);

const { machineState } = storeToRefs(machineStatusStore);

// activate/deactivate the drag and drop controls
watch(
  machineState,
  (newMachineState) => {
    if (newMachineState === Constants.IDLE) {
      gcodePreviewStore.activateDragAndDropControls();
    } else {
      gcodePreviewStore.deactivateDragAndDropControls();
    }
  },
  { immediate: true }
);

onMounted(async () => {
  config.value = await configurationSettings();

  // reset the zoom camera
  if (
    config.value?.machine_type === Constants.MACHINE_TYPE.LASER_CUTTER ||
    config.value?.machine_type === Constants.MACHINE_TYPE.VINYL_CUTTER
  ) {
    reset2DGraphControls();
  } else {
    reset3DGraphControls();
  }
  gcodePreviewStore.addGraphElementToGraphContainer();
});
</script>

<style scoped>
.loading-text {
  font-size: 2.5vh;
  padding: 2vh;
  z-index: 1;
}
</style>
