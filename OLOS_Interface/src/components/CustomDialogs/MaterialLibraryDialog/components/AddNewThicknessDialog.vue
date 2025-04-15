<template>
  <q-dialog
    ref="dialogRef"
    @hide="onDialogHide"
    :persistent="true"
    backdrop-filter="blur(4px)"
  >
    <q-card
      ref="addNewThicknessCardElement"
      class="q-dialog-plugin thickness-dialog-box"
    >
      <div class="column q-ma-lg q-gutter-y-lg">
        <div class="row items-center justify-start q-gutter-x-md">
          <span class="title-text-size">Material Thickness:</span>
          <q-input
            ref="addNewThicknessInputElement"
            v-model="selectedThicknessValue"
            clear-icon="close"
            suffix="mm"
            filled
            error-message="This value already exist or out of range"
            :error="!isEditThickness && !isValidThicknessValue"
            color="primary"
            class="row col sub-text-size"
            :disable="isEditThickness"
            @touchstart="
              virtualKeyboardStore.handleInputTouchStart(
                addNewThicknessCardElement,
                addNewThicknessInputElement
              )
            "
            @blur="virtualKeyboardStore.handleInputBlur"
            @change.capture="handlChangeSelectedThicknessValue"
            data-kioskboard-specialcharacters="true"
          />
        </div>

        <transition
          v-if="
            isEditThickness || (isValidThicknessValue && selectedThicknessValue)
          "
          appear
          enter-active-class="animated slideInDown"
          leave-active-class="animated slideInUp"
        >
          <div class="column q-gutter-y-md">
            <div class="row flex-start q-gutter-x-md">
              <span class="title-text-size">Operations:</span>

              <div class="column flex-start q-gutter-x-md">
                <q-checkbox
                  v-model="operationsSelection"
                  :val="Constants.PROFILE_OPTIONS.CUT"
                  :label="Constants.PROFILE_OPTIONS.CUT"
                  @update:model-value="handleAddNewOperation"
                />
                <q-checkbox
                  v-model="operationsSelection"
                  :val="Constants.PROFILE_OPTIONS.MARK"
                  :label="Constants.PROFILE_OPTIONS.MARK"
                  @update:model-value="handleAddNewOperation"
                />
                <q-checkbox
                  v-model="operationsSelection"
                  :val="Constants.PROFILE_OPTIONS.ENGRAVE"
                  :label="Constants.PROFILE_OPTIONS.ENGRAVE"
                  @update:model-value="handleAddNewOperation"
                />
              </div>
            </div>

            <transition
              appear
              enter-active-class="animated slideInDown"
              v-if="
                selectedThicknessValue &&
                operationsSelection.includes(Constants.PROFILE_OPTIONS.CUT)
              "
            >
              <div class="column flex-start">
                <q-separator />
                <p class="title-text-size"><u>Cutting Settings:</u></p>
                <operation-main-settings
                  :config
                  :add-new-thickness-card-element
                  v-model:power="laserPowerCutting"
                  v-model:speed="movementSpeedCutting"
                  v-model:tool="laserToolCutting"
                  v-model:is-valid-power="isValidLaserPowerCutting"
                  v-model:is-valid-speed="isValidMovementSpeedCutting"
                />
              </div>
            </transition>
            <transition
              appear
              enter-active-class="animated slideInDown"
              v-if="
                selectedThicknessValue &&
                operationsSelection.includes(Constants.PROFILE_OPTIONS.MARK)
              "
            >
              <div class="column flex-start">
                <q-separator />
                <p class="title-text-size"><u>Marking Settings:</u></p>

                <operation-main-settings
                  :config
                  :add-new-thickness-card-element
                  v-model:power="laserPowerMarking"
                  v-model:speed="movementSpeedMarking"
                  v-model:tool="laserToolMarking"
                  v-model:is-valid-power="isValidLaserPowerMarking"
                  v-model:is-valid-speed="isValidMovementSpeedMarking"
                />
              </div>
            </transition>
            <transition
              appear
              enter-active-class="animated slideInDown"
              v-if="
                selectedThicknessValue &&
                operationsSelection.includes(Constants.PROFILE_OPTIONS.ENGRAVE)
              "
            >
              <div class="column flex-start">
                <q-separator />
                <p class="title-text-size"><u>Engraving Settings:</u></p>

                <operation-main-settings
                  :config
                  :add-new-thickness-card-element
                  v-model:power="laserPowerEngraving"
                  v-model:speed="movementSpeedEngraving"
                  v-model:tool="laserToolEngraving"
                  v-model:is-valid-power="isValidLaserPowerEngraving"
                  v-model:is-valid-speed="isValidMovementSpeedEngraving"
                />

                <dithering-settings
                  :config
                  :add-new-thickness-card-element
                  v-model:algorithm="ditheringAlgorithm"
                  v-model:resolution="ditheringResolution"
                  v-model:grayShift="ditheringGrayShift"
                  v-model:block-size="ditheringBlockSize"
                  v-model:block-distance="ditheringBlockDistance"
                  v-model:is-valid-resolution="isValidDitheringResolution"
                  class="q-pt-md"
                />
              </div>
            </transition>
          </div>
        </transition>
        <q-card-actions align="right">
          <q-btn
            color="primary"
            flat
            label="Cancel"
            @click="onDialogCancel"
            size="1.5vh"
          />
          <q-btn
            v-if="isEditThickness"
            color="primary"
            label="Update"
            size="1.5vh"
            @click="handleUpdateThickness"
            :disable="!selectedThicknessValue || !isValidThickness"
          />

          <q-btn
            v-else
            color="primary"
            label="Add"
            size="1.5vh"
            @click="handleAddNewThickness"
            :disable="!selectedThicknessValue || !isValidThickness"
          />
        </q-card-actions>
      </div>
    </q-card>
  </q-dialog>
</template>
<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import { useDialogPluginComponent, QInput, QCard } from 'quasar';
import {
  MaterialThickness,
  ThicknessOperation,
} from 'src/interfaces/imageToGcode.interface';
import { Constants } from 'src/constants';
import { configurationSettings } from 'src/services/configuration.loader.service';
import { Config } from 'src/interfaces/configSettings.interface';
import { useVirtualKeyboardStore } from 'src/stores/virtual-keyboard';
import OperationMainSettings from 'src/components/GcodeGeneratorTabComponent/components/components/OperationMainSettings.vue';
import DitheringSettings from 'src/components/GcodeGeneratorTabComponent/components/components/DitheringSettings.vue';

const { dialogRef, onDialogHide, onDialogOK, onDialogCancel } =
  useDialogPluginComponent();
defineEmits([...useDialogPluginComponent.emits]);

const props = defineProps<{
  materialThicknesses: Array<MaterialThickness>;
  thicknessData: MaterialThickness | null;
  addThickness: (newThickness: MaterialThickness) => void;
  updateThickness: (selectedThickness: MaterialThickness) => void | null;
  deleteThickness: () => void | null;
  isEditThickness: boolean;
}>();

const virtualKeyboardStore = useVirtualKeyboardStore();

const config = ref<Config | null>(null);
const addNewThicknessCardElement = ref<QCard | null>(null);
const addNewThicknessInputElement = ref<QInput | null>(null);
const selectedThicknessValue = ref<number | null>(null);
const selectedMaterialThicknesses = ref<Array<MaterialThickness>>([]);
const selectedThicknessData = ref<MaterialThickness | null>(null);
const selectedThicknessOperations = ref<Array<ThicknessOperation>>([]);
const operationsSelection = ref<Array<string>>([]);
const isValidLaserPowerCutting = ref<boolean>(true);
const isValidMovementSpeedCutting = ref<boolean>(true);
const isValidLaserPowerMarking = ref<boolean>(true);
const isValidMovementSpeedMarking = ref<boolean>(true);
const isValidLaserPowerEngraving = ref<boolean>(true);
const isValidMovementSpeedEngraving = ref<boolean>(true);
const isValidDitheringResolution = ref<boolean>(true);

const laserPowerCutting = ref<number>(
  Constants.DEFAULT_GCODE_GENERATOR_SETTINGS.CUTTING_SETTINGS.power
);
const movementSpeedCutting = ref<number>(
  Constants.DEFAULT_GCODE_GENERATOR_SETTINGS.CUTTING_SETTINGS.speed
);
const laserToolCutting = ref<string>(
  Constants.DEFAULT_GCODE_GENERATOR_SETTINGS.CUTTING_SETTINGS.tool
);

const laserPowerMarking = ref<number>(
  Constants.DEFAULT_GCODE_GENERATOR_SETTINGS.MARKING_SETTINGS.power
);
const movementSpeedMarking = ref<number>(
  Constants.DEFAULT_GCODE_GENERATOR_SETTINGS.MARKING_SETTINGS.speed
);
const laserToolMarking = ref<string>(
  Constants.DEFAULT_GCODE_GENERATOR_SETTINGS.MARKING_SETTINGS.tool
);

const laserPowerEngraving = ref<number>(
  Constants.DEFAULT_GCODE_GENERATOR_SETTINGS.ENGRAVING_SETTINGS.power
);
const movementSpeedEngraving = ref<number>(
  Constants.DEFAULT_GCODE_GENERATOR_SETTINGS.ENGRAVING_SETTINGS.speed
);
const laserToolEngraving = ref<string>(
  Constants.DEFAULT_GCODE_GENERATOR_SETTINGS.ENGRAVING_SETTINGS.tool
);

const ditheringAlgorithm = ref<string>(
  Constants.DEFAULT_GCODE_GENERATOR_SETTINGS.ENGRAVING_SETTINGS.dithering
    .algorithm
);
const ditheringResolution = ref<number>(
  Constants.DEFAULT_GCODE_GENERATOR_SETTINGS.ENGRAVING_SETTINGS.dithering
    .resolution
);
const ditheringGrayShift = ref<number>(
  Constants.DEFAULT_GCODE_GENERATOR_SETTINGS.ENGRAVING_SETTINGS.dithering
    .grayShift
);
const ditheringBlockSize = ref<number>(
  Constants.DEFAULT_GCODE_GENERATOR_SETTINGS.ENGRAVING_SETTINGS.dithering
    .blockSize
);
const ditheringBlockDistance = ref<number>(
  Constants.DEFAULT_GCODE_GENERATOR_SETTINGS.ENGRAVING_SETTINGS.dithering
    .blockDistance
);

const isValidThicknessValue = computed(() => {
  if (
    selectedThicknessValue.value &&
    0 < selectedThicknessValue.value &&
    selectedThicknessValue.value < 1000
  ) {
    return !props.materialThicknesses.find(
      (thickness) => thickness.thicknessValue == selectedThicknessValue.value
    );
  } else if (!selectedThicknessValue.value) {
    return true;
  }
  return false;
});

const isValidThickness = computed(
  () =>
    (props.isEditThickness || isValidThicknessValue.value) &&
    selectedThicknessOperations.value.length &&
    isValidLaserPowerCutting.value &&
    isValidLaserPowerMarking.value &&
    isValidLaserPowerEngraving.value &&
    isValidMovementSpeedCutting.value &&
    isValidMovementSpeedMarking.value &&
    isValidMovementSpeedEngraving.value &&
    isValidDitheringResolution.value
);

const handleAddNewThickness = () => {
  const newThickness = {
    thicknessValue: selectedThicknessValue.value,
    thicknessOperations: selectedThicknessOperations.value,
  } as MaterialThickness;
  props.addThickness(newThickness);

  onDialogOK();
};

const handleUpdateThickness = () => {
  if (props.isEditThickness && selectedThicknessData.value) {
    selectedThicknessData.value = {
      ...selectedThicknessData.value,
      thicknessValue: selectedThicknessValue.value || 0,
      thicknessOperations: selectedThicknessOperations.value,
    };
    props.updateThickness(selectedThicknessData.value);
  }
  onDialogOK();
};

const handleAddNewOperation = (operations: Array<string>) => {
  // check all the operations for the thickness and compare them with existing operations for the specific thickness
  const newThicknessOperation = [] as Array<ThicknessOperation>;

  // get the array of all the operations for specific thickness
  const thicknessOperations = selectedThicknessOperations.value.map(
    (operation) => operation.operationType
  );

  operations.map((operation) => {
    if (!thicknessOperations.includes(operation)) {
      // add default settings for each operation
      switch (operation) {
        case Constants.PROFILE_OPTIONS.ENGRAVE:
          newThicknessOperation.push({
            operationType: operation,
            power: laserPowerEngraving.value,
            speed: movementSpeedEngraving.value,
            tool: laserToolEngraving.value,
            dithering: {
              algorithm: ditheringAlgorithm.value,
              resolution: ditheringResolution.value,
              grayShift: ditheringGrayShift.value,
              blockSize: ditheringBlockSize.value,
              blockDistance: ditheringBlockDistance.value,
            },
          } as ThicknessOperation);
          break;
        case Constants.PROFILE_OPTIONS.MARK:
          newThicknessOperation.push({
            operationType: operation,
            power: laserPowerMarking.value,
            speed: movementSpeedMarking.value,
            tool: laserToolMarking.value,
          } as ThicknessOperation);
          break;
        case Constants.PROFILE_OPTIONS.CUT:
          newThicknessOperation.push({
            operationType: operation,
            power: laserPowerCutting.value,
            speed: movementSpeedCutting.value,
            tool: laserToolCutting.value,
          } as ThicknessOperation);
          break;
      }
    } else {
      // add already existing operation with there own settings
      const existedOperation = selectedThicknessOperations.value.find(
        (op) => op.operationType === operation
      ) as ThicknessOperation;
      newThicknessOperation.push(existedOperation);
    }
  });
  selectedThicknessOperations.value = newThicknessOperation;
};

const handlChangeSelectedThicknessValue = (
  event: KeyboardEvent | TouchEvent
) => {
  selectedThicknessValue.value =
    virtualKeyboardStore.handleSanitizeNumberInput(event);
};

watch(
  () => [
    laserPowerCutting.value,
    movementSpeedCutting.value,
    laserToolCutting.value,
    laserPowerMarking.value,
    movementSpeedMarking.value,
    laserToolMarking.value,
    laserPowerEngraving.value,
    movementSpeedEngraving.value,
    laserToolEngraving.value,
    ditheringAlgorithm.value,
    ditheringResolution.value,
    ditheringGrayShift.value,
    ditheringBlockSize.value,
    ditheringBlockDistance.value,
  ],
  ([
    newCuttingPower,
    newCuttingSpeed,
    newCuttingTool,
    newMarkingPower,
    newMarkingSpeed,
    newMarkingTool,
    newEngravingPower,
    newEngravingSpeed,
    newEngravingTool,
    newDitheringAlgorithm,
    newDitheringResolution,
    newDitheringGrayShift,
    newDitheringBlockSize,
    newDitheringBlockDistance,
  ]) => {
    // Update Cutting Operation
    const cuttingOperation = selectedThicknessOperations.value.find(
      (op) => op.operationType === Constants.PROFILE_OPTIONS.CUT
    );
    if (cuttingOperation) {
      cuttingOperation.power = newCuttingPower as number;
      cuttingOperation.speed = newCuttingSpeed as number;
      cuttingOperation.tool = newCuttingTool as string;
    }

    // Update Marking Operation
    const markingOperation = selectedThicknessOperations.value.find(
      (op) => op.operationType === Constants.PROFILE_OPTIONS.MARK
    );
    if (markingOperation) {
      markingOperation.power = newMarkingPower as number;
      markingOperation.speed = newMarkingSpeed as number;
      markingOperation.tool = newMarkingTool as string;
    }

    // Update Engraving Operation
    const engravingOperation = selectedThicknessOperations.value.find(
      (op) => op.operationType === Constants.PROFILE_OPTIONS.ENGRAVE
    );
    if (engravingOperation) {
      engravingOperation.power = newEngravingPower as number;
      engravingOperation.speed = newEngravingSpeed as number;
      engravingOperation.tool = newEngravingTool as string;
      if (engravingOperation.dithering) {
        engravingOperation.dithering.algorithm =
          newDitheringAlgorithm as string;
        engravingOperation.dithering.resolution =
          newDitheringResolution as number;
        engravingOperation.dithering.grayShift =
          newDitheringGrayShift as number;
        engravingOperation.dithering.blockSize =
          newDitheringBlockSize as number;
        engravingOperation.dithering.blockDistance =
          newDitheringBlockDistance as number;
      }
    }
  }
);

const setupOperationsSettings = () => {
  if (props.isEditThickness) {
    selectedThicknessOperations.value.forEach((operation) => {
      switch (operation.operationType) {
        case Constants.PROFILE_OPTIONS.ENGRAVE:
          laserPowerEngraving.value = operation.power;
          movementSpeedEngraving.value = operation.speed;
          laserToolEngraving.value = operation.tool;
          if (operation.dithering) {
            ditheringAlgorithm.value = operation.dithering.algorithm;
            ditheringResolution.value = operation.dithering.resolution;
            ditheringGrayShift.value = operation.dithering.grayShift;
            ditheringBlockSize.value = operation.dithering.blockSize;
            ditheringBlockDistance.value = operation.dithering.blockDistance;
          }
          break;

        case Constants.PROFILE_OPTIONS.MARK:
          laserPowerMarking.value = operation.power;
          movementSpeedMarking.value = operation.speed;
          laserToolMarking.value = operation.tool;
          break;

        case Constants.PROFILE_OPTIONS.CUT:
          laserPowerCutting.value = operation.power;
          movementSpeedCutting.value = operation.speed;
          laserToolCutting.value = operation.tool;
          break;
      }
    });
  }
};

onMounted(async () => {
  config.value = await configurationSettings();
  selectedMaterialThicknesses.value = props.materialThicknesses;
  selectedThicknessData.value = props.thicknessData;
  selectedThicknessValue.value =
    selectedThicknessData.value?.thicknessValue || null;
  selectedThicknessOperations.value =
    selectedThicknessData.value?.thicknessOperations || [];
  operationsSelection.value = selectedThicknessOperations.value?.map(
    (operation) => operation.operationType || ''
  );

  setupOperationsSettings();
});
</script>
<style scoped>
.thickness-dialog-box {
  min-width: 50vw;
}
</style>
