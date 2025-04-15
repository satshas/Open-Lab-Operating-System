<template>
  <div class="column full-width">
    <div class="row items-center q-gutter-x-md">
      <span class="title-text-size">Guidance Scale:</span>
      <q-icon name="help" size="sm" color="blue-grey-9">
        <q-tooltip anchor="center right" self="center left" :offset="[10, 10]">
          {{ Constants.AI_ASSISTANT_MESSAGES.GUIDANCE_SCALE_MESSAGE }}
        </q-tooltip>
      </q-icon>
    </div>
    <div class="row flex-center q-gutter-x-md">
      <q-slider
        v-model="aiGeneratorSettingsData.guidanceScale"
        markers
        snap
        :min="1"
        :max="2"
        :step="0.1"
        thumb-size="1.5vh"
        class="col"
        :disable="isLoadingImages"
      />
      <span
        class="col-1 q-pa-sm bg-white rounded-borders text-center sub-text-size"
      >
        {{ aiGeneratorSettingsData.guidanceScale }}</span
      >
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
