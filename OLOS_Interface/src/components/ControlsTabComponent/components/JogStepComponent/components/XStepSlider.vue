<template>
  <div class="row full-width items-center">
    <span class="sub-text-size q-pr-md">X</span>

    <q-slider
      class="slider-width"
      v-model="xSliderValue"
      @change="jogControlsStore.setXJogStepSlider"
      markers
      :min="0"
      :max="3"
      thumb-size="2.5vh"
      :disable="isSliderDisabled()"
    />
    <div class="row col flex-center q-gutter-x-sm">
      <span class="sub-text-size text-bold">{{ xJogStep }} mm</span>
      <q-btn
        :icon="isCustomXStepValue ? 'close' : 'edit'"
        round
        outline
        size="1.3vh"
        @click="
          isCustomXStepValue ? clearXStepCustomValue() : openXCustomStepDialog()
        "
        :disable="isDisabled"
      />
    </div>
  </div>
  <!-- Dialog Component -->
  <custom-dialog
    v-model="dialogVisible"
    :jog-value="xJogStep"
    jog-axis="X"
    :set-step-custom-value="setXStepCustomValue"
  />
</template>

<script setup lang="ts">
import { storeToRefs } from 'pinia';
import { useJogControlsStore } from 'src/stores/jog-controls';
import CustomDialog from 'src/components/CustomDialogs/JogStepDialog.vue';
import { ref } from 'vue';

const props = defineProps<{
  isDisabled: boolean;
}>();

const jogControlsStore = useJogControlsStore();
const { xJogStep, xSliderValue, isCustomXStepValue } =
  storeToRefs(jogControlsStore);

const dialogVisible = ref(false);

const isSliderDisabled = () => {
  if (props.isDisabled || isCustomXStepValue.value) return true;
  return false;
};

const openXCustomStepDialog = () => {
  dialogVisible.value = true;
};

const setXStepCustomValue = (newValue: number) => {
  xJogStep.value = newValue;
  isCustomXStepValue.value = true;
};

const clearXStepCustomValue = () => {
  // reset to its init value
  xJogStep.value = 0.1;
  xSliderValue.value = 0;
  // Re-enable the slide
  isCustomXStepValue.value = false;
};
</script>
