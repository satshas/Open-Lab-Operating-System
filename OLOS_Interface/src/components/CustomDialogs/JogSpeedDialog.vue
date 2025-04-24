<template>
  <q-dialog ref="dialogRef" @hide="onDialogHide" :persistent="true">
    <q-card ref="jogSpeedCardElement" class="full-width q-pa-sm bg-blue-grey-1">
      <q-card-section class="row items-center">
        <span class="text-bold title-text-size"
          >Custom {{ jogAxis }} Jogging Speed Value</span
        >
        <q-space />
      </q-card-section>
      <q-card-section>
        <q-input
          ref="jogSpeedInputElement"
          v-model="jogSpeedValue"
          placeholder="Enter a number"
          :rules="[
            (val: number) => !!val || '* Required',
            (val: number) => val > 0 || 'Only positive numbers are allowed.',
            (val: number) =>
              val <= 10000 || 'Number must be less than or equal to 10000.',
          ]"
          @keydown="virtualKeyboardStore.handleSanitizeNumberInput"
          @touchstart="
            virtualKeyboardStore.handleInputTouchStart(
              jogSpeedCardElement,
              jogSpeedInputElement
            )
          "
          @blur="virtualKeyboardStore.handleInputBlur"
          @change.capture="handleChangeJogSpeedValue"
          data-kioskboard-specialcharacters="true"
        />
      </q-card-section>

      <q-card-actions align="right">
        <q-btn flat label="Cancel" size="2vh" @click="onDialogCancel" />
        <q-btn
          label="Set"
          color="primary"
          size="2vh"
          @click="setCustomValue"
          :disable="isSetButtonDisabled"
        />
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import { useDialogPluginComponent, QInput, QCard } from 'quasar';
import { useVirtualKeyboardStore } from 'src/stores/virtual-keyboard';

const { dialogRef, onDialogHide, onDialogOK, onDialogCancel } =
  useDialogPluginComponent();
defineEmits([...useDialogPluginComponent.emits]);

const props = defineProps<{
  jogAxis: string;
  jogValue: number;
  setSpeedCustomValue: (value: number) => void;
}>();

const virtualKeyboardStore = useVirtualKeyboardStore();

const jogSpeedValue = ref<number>(props.jogValue);
const jogSpeedInputElement = ref<QInput | null>(null);
const jogSpeedCardElement = ref<QCard | null>(null);

// Watch for changes to the input value to make sure if the set button disabled
const isSetButtonDisabled = computed(() => {
  if (
    jogSpeedValue.value &&
    jogSpeedValue.value > 0 &&
    jogSpeedValue.value <= 10000
  )
    return false;
  return true;
});

// Methods
const setCustomValue = () => {
  props.setSpeedCustomValue(jogSpeedValue.value);
  onDialogOK();
};

const handleChangeJogSpeedValue = (event: KeyboardEvent | TouchEvent) => {
  jogSpeedValue.value = virtualKeyboardStore.handleSanitizeNumberInput(event);
};
</script>
