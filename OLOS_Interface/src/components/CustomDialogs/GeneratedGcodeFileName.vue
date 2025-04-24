<template>
  <q-dialog ref="dialogRef" @hide="onDialogHide" :persistent="true">
    <q-card
      ref="gcodeFileNameCardElement"
      class="full-width q-pa-sm bg-blue-grey-1"
    >
      <q-card-section class="column q-pa-sm q-gutter-y-sm">
        <span class="text-bold title-text-size">Gcode Generator</span>
        <span class="subtitle-text-size"
          >what would you like to name your job file?</span
        >
        <q-space />
      </q-card-section>
      <q-card-section>
        <q-input
          ref="gcodeFileNameInputElement"
          v-model="gcodeFileName"
          placeholder="Enter your file name"
          :rules="[(val: string) => !!val || '* Required']"
          reactive-rules
          @touchstart="
            virtualKeyboardStore.handleInputTouchStart(
              gcodeFileNameCardElement,
              gcodeFileNameInputElement
            )
          "
          @blur="virtualKeyboardStore.handleInputBlur"
          @change="handleChangeFileNameValue"
          data-kioskboard-specialcharacters="true"
          suffix=".nc"
        />
      </q-card-section>

      <q-card-actions align="right">
        <q-btn flat label="Cancel" @click="onDialogCancel" color="grey-8" />
        <q-btn
          label="OK"
          color="primary"
          @click="onDialogOK(gcodeFileName)"
          :disable="isFileNameButtonDisabled"
        />
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import { useVirtualKeyboardStore } from 'src/stores/virtual-keyboard';
import { useDialogPluginComponent, QInput, QCard } from 'quasar';

const { dialogRef, onDialogHide, onDialogOK, onDialogCancel } =
  useDialogPluginComponent();
defineEmits([...useDialogPluginComponent.emits]);

const virtualKeyboardStore = useVirtualKeyboardStore();

const gcodeFileName = ref<string>('');
const gcodeFileNameInputElement = ref<QInput | null>(null);
const gcodeFileNameCardElement = ref<QCard | null>(null);

// Watch for changes to the input value to make sure if the set button disabled
const isFileNameButtonDisabled = computed(() => {
  if (gcodeFileName.value.length > 0) {
    return false;
  }
  return true;
});

const handleChangeFileNameValue = (value: string) => {
  gcodeFileName.value = value;
};
</script>
