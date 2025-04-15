<template>
  <q-dialog ref="dialogRef" @hide="onDialogHide" :persistent="true">
    <q-card
      ref="duplicateImageCardElement"
      class="full-width q-pa-sm bg-blue-grey-1"
    >
      <q-card-section class="column q-pa-sm q-gutter-y-sm">
        <span class="text-bold title-text-size">Duplicate Selected Image</span>
        <span class="subtitle-text-size"
          >Enter the number of image copies you want to generate</span
        >
        <q-space />
      </q-card-section>
      <q-card-section>
        <q-input
          ref="duplicateImageInputElement"
          v-model="numberOfCopies"
          placeholder="Enter a number"
          :rules="[
            (val: string) => !!val || '* Required',
            (val: string) =>
              Number.isInteger(parseFloat(val)) ||
              'Please Enter an Integer number',
          ]"
          reactive-rules
          @touchstart="
            virtualKeyboardStore.handleInputTouchStart(
              duplicateImageCardElement,
              duplicateImageInputElement
            )
          "
          @blur="virtualKeyboardStore.handleInputBlur"
          @change.capture="handleChangeNumberOfCopiesValue"
          data-kioskboard-specialcharacters="true"
        />
      </q-card-section>

      <q-card-actions align="right">
        <q-btn flat label="Cancel" @click="onDialogCancel" color="grey-8" />
        <q-btn
          label="Duplicate"
          color="grey-8"
          @click="setNumberOfCopies"
          :disable="isDuplicateButtonDisabled"
        />
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import { useVirtualKeyboardStore } from 'src/stores/virtual-keyboard';
import { useImageToGcodeConvertor } from 'src/stores/image-to-gcode';
import { useDialogPluginComponent, QInput, QCard } from 'quasar';

const { dialogRef, onDialogHide, onDialogOK, onDialogCancel } =
  useDialogPluginComponent();
defineEmits([...useDialogPluginComponent.emits]);

const imageToGcodeConvertorStore = useImageToGcodeConvertor();
const virtualKeyboardStore = useVirtualKeyboardStore();

const numberOfCopies = ref<number>(1);
const duplicateImageInputElement = ref<QInput | null>(null);
const duplicateImageCardElement = ref<QCard | null>(null);

// Watch for changes to the input value to make sure if the set button disabled
const isDuplicateButtonDisabled = computed(() => {
  if (numberOfCopies.value > 0) {
    return false;
  }
  return true;
});

// Methods
const setNumberOfCopies = async () => {
  for (let i = 0; i < numberOfCopies.value; i++) {
    await imageToGcodeConvertorStore.duplicateActiveImage();
  }
  onDialogOK();
};

const handleChangeNumberOfCopiesValue = (event: KeyboardEvent | TouchEvent) => {
  numberOfCopies.value = virtualKeyboardStore.handleSanitizeNumberInput(event);
};
</script>
