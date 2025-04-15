<template>
  <div class="q-pa-lg">
    <div v-if="config" class="column q-gutter-md">
      <image-viewer :config="config" />

      <image-note-message v-if="imageToGcodeConvertorStore.activeImage" />

      <image-settings-box
        :key="imageToGcodeConvertorStore.activeImage?.imageId"
        :hidden="!imageToGcodeConvertorStore.activeImage"
        :config="config"
      />
      <q-card
        v-if="imageToGcodeConvertorStore.activeImage"
        bordered
        square
        flat
        class="fit"
      >
        <q-splitter v-model="splitterModel" :horizontal="isMobile">
          <template v-slot:before>
            <q-tabs
              v-model="activeTab"
              class="text-grey border-bottom"
              active-color="primary"
              active-bg-color="grey-4"
              indicator-color="primary"
              :vertical="!isMobile"
              stretch
            >
              <q-tab name="mapping" icon="grid_on" label="Mapping" />
              <q-tab
                name="settings"
                icon="settings"
                label="Settings"
                class="col-grow"
              />
              <q-tab
                name="materials"
                icon="library_books"
                label="Materials"
                class="col-grow"
              />
            </q-tabs>
          </template>
          <template v-slot:after>
            <q-tab-panels
              v-model="activeTab"
              animated
              :vertical="!isMobile"
              transition-prev="jump-up"
              transition-next="jump-up"
            >
              <q-tab-panel name="mapping">
                <image-mapping
                  :key="imageToGcodeConvertorStore.activeImage?.imageId"
                />
              </q-tab-panel>

              <q-tab-panel name="settings">
                <gcode-file-settings
                  :config="config"
                  :key="imageToGcodeConvertorStore.activeImage?.imageId"
                />
              </q-tab-panel>

              <q-tab-panel name="materials">
                <material-library />
              </q-tab-panel>
            </q-tab-panels>
          </template>
        </q-splitter>
      </q-card>

      <generate-gcode-button :config="config" />
    </div>
  </div>
</template>
<script setup lang="ts">
import { useQuasar } from 'quasar';
import ImageViewer from 'src/components/GcodeGeneratorTabComponent/components/ImageViewer.vue';
import ImageMapping from 'src/components/GcodeGeneratorTabComponent/components/ImageMapping.vue';
import ImageSettingsBox from 'src/components/GcodeGeneratorTabComponent/components/ImageSettingsBox.vue';
import ImageNoteMessage from 'src/components/GcodeGeneratorTabComponent/components/ImageNoteMessage.vue';
import materialLibrary from 'src/components/GcodeGeneratorTabComponent/components/MaterialLibrary.vue';
import GcodeFileSettings from 'src/components/GcodeGeneratorTabComponent/components/GcodeFileSettings.vue';
import GenerateGcodeButton from 'src/components/GcodeGeneratorTabComponent/components/GenerateGcodeButton.vue';
import { onMounted, ref, watch, computed } from 'vue';
import { useImageToGcodeConvertor } from 'src/stores/image-to-gcode';
import { useAiImageGeneratorStore } from 'src/stores/ai-image-generator';
import { useMaterialLibraryStore } from 'src/stores/material-library';
import { storeToRefs } from 'pinia';
import { configurationSettings } from 'src/services/configuration.loader.service';
import { Config } from 'src/interfaces/configSettings.interface';
import { Constants } from 'src/constants';
import { useUSBMonitorStore } from 'src/stores/usb-monitor';
import { useImageFilesManagementStore } from 'src/stores/image-files-management';

const $q = useQuasar();
const imageToGcodeConvertorStore = useImageToGcodeConvertor();
const aiImageGeneratorDialogStore = useAiImageGeneratorStore();
const materialLibraryStore = useMaterialLibraryStore();
const imageFilesManagementStore = useImageFilesManagementStore();
const usbMonitorStore = useUSBMonitorStore();

const { isUSBStorageConnected } = storeToRefs(usbMonitorStore);
const { isUploadedImagesDialogShown } = storeToRefs(imageFilesManagementStore);

const config = ref<Config | null>(null);
const splitterModel = ref(15);
const isMobile = ref($q.screen.lt.md);

// change the tab when adding a new image or changing the active image
const activeTab = computed({
  get() {
    return imageToGcodeConvertorStore.activeImage?.activeTab;
  },
  set(newActiveTab) {
    if (newActiveTab && imageToGcodeConvertorStore.activeImage)
      imageToGcodeConvertorStore.activeImage.activeTab = newActiveTab;
  },
});

// check if a usb drive is connected
watch(isUSBStorageConnected, (newIsUSBStorageConnected) => {
  if (newIsUSBStorageConnected) {
    if (isUploadedImagesDialogShown.value) {
      imageFilesManagementStore.closeUploadedImageFilesDialog();
    }
    usbMonitorStore.showImageUSBFilesDialog();
  } else {
    usbMonitorStore.closeImageUSBFilesDialog();
  }
});

onMounted(async () => {
  config.value = await configurationSettings();

  // load material library data
  if (config.value.machine_type === Constants.MACHINE_TYPE.LASER_CUTTER) {
    await materialLibraryStore.fetchMaterialLibraryData();
    // load system saved images data
    await imageFilesManagementStore.listImages();

    // load AI settings
    if (config.value?.ai_configuration.use_ai_image_generator) {
      aiImageGeneratorDialogStore.fetchAIConfigData();
    }
  }
});
</script>
<style>
::v-deep(.q-tab__icon) {
  font-size: 2.5vh;
}
::v-deep(.q-tab__label) {
  font-size: 2vh;
}
</style>
