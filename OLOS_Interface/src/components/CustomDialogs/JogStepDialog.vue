<template>
  <q-dialog ref="dialogRef" @hide="onDialogHide" :persistent="true">
    <q-card ref="jogStepCardElement" class="full-width q-pa-sm bg-blue-grey-1">
      <q-card-section class="row items-center q-pa-sm">
        <span class="text-bold title-text-size"
          >Customize {{ jogAxis }} Jogging Step Value</span
        >
        <q-space />
      </q-card-section>
      <q-card-section>
        <q-input
          ref="jogStepInputElement"
          v-model="jogStepValue"
          placeholder="Enter a number"
          min="0"
          max="10000"
          step=".1"
          :rules="[
            (val: number) => !!val || '* Required',
            (val: number) => val > 0 || 'Only positive numbers are allowed.',
            (val: number) =>
              val <= 1000 || 'Number must be less than or equal to 1000.',
          ]"
          reactive-rules
          @keydown="virtualKeyboardStore.handleSanitizeNumberInput"
          @touchstart="
            virtualKeyboardStore.handleInputTouchStart(
              jogStepCardElement,
              jogStepInputElement
            )
          "
          @blur="virtualKeyboardStore.handleInputBlur"
          @change.capture="handleChangeJogStepValue"
          data-kioskboard-specialcharacters="true"
        />
      </q-card-section>

      <q-card-actions align="right">
        <q-btn flat label="Cancel" @click="onDialogCancel" />
        <q-btn
          label="Set"
          color="primary"
          @click="setCustomValue"
          :disable="isSetButtonDisabled"
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

const props = defineProps<{
  jogAxis: string;
  jogValue: number;
  setStepCustomValue: (value: number) => void;
}>();

const virtualKeyboardStore = useVirtualKeyboardStore();

const jogStepValue = ref<number>(props.jogValue);
const jogStepCardElement = ref<QInput | null>(null);
const jogStepInputElement = ref<QInput | null>(null);

// Watch for changes to the input value to make sure if the set button disabled
const isSetButtonDisabled = computed(() => {
  if (
    jogStepValue.value &&
    jogStepValue.value > 0 &&
    jogStepValue.value <= 1000
  )
    return false;
  return true;
});

// Methods
const setCustomValue = () => {
  props.setStepCustomValue(jogStepValue.value);
  onDialogOK();
};

const handleChangeJogStepValue = (event: KeyboardEvent | TouchEvent) => {
  jogStepValue.value = virtualKeyboardStore.handleSanitizeNumberInput(event);
};
</script>
