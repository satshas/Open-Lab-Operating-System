<template>
  <div class="full-width q-pa-lg">
    <div
      :class="{
        disabled:
          machineState === Constants.RUN || machineState === Constants.HOLD,
      }"
    >
      <jobs-files-uploader v-if="config?.remote_file_uploader" />
      <jobs-files-table />
      <jobs-files-buttons />
    </div>
  </div>
</template>

<script setup lang="ts">
import { useMachineStatusStore } from 'src/stores/machine-status';
import { useUSBMonitorStore } from 'src/stores/usb-monitor';
import { useTabsStore } from 'src/stores/active-tab';
import JobsFilesButtons from './components/JobsFilesButtons.vue';
import JobsFilesTable from './components/JobsFilesTable.vue';
import JobsFilesUploader from './components/JobsFilesUploader.vue';
import { storeToRefs } from 'pinia';
import { Constants } from 'src/constants';
import { useRouter } from 'vue-router';
import { onMounted, ref, watch } from 'vue';
import { configurationSettings } from 'src/services/configuration.loader.service';
import { Config } from 'src/interfaces/configSettings.interface';

// Get the Vue Router instance
const router = useRouter();

const config = ref<Config | null>(null);
// Disable the buttons and the file table when the machine is running
const machineStore = useMachineStatusStore();
const tabsStore = useTabsStore();
const usbMonitorStore = useUSBMonitorStore();

const { machineState } = storeToRefs(machineStore);
const { navList } = storeToRefs(tabsStore);
const { isUSBStorageConnected } = storeToRefs(usbMonitorStore);

// Watch for changes in machineState
watch(machineState, (newState) => {
  if (
    (newState === Constants.RUN || newState === Constants.HOLD) &&
    router.currentRoute.value.path !== '/controls'
  ) {
    tabsStore.changeTab(navList.value.controls);
  }
});

watch(isUSBStorageConnected, (newIsUSBStorageConnected) => {
  if (newIsUSBStorageConnected) {
    usbMonitorStore.showJobUSBFilesDialog();
  } else {
    usbMonitorStore.closeJobUSBFilesDialog();
  }
});

onMounted(async () => {
  config.value = await configurationSettings();
});
</script>

<style scoped>
.disabled {
  pointer-events: none;
  opacity: 0.1;
}
</style>
