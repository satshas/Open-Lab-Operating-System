<template>
  <div class="row fititems-center justify-between">
    <div class="row q-gutter-x-md col-lg col-md col-sm-12 col-xs-12">
      <q-btn
        icon="file_open"
        label="Open Job"
        text-color="black"
        :color="isFileSelected ? 'grey-4' : 'blue-grey-2'"
        :disable="!isFileSelected"
        @click="handleOpenFile"
        size="2vh"
        class="q-mb-md"
      />
      <q-btn
        icon="edit_square"
        label="Rename Job"
        text-color="black"
        :color="isFileSelected ? 'grey-4' : 'blue-grey-2'"
        :disable="!isFileSelected"
        @click="handleRenameFile"
        size="2vh"
        class="q-mb-md"
      />
    </div>
    <div
      class="row col-lg-5 col-md-5 col-sm-12 col-xs-12"
      :class="{
        'justify-end': $q.screen.gt.sm,
      }"
    >
      <q-btn
        v-if="isUSBStorageConnected"
        icon="usb"
        label="Check USB Jobs Files"
        text-color="black"
        color="grey-4"
        size="2vh"
        @click="usbMonitorStore.showJobUSBFilesDialog"
        class="q-mb-md"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { useJobsFilesManagementStore } from 'src/stores/jobs-files-management';
import { useUSBMonitorStore } from 'src/stores/usb-monitor';
import { storeToRefs } from 'pinia';
import { useQuasar } from 'quasar';
import { showNotifyMessage } from 'src/services/notify.messages.service';
import { Constants } from 'src/constants';
import RenameFileDialog from 'src/components/CustomDialogs/RenameFileDialog.vue';
const $q = useQuasar();

const notifyMessage = showNotifyMessage();
const jobManagerStore = useJobsFilesManagementStore();
const usbMonitorStore = useUSBMonitorStore();

const { filesListData, selectedFilename, isFileSelected } =
  storeToRefs(jobManagerStore);
const { isUSBStorageConnected } = storeToRefs(usbMonitorStore);

// fastapi calls
const handleOpenFile = () => {
  jobManagerStore
    .openFile()
    .then(async () => {
      notifyMessage.success(Constants.API_SUCCESS_MESSAGES.OPEN_MESSAGE);
    })
    .catch((error) => {
      notifyMessage.error(error.message);
    });
};

const handleRenameFile = () => {
  $q.dialog({
    component: RenameFileDialog,
    componentProps: {
      filesListData: filesListData.value,
      filename: selectedFilename.value,
      renameJob,
    },
  });
};

const renameJob = (newFilename: string) => {
  jobManagerStore
    .renameFile(selectedFilename.value, newFilename)
    .then(() => {
      notifyMessage.success(Constants.API_SUCCESS_MESSAGES.RENAME_MESSAGE);
    })
    .catch((error) => {
      notifyMessage.error(error.message);
    });
};
</script>
