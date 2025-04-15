<template>
  <div class="column full-width">
    <div class="row items-center q-gutter-x-md">
      <span class="title-text-size">Seed:</span>
      <q-icon name="help" size="sm" color="blue-grey-9">
        <q-tooltip anchor="center right" self="center left" :offset="[10, 10]">
          {{ Constants.AI_ASSISTANT_MESSAGES.SEEDS_MESSAGE }}
        </q-tooltip>
      </q-icon>
    </div>
    <div class="row flex-center q-gutter-x-md">
      <q-slider
        v-model="aiGeneratorSettingsData.seed"
        :min="0"
        :max="999999"
        thumb-size="1.5vh"
        class="col"
        :disable="!aiGeneratorSettingsData.isSeedsUsed || isLoadingImages"
      />
      <span
        class="col-1 q-pa-sm bg-white rounded-borders text-center sub-text-size"
      >
        {{ aiGeneratorSettingsData.seed }}</span
      >
    </div>
    <q-checkbox
      v-model="aiGeneratorSettingsData.isSeedsUsed"
      left-label
      label="Use Seeds:"
      color="primary"
      size="4vh"
      class="text-subtitle1 self-start"
      :disable="isLoadingImages"
    />
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
