<template>
  <div class="column q-gutter-y-md">
    <div class="row col items-center q-gutter-x-md">
      <span class="sub-text-size">Algorithm:</span>
      <q-select
        square
        outlined
        dense
        behavior="menu"
        :options="Object.values(Constants.DITHERING_ALGORITHMS)"
        v-model="ditheringAlgorithm"
        class="row col"
        @update:model-value="(newVal) => emit('update:algorithm', newVal)"
      />
    </div>

    <div
      v-if="ditheringAlgorithm === Constants.DITHERING_ALGORITHMS.GRID"
      class="row col items-center q-gutter-x-md"
    >
      <span class="sub-text-size">Grid settings:</span>
      <div class="row col q-gutter-x-lg">
        <div class="row col items-center q-gutter-x-lg">
          <span>Block Size:</span>
          <q-slider
            v-model="ditheringBlockSize"
            :min="
              props.config?.laser_cutter_settings?.gcode_generator
                .dithering_settings.grid_algorithm.block_size.min
            "
            :max="
              props.config?.laser_cutter_settings?.gcode_generator
                .dithering_settings.grid_algorithm.block_size.max
            "
            :step="0.1"
            snap
            label
            :label-value="ditheringBlockSize + ' px'"
            label-always
            color="primary"
            class="row col"
            @update:model-value="(newVal) => emit('update:blockSize', newVal)"
          />
        </div>
        <div class="row col items-center q-gutter-x-lg">
          <span>Block Distance:</span>
          <q-slider
            v-model="ditheringBlockDistance"
            :min="
              props.config?.laser_cutter_settings?.gcode_generator
                .dithering_settings.grid_algorithm.block_distance.min
            "
            :max="
              props.config?.laser_cutter_settings?.gcode_generator
                .dithering_settings.grid_algorithm.block_distance.max
            "
            :step="0.1"
            snap
            label
            :label-value="ditheringBlockDistance + ' px'"
            label-always
            color="primary"
            class="row col"
            @update:model-value="
              (newVal) => emit('update:blockDistance', newVal)
            "
          />
        </div>
      </div>
    </div>

    <div class="row col items-center q-gutter-x-md">
      <span class="sub-text-size">Resolution:</span>
      <q-input
        ref="resolutionInputElement"
        v-model.number="ditheringResolution"
        :min="
          props.config?.laser_cutter_settings?.gcode_generator
            .dithering_settings.resolution.min
        "
        :max="
          props.config?.laser_cutter_settings?.gcode_generator
            .dithering_settings.resolution.max
        "
        outlined
        dense
        class="row col"
        suffix="DPI"
        :error-message="errorMessage()"
        :error="!isValidDitheringResolution"
        @touchstart="
          virtualKeyboardStore.handleInputTouchStart(
            addNewThicknessCardElement ?? null,
            resolutionInputElement
          )
        "
        @blur="virtualKeyboardStore.handleInputBlur"
        @change.capture="handleChangeResolutionValue"
        data-kioskboard-specialcharacters="true"
      />
    </div>
    <div class="row col items-center q-gutter-x-md">
      <span class="sub-text-size">Gray Shift:</span>
      <q-slider
        v-model="ditheringGrayShift"
        :min="-255"
        :max="255"
        :step="1"
        snap
        label
        :label-value="ditheringGrayShift"
        label-always
        color="grey-7"
        track-color="grey-1"
        class="row col"
        @update:model-value="(newVal) => emit('update:grayShift', newVal)"
      />
    </div>
  </div>
</template>
<script setup lang="ts">
import { Constants } from 'src/constants';
import { Config } from 'src/interfaces/configSettings.interface';
import { ref, watch } from 'vue';
import { useVirtualKeyboardStore } from 'src/stores/virtual-keyboard';

import { QInput, QCard } from 'quasar';

const props = defineProps<{
  config: Config | null;
  addNewThicknessCardElement?: QCard | null;
  algorithm: string;
  resolution: number;
  grayShift: number;
  blockSize: number;
  blockDistance: number;
  isValidResolution: boolean;
}>();

const emit = defineEmits([
  'update:algorithm',
  'update:resolution',
  'update:grayShift',
  'update:blockSize',
  'update:blockDistance',
  'update:isValidResolution',
]);

const virtualKeyboardStore = useVirtualKeyboardStore();

const ditheringAlgorithm = ref<string>(props.algorithm);
const ditheringResolution = ref<number>(props.resolution);
const ditheringGrayShift = ref<number>(props.grayShift);
const ditheringBlockSize = ref<number>(props.blockSize);
const ditheringBlockDistance = ref<number>(props.blockDistance);

const isValidDitheringResolution = ref<boolean>(props.isValidResolution);

const resolutionInputElement = ref<QInput | null>(null);

const handleChangeResolutionValue = (event: KeyboardEvent | TouchEvent) => {
  ditheringResolution.value =
    virtualKeyboardStore.handleSanitizeNumberInput(event);

  emit('update:resolution', ditheringResolution.value);
  isValidDitheringResolution.value = props.config?.laser_cutter_settings
    ? ditheringResolution.value <=
        props.config.laser_cutter_settings.gcode_generator.dithering_settings
          .resolution.max &&
      ditheringResolution.value >
        props.config.laser_cutter_settings.gcode_generator.dithering_settings
          .resolution.min
    : false;
};

const errorMessage = () => {
  if (props.config?.laser_cutter_settings) {
    const minValue =
      props.config.laser_cutter_settings.gcode_generator.dithering_settings
        .resolution.min;
    const maxValue =
      props.config.laser_cutter_settings.gcode_generator.dithering_settings
        .resolution.max;
    return `The value should be between ${minValue} and ${maxValue}`;
  }
};

// emit the validation changes to the parent component
watch(isValidDitheringResolution, (newIsValidDitheringResolution) => {
  emit('update:isValidResolution', newIsValidDitheringResolution);
});
</script>
