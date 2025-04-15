<template>
  <div class="row full-width items-center">
    <span class="sub-text-size q-pr-md">Y</span>

    <q-slider
      class="slider-width"
      v-model="ySliderValue"
      @change="jogControlsStore.setYJogStepSlider"
      markers
      :min="0"
      :max="3"
      thumb-size="2.5vh"
      :disable="isSliderDisabled() || isXYLocked"
    />
    <div class="row col flex-center q-gutter-x-sm">
      <span class="sub-text-size text-bold">{{ yJogStep }} mm</span>
      <q-btn
        :icon="
          isCustomYStepValue || (isCustomXStepValue && isXYLocked)
            ? 'close'
            : 'edit'
        "
        round
        outline
        size="1.3vh"
        @click="
          isCustomYStepValue ? clearYStepCustomValue() : openYCustomStepDialog()
        "
        :disable="isDisabled || isXYLocked"
      />
    </div>
  </div>
  <!-- Dialog Component -->
  <custom-dialog
    v-model="dialogVisible"
    :jog-value="yJogStep"
    jog-axis="Y"
    :set-step-custom-value="setYStepCustomValue"
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

const {
  yJogStep,
  ySliderValue,
  isCustomXStepValue,
  isCustomYStepValue,
  isXYLocked,
} = storeToRefs(jogControlsStore);

const dialogVisible = ref(false);

const isSliderDisabled = () => {
  if (props.isDisabled || isCustomYStepValue.value) return true;
  return false;
};

const openYCustomStepDialog = () => {
  dialogVisible.value = true;
};

const setYStepCustomValue = (newValue: number) => {
  yJogStep.value = newValue;
  // Disable the slider
  isCustomYStepValue.value = true;
};

const clearYStepCustomValue = () => {
  // reset to its init value
  yJogStep.value = 0.1;
  ySliderValue.value = 0;
  // Reenable the slider
  isCustomYStepValue.value = false;
};
</script>
