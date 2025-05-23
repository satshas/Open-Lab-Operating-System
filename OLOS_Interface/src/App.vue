<template>
  <router-view />
</template>

<script setup lang="ts">
import { storeToRefs } from 'pinia';
import { useJobsFilesManagementStore } from './stores/jobs-files-management';
import { useGcodePreviewStore } from './stores/gcode-preview';
import { useMachineStatusStore } from './stores/machine-status';
import { useWebSocketStore } from './stores/websocket-connection';
import { onBeforeMount, watch } from 'vue';
import { showNotifyMessage } from './services/notify.messages.service';
import { Constants } from 'src/constants';

const jobManagerStore = useJobsFilesManagementStore();
const gcodePreviewStore = useGcodePreviewStore();
const machineStatusStore = useMachineStatusStore();
const websocketStore = useWebSocketStore();
const notifyMessage = showNotifyMessage();

const { fileData } = storeToRefs(jobManagerStore);
const { machineState } = storeToRefs(machineStatusStore);

onBeforeMount(() => {
  // Connect to WebSocket when component is mounted
  websocketStore.connect(process.env.WEBSOCKET_URL || '');

  // check the opened file in the system
  jobManagerStore
    .checkOpenFile()
    .catch((error) => notifyMessage.error(error.message));
});

// create gcode previewer graph
watch(
  () => fileData.value.fileContent,
  (newFileContent) => {
    gcodePreviewStore.createGcodePreviewerGraph(newFileContent).then(() => {
      // incase the machine running while creating the gcode preview
      if (machineState.value !== Constants.IDLE) {
        gcodePreviewStore.deactivateDragAndDropControls();
      }
    });
  },
  { deep: true }
);
</script>
<style lang="scss">
.q-dialog__backdrop {
  backdrop-filter: blur(3px);
}
</style>
