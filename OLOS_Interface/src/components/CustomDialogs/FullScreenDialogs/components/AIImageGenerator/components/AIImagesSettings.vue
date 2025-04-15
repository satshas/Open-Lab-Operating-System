<template>
  <div class="column full-width">
    <span class="title-text-size">Number of Images:</span>
    <div class="row flex-center q-gutter-x-md">
      <q-slider
        v-model="aiGeneratorSettingsData.numberOfImages"
        markers
        snap
        :min="1"
        :max="5"
        thumb-size="15px"
        class="col"
        :disable="isLoadingImages"
      />
      <span
        class="col-1 q-pa-sm bg-white rounded-borders text-center sub-text-size"
      >
        {{ aiGeneratorSettingsData.numberOfImages }}</span
      >
    </div>
  </div>
  <div class="column full-width">
    <span class="title-text-size">Image Width:</span>
    <q-select
      outlined
      v-model="aiGeneratorSettingsData.imageWidth"
      :options="Constants.AI_IMAGE_SIZE_OPTIONS"
      suffix="px"
      bg-color="white"
      behavior="menu"
      :disable="isLoadingImages"
    />
  </div>
  <div class="column full-width">
    <span class="title-text-size">Image Height:</span>
    <q-select
      outlined
      v-model="aiGeneratorSettingsData.imageHeight"
      :options="Constants.AI_IMAGE_SIZE_OPTIONS"
      suffix="px"
      bg-color="white"
      behavior="menu"
      :disable="isLoadingImages"
    />
  </div>

  <div class="row items-center full-width">
    <span class="title-text-size">Image Type:</span>
    <div class="row col">
      <q-radio
        v-model="aiGeneratorSettingsData.imageForm"
        val="PNG"
        label="PNG"
        size="4vh"
        :disable="isLoadingImages"
      />
      <q-radio
        v-model="aiGeneratorSettingsData.imageForm"
        val="SVG"
        label="SVG"
        size="4vh"
        :disable="isLoadingImages"
      />
    </div>
  </div>
</template>
<script setup lang="ts">
import { storeToRefs } from 'pinia';
import { useAiImageGeneratorStore } from 'src/stores/ai-image-generator';
import { Constants } from 'src/constants';

const aiImageGeneratorDialogStore = useAiImageGeneratorStore();

const { aiGeneratorSettingsData, isLoadingImages } = storeToRefs(
  aiImageGeneratorDialogStore
);
</script>
