<template>
  <div
    v-if="!imageToGcodeConvertorStore.generatorImagesDataList.length"
    class="column fit q-ma-md items-center q-gutter-y-xl"
  >
    <p class="title-text-size">Choice Images Source</p>
    <div class="row flex-center q-gutter-md">
      <q-btn
        label="Browse Uploaded Images"
        color="brown-5"
        stack
        icon="search"
        size="2vh"
        class="source-button"
        @click="imageFilesManagementStore.showUploadedImageFilesDialog"
      />
      <q-btn
        v-if="isUSBStorageConnected"
        label="Check USB Images Files"
        color="purple-5"
        stack
        icon="usb"
        class="source-button"
        @click="usbMonitorStore.showImageUSBFilesDialog"
      />

      <div v-if="config?.ai_image_generator" class="column items-center">
        <q-btn
          label="Generate Images Using AI"
          color="blue-5"
          stack
          icon="smart_toy"
          class="source-button"
          @click="aiImageGeneratorDialogStore.showAIGeneratorDialog"
        />
      </div>

      <q-btn
        label="Pick Images Files"
        color="green"
        stack
        icon="attach_file"
        class="source-button"
        @click="imageFilesInput?.pickFiles()"
      >
        <q-file
          ref="imageFilesInput"
          v-model="imagesFiles"
          accept=".jpg,.jpeg,.png,.svg,.webp,.dxf"
          :max-file-size="Constants.MAX_IMAGE_FILE_SIZE"
          multiple
          @rejected="onRejected"
          style="display: none"
          @update:model-value="handleAddNewImageFiles"
        />
      </q-btn>
    </div>
  </div>
</template>
<script setup lang="ts">
import { storeToRefs } from 'pinia';
import { useUSBMonitorStore } from 'src/stores/usb-monitor';
import { useAiImageGeneratorStore } from 'src/stores/ai-image-generator';
import { useImageFilesManagementStore } from 'src/stores/image-files-management';
import { ref } from 'vue';
import { QFile } from 'quasar';
import { Constants } from 'src/constants';
import { showNotifyMessage } from 'src/services/notify.messages.service';
import { RejectedFileEntry } from 'src/interfaces/imageToGcode.interface';
import { Config } from 'src/interfaces/configSettings.interface';
import { useImageToGcodeConvertor } from 'src/stores/image-to-gcode';
import { useMaterialLibraryStore } from 'src/stores/material-library';

defineProps<{
  config: Config | null;
}>();

const imageFilesInput = ref<QFile | null>(null);
const imagesFiles = ref<Array<File> | File | null>(null);

const aiImageGeneratorDialogStore = useAiImageGeneratorStore();
const imageFilesManagementStore = useImageFilesManagementStore();
const imageToGcodeConvertorStore = useImageToGcodeConvertor();
const usbMonitorStore = useUSBMonitorStore();
const materialLibraryStore = useMaterialLibraryStore();

const { isUSBStorageConnected } = storeToRefs(usbMonitorStore);

const handleAddNewImageFiles = (files: Array<File>) => {
  files.forEach(async (file) => {
    await imageFilesManagementStore.uploadImageFile(file);
    await imageToGcodeConvertorStore.addNewImageData(file);
    materialLibraryStore.updateGcodeFileSettings();
  });

  // clear the files array after finishing processing the files
  imagesFiles.value = null;
};
// validation function for svg file picker
const onRejected = (rejectedEntries: RejectedFileEntry[]) => {
  rejectedEntries.forEach((entry) => {
    const notifyMessage = showNotifyMessage();

    switch (entry.failedPropValidation) {
      case Constants.UPLOAD_FILES_ERRORS.MAX_FILES.NAME:
        notifyMessage.error(Constants.UPLOAD_FILES_ERRORS.MAX_FILES.MESSAGE);
        break;
      case Constants.UPLOAD_FILES_ERRORS.MAX_FILE_SIZE.NAME:
        notifyMessage.error(
          Constants.UPLOAD_FILES_ERRORS.MAX_FILE_SIZE.MESSAGE
        );
        break;
      case Constants.UPLOAD_FILES_ERRORS.ACCEPT.NAME:
        notifyMessage.error(Constants.UPLOAD_FILES_ERRORS.ACCEPT.MESSAGE);
        break;
      case Constants.UPLOAD_FILES_ERRORS.DUPLICATE.NAME:
        notifyMessage.error(Constants.UPLOAD_FILES_ERRORS.DUPLICATE.MESSAGE);
        break;
      default:
        notifyMessage.error(Constants.UPLOAD_FILES_ERRORS.DEFAULT.MESSAGE);
    }
  });
};
</script>
<style scoped>
.source-button {
  font-size: 2vh;
  max-width: 40vh;
}
</style>
