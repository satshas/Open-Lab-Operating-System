<template>
  <div class="row full-width items-center justify-between">
    <q-btn
      :loading="isLoadingImages"
      size="2vh"
      :class="{
        'col-11': isLoadingImages,
        'full-width': !isLoadingImages,
      }"
      color="primary"
      @click="handleAIGenerateImages"
      :disable="!aiGeneratorSettingsData.mainPrompts || isLoadingImages"
    >
      Generate
      <template v-slot:loading>
        <div class="row items-center q-gutter-x-md">
          Please be patient. This process may take some time
          <q-spinner-hourglass />
        </div>
      </template>
    </q-btn>
    <q-btn
      v-if="isLoadingImages"
      icon="cancel"
      size="2vh"
      color="negative"
      class="q-ml-sm col"
      @click="handleCancelGeneratingImage"
    />
  </div>
</template>

<script setup lang="ts">
import { storeToRefs } from 'pinia';
import { useAiImageGeneratorStore } from 'src/stores/ai-image-generator';
import { useQuasar } from 'quasar';
import { Constants } from 'src/constants';
import { showNotifyMessage } from 'src/services/notify.messages.service';

const $q = useQuasar();
const aiImageGeneratorDialogStore = useAiImageGeneratorStore();
const notifyMessage = showNotifyMessage();

const { aiGeneratorSettingsData, isLoadingImages } = storeToRefs(
  aiImageGeneratorDialogStore
);

const handleAIGenerateImages = async () => {
  // make sure that the user will not enter settings that may crash the system
  if (isAISettingsValid()) {
    aiImageGeneratorDialogStore
      .generateAIImages()
      .catch((error) => notifyMessage.error(error.message));
  } else {
    showWarningAISettingsDialog();
  }
};

const handleCancelGeneratingImage = () => {
  aiImageGeneratorDialogStore
    .cancelGeneratingImages()
    .catch((error) => notifyMessage.error(error.message));
};

const isAISettingsValid = () => {
  // images number
  if (
    aiGeneratorSettingsData.value.numberOfImages >
    Constants.AI_SETTINGS_LIMITATION.NUMBER_OF_IMAGES
  ) {
    if (
      aiGeneratorSettingsData.value.inferenceSteps >
        Constants.AI_SETTINGS_LIMITATION.INFERENCE_STEPS ||
      aiGeneratorSettingsData.value.imageWidth >
        Constants.AI_SETTINGS_LIMITATION.IMAGE_WIDTH ||
      aiGeneratorSettingsData.value.inferenceSteps >
        Constants.AI_SETTINGS_LIMITATION.IMAGE_HEIGHT
    )
      return false;
  }
  // inference steps
  if (
    aiGeneratorSettingsData.value.inferenceSteps >
    Constants.AI_SETTINGS_LIMITATION.INFERENCE_STEPS
  ) {
    if (
      aiGeneratorSettingsData.value.numberOfImages >
        Constants.AI_SETTINGS_LIMITATION.NUMBER_OF_IMAGES ||
      aiGeneratorSettingsData.value.imageWidth >
        Constants.AI_SETTINGS_LIMITATION.IMAGE_WIDTH ||
      aiGeneratorSettingsData.value.imageHeight >
        Constants.AI_SETTINGS_LIMITATION.IMAGE_HEIGHT
    )
      return false;
  }
  // image width
  if (
    aiGeneratorSettingsData.value.imageWidth >
    Constants.AI_SETTINGS_LIMITATION.IMAGE_WIDTH
  ) {
    if (
      aiGeneratorSettingsData.value.numberOfImages >
        Constants.AI_SETTINGS_LIMITATION.NUMBER_OF_IMAGES ||
      aiGeneratorSettingsData.value.inferenceSteps >
        Constants.AI_SETTINGS_LIMITATION.INFERENCE_STEPS ||
      aiGeneratorSettingsData.value.imageHeight >
        Constants.AI_SETTINGS_LIMITATION.IMAGE_HEIGHT
    )
      return false;
  }
  // image height
  if (
    aiGeneratorSettingsData.value.imageHeight >
    Constants.AI_SETTINGS_LIMITATION.IMAGE_HEIGHT
  ) {
    if (
      aiGeneratorSettingsData.value.numberOfImages >
        Constants.AI_SETTINGS_LIMITATION.NUMBER_OF_IMAGES ||
      aiGeneratorSettingsData.value.inferenceSteps >
        Constants.AI_SETTINGS_LIMITATION.INFERENCE_STEPS ||
      aiGeneratorSettingsData.value.imageWidth >
        Constants.AI_SETTINGS_LIMITATION.IMAGE_WIDTH
    )
      return false;
  }
  return true;
};

const showWarningAISettingsDialog = () => {
  $q.dialog({
    color: 'primary',
    title: 'Warning!',
    message:
      'The selected settings may exceed system limits and cause instability. Please adjust them to ensure smooth operation.',
    progress: false,
    ok: true,
  });
};
</script>
