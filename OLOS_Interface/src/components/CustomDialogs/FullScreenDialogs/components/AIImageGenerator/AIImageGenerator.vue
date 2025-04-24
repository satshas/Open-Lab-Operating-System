<template>
  <q-dialog
    v-model="aiImageGeneratorDialogStore.isAIImageGeneratorDialogShown"
    persistent
    maximized
    transition-show="scale"
    transition-hide="scale"
  >
    <q-card class="bg-grey-4">
      <div ref="aiDialogCardElement" class="column fit relative-position">
        <q-bar
          class="row full-width text-white bg-primary items-center justify-between q-py-md"
        >
          <span class="text-bold title-text-size">AI Image Generator</span>
          <q-btn
            dense
            flat
            icon="close"
            size="2vh"
            @click="aiImageGeneratorDialogStore.closeAIGeneratorDialog"
          >
            <q-tooltip class="text-white">Close</q-tooltip>
          </q-btn>
        </q-bar>

        <div class="row full-width col">
          <div
            class="column col-md-6 col-sm-12 col-xs-12 items-center justify-between q-pa-md q-gutter-y-sm"
          >
            <ai-images-carousel />

            <ai-prompts :ai-dialog-card-element />

            <ai-negative-prompts :ai-dialog-card-element />

            <generate-images-button />
          </div>

          <q-separator
            :vertical="!$q.screen.lt.md"
            color="black"
            class="q-my-md"
            size="sm"
          />

          <div
            class="column col items-center justify-between q-pa-md q-gutter-y-sm"
          >
            <ai-models-selector />

            <q-separator class="full-width" />

            <ai-images-settings />

            <q-separator class="full-width" />

            <ai-inference-steps />

            <ai-guidance-scale />

            <ai-seeds />

            <q-separator class="full-width" />

            <ai-settings-buttons />
          </div>
        </div>
      </div>
    </q-card>
  </q-dialog>
</template>

<script setup lang="ts">
import AiPrompts from 'src/components/CustomDialogs/FullScreenDialogs/components/AIImageGenerator/components/AIPrompts.vue';
import AiNegativePrompts from 'src/components/CustomDialogs/FullScreenDialogs/components/AIImageGenerator/components/AINegativePrompts.vue';
import AiImagesCarousel from 'src/components/CustomDialogs/FullScreenDialogs/components/AIImageGenerator/components/AIImagesCarousel.vue';
import GenerateImagesButton from 'src/components/CustomDialogs/FullScreenDialogs/components/AIImageGenerator/components/GenerateImagesButton.vue';
import AiModelsSelector from 'src/components/CustomDialogs/FullScreenDialogs/components/AIImageGenerator/components/AIModelsSelector.vue';
import AiImagesSettings from 'src/components/CustomDialogs/FullScreenDialogs/components/AIImageGenerator/components/AIImagesSettings.vue';
import AiInferenceSteps from 'src/components/CustomDialogs/FullScreenDialogs/components/AIImageGenerator/components/AIInferenceSteps.vue';
import AiGuidanceScale from 'src/components/CustomDialogs/FullScreenDialogs/components/AIImageGenerator/components/AIGuidanceScale.vue';
import AiSeeds from 'src/components/CustomDialogs/FullScreenDialogs/components/AIImageGenerator/components/AISeeds.vue';
import AiSettingsButtons from 'src/components/CustomDialogs/FullScreenDialogs/components/AIImageGenerator/components/AISettingsButtons.vue';
import { useAiImageGeneratorStore } from 'src/stores/ai-image-generator';
import { useQuasar, QCard } from 'quasar';
import { ref } from 'vue';

const $q = useQuasar();

const aiImageGeneratorDialogStore = useAiImageGeneratorStore();
const aiDialogCardElement = ref<QCard | null>(null);
</script>
