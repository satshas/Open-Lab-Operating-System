<template>
  <q-dialog ref="dialogRef" @hide="onDialogHide" :persistent="true">
    <!-- Dialog content -->
    <q-card
      ref="settingsNameCardElement"
      class="full-width q-pa-sm bg-blue-grey-1"
    >
      <q-card-section class="row items-center q-pa-sm">
        <span class="text-bold title-text-size">Give your settings a name</span>
        <q-space />
      </q-card-section>
      <q-card-section>
        <q-input
          ref="settingsNameInputElement"
          v-model="aiImageGeneratorDialogStore.aiSettingName"
          placeholder="Enter settings name"
          reactive-rules
          @touchstart="
            virtualKeyboardStore.handleInputTouchStart(
              settingsNameCardElement,
              settingsNameInputElement
            )
          "
          @blur="virtualKeyboardStore.handleInputBlur"
          @change="(value: string) => (aiImageGeneratorDialogStore.aiSettingName = value)"
          data-kioskboard-specialcharacters="true"
        />
      </q-card-section>

      <q-card-actions align="right">
        <q-btn flat label="Cancel" @click="onDialogCancel" />
        <q-btn
          label="Ok"
          color="positive"
          @click="setNewSettingsName"
          :disable="isOkButtonDisabled"
        />
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useAiImageGeneratorStore } from 'src/stores/ai-image-generator';
import { useDialogPluginComponent, QInput, QCard } from 'quasar';
import { useVirtualKeyboardStore } from 'src/stores/virtual-keyboard';

const { dialogRef, onDialogHide, onDialogOK, onDialogCancel } =
  useDialogPluginComponent();
defineEmits([...useDialogPluginComponent.emits]);

const aiImageGeneratorDialogStore = useAiImageGeneratorStore();
const virtualKeyboardStore = useVirtualKeyboardStore();

const props = defineProps<{
  handleSaveAISettings: () => void;
}>();

const settingsNameInputElement = ref<QInput | null>(null);
const settingsNameCardElement = ref<QCard | null>(null);

// Methods
const setNewSettingsName = () => {
  props.handleSaveAISettings();
  onDialogOK();
};

const isOkButtonDisabled = computed(() => {
  if (aiImageGeneratorDialogStore.aiSettingName.length > 0) return false;
  return true;
});
</script>
