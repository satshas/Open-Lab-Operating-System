<template>
  <div class="column full-width">
    <div class="row items-center q-gutter-x-md">
      <span class="title-text-size"
        >Negative Prompts: (set guidance scale > 1.0)</span
      >
      <q-icon name="help" size="sm" color="blue-grey-9">
        <q-tooltip anchor="center right" self="center left" :offset="[10, 10]">
          {{ Constants.AI_ASSISTANT_MESSAGES.NEGATIVE_PROMPTS_MESSAGE }}
        </q-tooltip>
      </q-icon>
    </div>
    <q-input
      ref="negativePromptInputElement"
      v-model="aiGeneratorSettingsData.negativePrompts"
      outlined
      color="primary"
      bg-color="white"
      @touchstart="
        virtualKeyboardStore.handleInputTouchStart(
          aiDialogCardElement,
          negativePromptInputElement
        )
      "
      @blur="virtualKeyboardStore.handleInputBlur"
      @change="(value: string) => aiGeneratorSettingsData.negativePrompts = value"
      data-kioskboard-specialcharacters="true"
      :placeholder="
        Constants.AI_ASSISTANT_MESSAGES.NEGATIVE_PROMPTS_PLACEHOLDER
      "
      class="full-width sub-text-size"
      :disable="isLoadingImages"
    />
  </div>
</template>

<script setup lang="ts">
import { storeToRefs } from 'pinia';
import { useAiImageGeneratorStore } from 'src/stores/ai-image-generator';
import { useVirtualKeyboardStore } from 'src/stores/virtual-keyboard';
import { Constants } from 'src/constants';
import { ref } from 'vue';
import { QInput, QCard } from 'quasar';

defineProps<{
  aiDialogCardElement: QCard | null;
}>();

const aiImageGeneratorDialogStore = useAiImageGeneratorStore();
const virtualKeyboardStore = useVirtualKeyboardStore();

const { aiGeneratorSettingsData, isLoadingImages } = storeToRefs(
  aiImageGeneratorDialogStore
);
const negativePromptInputElement = ref<QInput | null>(null);
</script>
