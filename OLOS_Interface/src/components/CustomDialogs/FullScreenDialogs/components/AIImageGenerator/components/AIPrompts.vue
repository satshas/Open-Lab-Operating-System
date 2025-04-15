<template>
  <div class="column full-width">
    <span class="title-text-size">Prompts:</span>
    <q-input
      ref="promptInputElement"
      v-model="aiGeneratorSettingsData.mainPrompts"
      outlined
      color="primary"
      bg-color="white"
      type="textarea"
      @touchstart="
        virtualKeyboardStore.handleInputTouchStart(
          aiDialogCardElement,
          promptInputElement
        )
      "
      @blur="virtualKeyboardStore.handleInputBlur"
      @change="(value: string) => aiGeneratorSettingsData.mainPrompts = value"
      data-kioskboard-specialcharacters="true"
      :placeholder="Constants.AI_ASSISTANT_MESSAGES.PROMPTS_PLACEHOLDER"
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

const emit = defineEmits(['update:aiDialogCardElement']);

const aiImageGeneratorDialogStore = useAiImageGeneratorStore();
const virtualKeyboardStore = useVirtualKeyboardStore();

const { aiGeneratorSettingsData, isLoadingImages } = storeToRefs(
  aiImageGeneratorDialogStore
);

// const virtualKeyboard = new VirtualKeyboard();
const promptInputElement = ref<QInput | null>(null);
</script>
