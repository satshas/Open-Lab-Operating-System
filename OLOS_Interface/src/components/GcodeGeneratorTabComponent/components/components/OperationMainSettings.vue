<template>
  <div class="column q-gutter-y-md">
    <div class="row col items-center q-gutter-x-md">
      <span class="sub-text-size">Laser Power:</span>
      <q-input
        ref="laserPowerInputElement"
        v-model.number="laserPower"
        :min="config?.laser_cutter_settings?.gcode_generator.laser_power.min"
        :max="config?.laser_cutter_settings?.gcode_generator.laser_power.max"
        outlined
        dense
        suffix="%"
        :error-message="errorMessage()"
        :error="!isValidPower"
        class="row col"
        @touchstart="
          virtualKeyboardStore.handleInputTouchStart(
            props.addNewThicknessCardElement ?? null,
            laserPowerInputElement
          )
        "
        @blur="virtualKeyboardStore.handleInputBlur"
        @change.capture="handleChangePowerValue"
        data-kioskboard-specialcharacters="true"
      />
    </div>
    <div class="row col items-center q-gutter-x-md">
      <span class="sub-text-size">Movement Speed:</span>
      <q-input
        ref="movementSpeedInputElement"
        v-model.number="movementSpeed"
        :min="config?.laser_cutter_settings?.gcode_generator.movement_speed.min"
        :max="config?.laser_cutter_settings?.gcode_generator.movement_speed.max"
        outlined
        dense
        suffix="mm/min"
        :error-message="errorMessage(true)"
        :error="!isValidSpeed"
        class="row col"
        @touchstart="
          virtualKeyboardStore.handleInputTouchStart(
            props.addNewThicknessCardElement ?? null,
            movementSpeedInputElement
          )
        "
        @blur="virtualKeyboardStore.handleInputBlur"
        @change.capture="handleChangeSpeedValue"
        data-kioskboard-specialcharacters="true"
      />
    </div>
    <div class="row col q-gutter-x-md items-center">
      <span class="sub-text-size">Used Tool:</span>
      <div
        v-for="(toolName, toolNum) in config?.laser_cutter_settings?.tools"
        :key="toolNum"
        class="row col q-gutter-x-md items-center"
      >
        <q-radio
          v-model="laserTool"
          :val="toolName.name"
          :label="toolName.name"
          size="4vh"
          keep-color
          @update:model-value="(newValue) => emit('update:tool', newValue)"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Config } from 'src/interfaces/configSettings.interface';
import { ref, watch } from 'vue';
import { QInput, QCard } from 'quasar';
import { useVirtualKeyboardStore } from 'src/stores/virtual-keyboard';

const props = defineProps<{
  config: Config | null;
  addNewThicknessCardElement?: QCard | null;
  power: number;
  speed: number;
  tool: string;
  isValidPower: boolean;
  isValidSpeed: boolean;
}>();

const emit = defineEmits([
  'update:power',
  'update:speed',
  'update:tool',
  'update:isValidPower',
  'update:isValidSpeed',
]);

const virtualKeyboardStore = useVirtualKeyboardStore();

const laserPower = ref<number>(props.power);
const movementSpeed = ref<number>(props.speed);
const laserTool = ref<string>(props.tool);
const isValidLaserPower = ref<boolean>(props.isValidPower);
const isValidMovementSpeed = ref<boolean>(props.isValidSpeed);
const laserPowerInputElement = ref<QInput | null>(null);
const movementSpeedInputElement = ref<QInput | null>(null);

const handleChangeSpeedValue = (event: KeyboardEvent | TouchEvent) => {
  movementSpeed.value = virtualKeyboardStore.handleSanitizeNumberInput(event);

  emit('update:speed', movementSpeed.value);
  isValidMovementSpeed.value = props.config?.laser_cutter_settings
    ? movementSpeed.value <=
        props.config.laser_cutter_settings.gcode_generator.movement_speed.max &&
      movementSpeed.value >
        props.config.laser_cutter_settings.gcode_generator.movement_speed.min
    : false;
};

const handleChangePowerValue = (event: KeyboardEvent | TouchEvent) => {
  laserPower.value = virtualKeyboardStore.handleSanitizeNumberInput(event);

  emit('update:power', laserPower.value);
  isValidLaserPower.value = props.config?.laser_cutter_settings
    ? laserPower.value <=
        props.config.laser_cutter_settings.gcode_generator.laser_power.max &&
      laserPower.value >
        props.config.laser_cutter_settings.gcode_generator.laser_power.min
    : false;
};

const errorMessage = (isSpeedError = false) => {
  if (isSpeedError && props.config?.laser_cutter_settings) {
    const minValue =
      props.config.laser_cutter_settings.gcode_generator.movement_speed.min;
    const maxValue =
      props.config.laser_cutter_settings.gcode_generator.movement_speed.max;
    return `The value should be between ${minValue} and ${maxValue}`;
  } else if (props.config?.laser_cutter_settings) {
    const minValue =
      props.config.laser_cutter_settings.gcode_generator.laser_power.min;
    const maxValue =
      props.config.laser_cutter_settings.gcode_generator.laser_power.max;
    return `The value should be between ${minValue} and ${maxValue}`;
  }
};

// emit the changes on the validation flags
watch(isValidLaserPower, (newIsValidLaserPower) => {
  emit('update:isValidPower', newIsValidLaserPower);
});

watch(isValidMovementSpeed, (newIsValidLMovementSpeed) => {
  emit('update:isValidSpeed', newIsValidLMovementSpeed);
});
</script>
