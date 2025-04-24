<template>
  <div class="row full-width items-center">
    <span class="sub-text-size q-pr-md">Z</span>
    <q-slider
      class="slider-width"
      v-model="zSliderValue"
      @change="jogControlsStore.setZJogStepSlider"
      markers
      :min="0"
      :max="3"
      thumb-size="2.5vh"
      :disable="isSliderDisabled()"
    />

    <div class="row col flex-center q-gutter-x-sm">
      <span class="sub-text-size text-bold">{{ zJogStep }} mm</span>
      <q-btn
        :icon="isCustomZStepValue ? 'close' : 'edit'"
        round
        outline
        size="1.3vh"
        @click="
          isCustomZStepValue ? clearZStepCustomValue() : openZCustomStepDialog()
        "
        :disable="isDisabled"
      />
    </div>
  </div>
  <!-- Dialog Component -->
  <custom-dialog
    v-model="dialogVisible"
    :jog-value="zJogStep"
    jog-axis="Z"
    :set-step-custom-value="setZStepCustomValue"
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

const { zJogStep, zSliderValue, isCustomZStepValue } =
  storeToRefs(jogControlsStore);

const dialogVisible = ref(false);

const isSliderDisabled = () => {
  if (props.isDisabled || isCustomZStepValue.value) return true;
  return false;
};

const openZCustomStepDialog = () => {
  dialogVisible.value = true;
};

const setZStepCustomValue = (newValue: number) => {
  zJogStep.value = newValue;
  isCustomZStepValue.value = true;
};

const clearZStepCustomValue = () => {
  // reset to its init value
  zJogStep.value = 0.1;
  zSliderValue.value = 0;
  // Re-enable the slider
  isCustomZStepValue.value = false;
};
</script>
