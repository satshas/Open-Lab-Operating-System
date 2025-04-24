<template>
  <q-dialog
    v-model="isAddNewImageDialogShown"
    transition-show="scale"
    transition-hide="scale"
  >
    <q-card>
      <div class="column fit">
        <q-bar
          class="row full-width text-white bg-grey-7 items-center justify-between q-py-lg"
        >
          <h5 class="text-bold">Choice Images Source</h5>
          <q-btn
            dense
            flat
            icon="close"
            size="lg"
            @click="imageToGcodeConvertorStore.closeAddNewImageDialog"
          >
            <q-tooltip>Close</q-tooltip>
          </q-btn>
        </q-bar>

        <div class="row q-pa-xl flex-center q-gutter-md">
          <q-btn
            label="Browse Uploaded Images"
            color="brown-5"
            stack
            icon="search"
            size="lg"
            class="fit"
            unelevated
            @click="imageFilesManagementStore.showUploadedImageFilesDialog"
          />
          <q-btn
            v-if="isUSBStorageConnected"
            label="Check USB Images Files"
            color="purple-5"
            stack
            icon="usb"
            size="lg"
            class="fit"
            unelevated
            @click="usbMonitorStore.showImageUSBFilesDialog"
          />

          <q-btn
            v-if="config?.ai_image_generator"
            label="Generate Images Using AI"
            color="blue-5"
            stack
            icon="smart_toy"
            size="lg"
            class="fit"
            unelevated
            @click="aiImageGeneratorDialogStore.showAIGeneratorDialog"
          />

          <q-btn
            label="Pick Images Files"
            color="green"
            stack
            icon="attach_file"
            size="lg"
            class="fit"
            unelevated
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
              @update:model-value="imageFilesManagementStore.uploadImageFile"
            />
          </q-btn>
        </div>
      </div>
    </q-card>
  </q-dialog>
</template>
<script setup lang="ts">
import { storeToRefs } from 'pinia';
import { useUSBMonitorStore } from 'src/stores/usb-monitor';
import { useAiImageGeneratorStore } from 'src/stores/ai-image-generator';
import { useImageFilesManagementStore } from 'src/stores/image-files-management';
import { ref, watch } from 'vue';
import { QFile } from 'quasar';
import { Constants } from 'src/constants';
import { showNotifyMessage } from 'src/services/notify.messages.service';
import { RejectedFileEntry } from 'src/interfaces/imageToGcode.interface';
import { Config } from 'src/interfaces/configSettings.interface';
import { useImageToGcodeConvertor } from 'src/stores/image-to-gcode';

defineProps<{
  config: Config | null;
}>();

const imageFilesInput = ref<QFile | null>(null);
const imagesFiles = ref<Array<File> | File | null>(null);

const aiImageGeneratorDialogStore = useAiImageGeneratorStore();
const imageFilesManagementStore = useImageFilesManagementStore();
const imageToGcodeConvertorStore = useImageToGcodeConvertor();
const usbMonitorStore = useUSBMonitorStore();

const { isUploadedImagesDialogShown } = storeToRefs(imageFilesManagementStore);
const { isAIImageGeneratorDialogShown } = storeToRefs(
  aiImageGeneratorDialogStore
);
const { isUSBStorageConnected, isUSBImageFilesDialogShown } =
  storeToRefs(usbMonitorStore);
const { isAddNewImageDialogShown } = storeToRefs(imageToGcodeConvertorStore);

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

// close the add new image dialog when one of the dialog close
watch(
  [
    isUploadedImagesDialogShown,
    isAIImageGeneratorDialogShown,
    isUSBImageFilesDialogShown,
  ],
  () => {
    if (isAddNewImageDialogShown.value) {
      imageToGcodeConvertorStore.closeAddNewImageDialog();
    }
  }
);
</script>
