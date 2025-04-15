<template>
  <q-dialog ref="dialogRef" @hide="onDialogHide" :persistent="true">
    <q-card
      ref="imageNameCardElement"
      class="full-width q-pa-sm bg-blue-grey-1"
    >
      <q-card-section class="column q-pa-sm q-gutter-y-sm">
        <span class="text-bold title-text-size">AI Image Generator</span>
        <span class="*sub-text-size"
          >What would you like to name your image?</span
        >
        <q-space />
      </q-card-section>
      <q-card-section>
        <q-input
          ref="imageNameInputElement"
          v-model="imageName"
          placeholder="Enter image name"
          :suffix="isReceivedImagesSVGForm ? '.svg' : '.png'"
          @touchstart="
            virtualKeyboardStore.handleInputTouchStart(
              imageNameCardElement,
              imageNameInputElement
            )
          "
          @blur="virtualKeyboardStore.handleInputBlur"
          @change="(value: string) => (imageName = value)"
          data-kioskboard-specialcharacters="true"
        />
      </q-card-section>

      <q-card-actions align="right">
        <q-btn flat label="Cancel" @click="onDialogCancel" />
        <q-btn
          label="Ok"
          color="primary"
          @click="setNewImageName"
          :disable="isOkButtonDisabled"
        />
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useVirtualKeyboardStore } from 'src/stores/virtual-keyboard';
import { useDialogPluginComponent, QInput, QCard } from 'quasar';

const { dialogRef, onDialogHide, onDialogOK, onDialogCancel } =
  useDialogPluginComponent();
defineEmits([...useDialogPluginComponent.emits]);

const props = defineProps<{
  isReceivedImagesSVGForm: boolean;
  downloadImage?: (name: string) => Promise<void>;
  useImage?: (name: string) => Promise<void>;
  saveImage?: (name: string) => Promise<void>;
}>();

const virtualKeyboardStore = useVirtualKeyboardStore();

const imageName = ref<string>('');
const imageNameInputElement = ref<QInput | null>(null);
const imageNameCardElement = ref<QCard | null>(null);

// Methods
const setNewImageName = () => {
  if (props.downloadImage) {
    props.downloadImage(imageName.value);
  } else if (props.useImage) {
    props.useImage(imageName.value);
  } else if (props.saveImage) {
    props.saveImage(imageName.value);
  }
  onDialogOK();
};

const isOkButtonDisabled = computed(() => {
  if (imageName.value !== '') return false;
  return true;
});
</script>
