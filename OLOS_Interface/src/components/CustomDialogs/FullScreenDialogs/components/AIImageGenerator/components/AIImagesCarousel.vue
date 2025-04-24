<template>
  <div class="row flex-center images-container">
    <transition
      appear
      enter-active-class="animated fadeIn"
      leave-active-class="animated fadeOut"
    >
      <q-carousel
        v-if="originalGeneratedImages.length"
        v-model="imageSliderNumber"
        v-model:fullscreen="isFullScreen"
        swipeable
        animated
        thumbnails
        infinite
        class="fit"
      >
        <q-carousel-slide
          v-for="(image, index) in base64GeneratedImages"
          :key="index"
          :name="index"
          :img-src="image"
          class="images-style"
        />
        <template v-slot:control>
          <image-controls-button
            :is-full-screen="isFullScreen"
            :is-loading-images="isLoadingImages"
            :handle-full-screen
            :handle-use-image
            :handle-save-image
            :handle-download-image
          />
        </template>
      </q-carousel>

      <q-icon v-else name="image" size="20vw" color="grey" />
    </transition>

    <q-inner-loading
      class="column fit items-center justify-between"
      :showing="isLoadingImages"
    >
      <q-spinner class="col" size="5vw" color="primary" />
    </q-inner-loading>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useAiImageGeneratorStore } from 'src/stores/ai-image-generator';
import { useImageToGcodeConvertor } from 'src/stores/image-to-gcode';
import { useImageFilesManagementStore } from 'src/stores/image-files-management';
import { useMaterialLibraryStore } from 'src/stores/material-library';
import { fileFromImageUrl } from 'src/services/image.editor.service';
import { showNotifyMessage } from 'src/services/notify.messages.service';
import ImageControlsButton from 'src/components/CustomDialogs/FullScreenDialogs/components/AIImageGenerator/components/ImageControlsButton.vue';
import AiImageNameDialog from 'src/components/CustomDialogs/FullScreenDialogs/components/AIImageGenerator/components/AIImageNameDialog.vue';
import { useQuasar } from 'quasar';

const $q = useQuasar();
const aiImageGeneratorDialogStore = useAiImageGeneratorStore();
const notifyMessage = showNotifyMessage();

import { storeToRefs } from 'pinia';

const imageToGcodeConvertorStore = useImageToGcodeConvertor();
const imageFilesManagementStore = useImageFilesManagementStore();
const materialLibraryStore = useMaterialLibraryStore();

const {
  originalGeneratedImages,
  base64GeneratedImages,
  isLoadingImages,
  isReceivedImagesSVGForm,
} = storeToRefs(aiImageGeneratorDialogStore);

const imageSliderNumber = ref<number>(0);
const isFullScreen = ref<boolean>(false);

const handleFullScreen = () => {
  isFullScreen.value = !isFullScreen.value;
};

const handleDownloadImage = async () => {
  $q.dialog({
    component: AiImageNameDialog,
    componentProps: {
      isReceivedImagesSVGForm: isReceivedImagesSVGForm.value,
      downloadImage,
    },
  });
};

const downloadImage = async (name: string) => {
  const imageSrc = originalGeneratedImages.value[imageSliderNumber.value];

  const blob = await fetch(imageSrc).then((res) => res.blob());

  // Create a temporary link element
  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  const imageName = name + (isReceivedImagesSVGForm.value ? '.svg' : '.png');
  // upload to system
  link.download = imageName;
  // Trigger download
  link.click();
  // Clean up the URL object
  URL.revokeObjectURL(link.href);
};

const handleUseImage = async () => {
  $q.dialog({
    component: AiImageNameDialog,
    componentProps: {
      isReceivedImagesSVGForm: isReceivedImagesSVGForm.value,
      useImage,
    },
  });
};

const useImage = async (name: string) => {
  const imageSrc = originalGeneratedImages.value[imageSliderNumber.value];
  // first, upload to system
  const imageName = name + (isReceivedImagesSVGForm.value ? '.svg' : '.png');
  // upload to system
  const image = await fileFromImageUrl(imageSrc, imageName);
  await imageFilesManagementStore.uploadImageFile(image);
  // add the image to the generator images list
  await imageToGcodeConvertorStore.addNewImageData(image);
  // Close the generator dialog
  aiImageGeneratorDialogStore.closeAIGeneratorDialog();
  // update the gcode settings for the image
  materialLibraryStore.updateGcodeFileSettings();
};

const handleSaveImage = async () => {
  $q.dialog({
    component: AiImageNameDialog,
    componentProps: {
      isReceivedImagesSVGForm: isReceivedImagesSVGForm.value,
      saveImage,
    },
  });
};

const saveImage = async (name: string) => {
  const imageSrc = originalGeneratedImages.value[imageSliderNumber.value];
  const imageName = name + (isReceivedImagesSVGForm.value ? '.svg' : '.png');

  // upload to system
  const image = await fileFromImageUrl(imageSrc, imageName);
  await imageFilesManagementStore.uploadImageFile(image).then(() => {
    notifyMessage.success('Image saved successfully in the system');
  });
};
</script>
<style scoped>
.images-container {
  width: 100%;
  height: 50vh;
  position: relative;
  background-color: white;
  border-radius: 5px;
  border: 2px solid gray;
}

.images-style {
  background-size: contain;
  background-repeat: no-repeat;
  background-position: center;
}
</style>
