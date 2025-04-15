<template>
  <div class="column q-gutter-y-md">
    <p class="title-text-size text-bold"><u>Main Settings:</u></p>

    <div class="row items-center justify-start q-gutter-x-md">
      <span class="sub-text-size">Material Name:</span>
      <q-select
        filled
        behavior="menu"
        v-model="selectedMaterial"
        :options="materialsList ? materialsList : []"
        clearable
        class="row col"
        dense
        @update:model-value="handleRemoveMaterialThickness"
      >
        <template v-slot:selected-item="scope">
          <q-item class="row full-width items-center justify-between">
            <q-item-section>
              <q-item-label class="title-text-size">{{
                scope.opt.materialName
              }}</q-item-label>
            </q-item-section>
            <q-item-section v-if="scope.opt.materialImage">
              <q-img :src="scope.opt.materialImage" class="material-img" />
            </q-item-section>
          </q-item>
        </template>
        <template v-slot:option="scope">
          <q-item
            v-bind="scope.itemProps"
            class="row full-width items-center justify-between"
          >
            <q-item-section>
              <q-item-label class="title-text-size">{{
                scope.opt.materialName
              }}</q-item-label>
            </q-item-section>
            <q-item-section v-if="scope.opt.materialImage">
              <q-img :src="scope.opt.materialImage" class="material-img" />
            </q-item-section>
          </q-item>
        </template>
      </q-select>
    </div>

    <transition
      appear
      enter-active-class="animated slideInDown"
      v-if="selectedMaterial"
    >
      <div class="row items-center col col-xs-12">
        <span class="sub-text-size">Material Thickness:</span>
        <q-select
          filled
          behavior="menu"
          v-model="selectedMaterialThickness"
          :options="
            selectedMaterial.materialThicknesses
              ? selectedMaterial.materialThicknesses
              : []
          "
          clearable
          class="row col"
          @update:model-value="handleThicknessChange"
        >
          <template v-slot:selected-item="scope">
            <q-item-section>
              <q-item-label>{{ scope.opt.thicknessValue }} mm</q-item-label>
            </q-item-section>
          </template>
          <template v-slot:option="scope">
            <q-item v-bind="scope.itemProps">
              <q-item-section>
                <q-item-label>{{ scope.opt.thicknessValue }} mm</q-item-label>
              </q-item-section>
            </q-item>
          </template>
        </q-select>
      </div>
    </transition>

    <transition
      appear
      enter-active-class="animated slideInDown"
      v-if="selectedMaterialThickness"
    >
      <div class="column q-gutter-y-md">
        <q-separator />

        <q-select
          v-model="selectedOperation"
          label="Pick Operations Settings"
          :options="
            selectedMaterialThickness.thicknessOperations
              ? selectedMaterialThickness.thicknessOperations
              : []
          "
          square
          outlined
          behavior="menu"
          class="settings-selector"
        >
          <template v-slot:selected-item="scope">
            <q-item-section>
              <q-item-label>{{ scope.opt.operationType }}</q-item-label>
            </q-item-section>
          </template>
          <template v-slot:option="scope">
            <q-item v-bind="scope.itemProps">
              <q-item-section>
                <q-item-label>{{ scope.opt.operationType }}</q-item-label>
              </q-item-section>
            </q-item>
          </template>
        </q-select>
      </div>
    </transition>

    <transition
      appear
      enter-active-class="animated slideInDown"
      v-if="
        selectedMaterialThickness &&
        selectedOperation &&
        imageToGcodeConvertorStore.activeImage
      "
    >
      <div>
        <div
          v-if="
            selectedOperation.operationType === Constants.PROFILE_OPTIONS.CUT
          "
          class="column"
        >
          <p class="title-text-size text-bold"><u>Cutting Settings:</u></p>
          <operation-main-settings
            :config
            v-model:power="laserPowerCutting"
            v-model:speed="movementSpeedCutting"
            v-model:tool="laserToolCutting"
            v-model:is-valid-power="isValidLaserPowerCutting"
            v-model:is-valid-speed="isValidMovementSpeedCutting"
          />
        </div>

        <div
          v-else-if="
            selectedOperation.operationType === Constants.PROFILE_OPTIONS.MARK
          "
          class="column"
        >
          <p class="title-text-size text-bold"><u>Marking Settings:</u></p>
          <operation-main-settings
            :config
            v-model:power="laserPowerMarking"
            v-model:speed="movementSpeedMarking"
            v-model:tool="laserToolMarking"
            v-model:is-valid-power="isValidLaserPowerMarking"
            v-model:is-valid-speed="isValidMovementSpeedMarking"
          />
        </div>

        <div
          v-else-if="
            selectedOperation.operationType ===
            Constants.PROFILE_OPTIONS.ENGRAVE
          "
          class="column"
        >
          <p class="title-text-size text-bold">
            <u>Engraving Settings:</u>
          </p>

          <operation-main-settings
            :config
            v-model:power="laserPowerEngraving"
            v-model:speed="movementSpeedEngraving"
            v-model:tool="laserToolEngraving"
            v-model:is-valid-power="isValidLaserPowerEngraving"
            v-model:is-valid-speed="isValidMovementSpeedEngraving"
          />

          <dithering-settings
            :config
            v-model:algorithm="ditheringAlgorithm"
            v-model:resolution="ditheringResolution"
            v-model:grayShift="ditheringGrayShift"
            v-model:block-size="ditheringBlockSize"
            v-model:block-distance="ditheringBlockDistance"
            v-model:is-valid-resolution="isValidDitheringResolution"
            class="q-pt-md"
          />
        </div>
        <q-separator />
      </div>
    </transition>

    <div
      v-if="selectedMaterial && selectedMaterialThickness"
      class="column q-gutter-y-md"
    >
      <q-btn
        label="Save Settings"
        size="2vh"
        color="primary"
        unelevated
        icon="save"
        @click="handleSavingSettings"
        :loading="imageToGcodeConvertorStore.isImageLoading"
        :disable="
          isSaveButtonDisabled || imageToGcodeConvertorStore.isImageLoading
        "
      />
      <q-separator />
      <p class="note sub-text-size">
        Note: Changing the settings here will not modify the main material
        settings.
      </p>
    </div>
  </div>
</template>
<script setup lang="ts">
import { storeToRefs } from 'pinia';
import { Constants } from 'src/constants';
import { useImageToGcodeConvertor } from 'src/stores/image-to-gcode';
import { useMaterialLibraryStore } from 'src/stores/material-library';
import {
  MaterialData,
  MaterialThickness,
  ThicknessOperation,
} from 'src/interfaces/imageToGcode.interface';
import { computed, onMounted, ref } from 'vue';
import { showNotifyMessage } from 'src/services/notify.messages.service';
import { Config } from 'src/interfaces/configSettings.interface';
import OperationMainSettings from 'src/components/GcodeGeneratorTabComponent/components/components/OperationMainSettings.vue';
import DitheringSettings from 'src/components/GcodeGeneratorTabComponent/components/components/DitheringSettings.vue';

const imageToGcodeConvertorStore = useImageToGcodeConvertor();
const materialLibraryStore = useMaterialLibraryStore();

const { materialsList } = storeToRefs(materialLibraryStore);

defineProps<{
  config: Config | null;
}>();

// initial hooks
const selectedMaterial = ref<MaterialData | null>();
const selectedMaterialThickness = ref<MaterialThickness | null>();
const selectedOperation = ref<ThicknessOperation | null>();

// cutting
const movementSpeedCutting = ref<number>(
  imageToGcodeConvertorStore.activeImage?.gcodeSettings.cuttingSettings.speed ??
    0
);
const laserPowerCutting = ref<number>(
  imageToGcodeConvertorStore.activeImage?.gcodeSettings.cuttingSettings.power ??
    0
);
const laserToolCutting = ref<string>(
  imageToGcodeConvertorStore.activeImage?.gcodeSettings.cuttingSettings.tool ??
    ''
);

// marking
const movementSpeedMarking = ref<number>(
  imageToGcodeConvertorStore.activeImage?.gcodeSettings.markingSettings.speed ??
    0
);
const laserPowerMarking = ref<number>(
  imageToGcodeConvertorStore.activeImage?.gcodeSettings.markingSettings.power ??
    0
);
const laserToolMarking = ref<string>(
  imageToGcodeConvertorStore.activeImage?.gcodeSettings.markingSettings.tool ??
    ''
);

// engraving
const movementSpeedEngraving = ref<number>(
  imageToGcodeConvertorStore.activeImage?.gcodeSettings.engravingSettings
    .speed ?? 0
);
const laserPowerEngraving = ref<number>(
  imageToGcodeConvertorStore.activeImage?.gcodeSettings.engravingSettings
    .power ?? 0
);
const laserToolEngraving = ref<string>(
  imageToGcodeConvertorStore.activeImage?.gcodeSettings.engravingSettings
    .tool ?? ''
);
const ditheringAlgorithm = ref<string>(
  imageToGcodeConvertorStore.activeImage?.gcodeSettings.engravingSettings
    .dithering.algorithm ?? ''
);
const ditheringResolution = ref<number>(
  imageToGcodeConvertorStore.activeImage?.gcodeSettings.engravingSettings
    .dithering.resolution ?? 0
);
const ditheringGrayShift = ref<number>(
  imageToGcodeConvertorStore.activeImage?.gcodeSettings.engravingSettings
    .dithering.grayShift ?? 0
);
const ditheringBlockSize = ref<number>(
  imageToGcodeConvertorStore.activeImage?.gcodeSettings.engravingSettings
    .dithering.blockSize ?? 0
);
const ditheringBlockDistance = ref<number>(
  imageToGcodeConvertorStore.activeImage?.gcodeSettings.engravingSettings
    .dithering.blockDistance ?? 0
);

const isValidLaserPowerCutting = ref<boolean>(true);
const isValidMovementSpeedCutting = ref<boolean>(true);
const isValidLaserPowerMarking = ref<boolean>(true);
const isValidMovementSpeedMarking = ref<boolean>(true);
const isValidLaserPowerEngraving = ref<boolean>(true);
const isValidMovementSpeedEngraving = ref<boolean>(true);
const isValidDitheringResolution = ref<boolean>(true);

const handleSavingSettings = () => {
  // save all the settings
  if (
    imageToGcodeConvertorStore.activeImage &&
    selectedMaterial.value &&
    selectedMaterialThickness.value
  ) {
    // main settings
    imageToGcodeConvertorStore.activeImage.gcodeSettings.mainSettings.material =
      selectedMaterial.value.materialName;
    imageToGcodeConvertorStore.activeImage.gcodeSettings.mainSettings.thickness =
      selectedMaterialThickness.value.thicknessValue;

    // cutting settings
    imageToGcodeConvertorStore.activeImage.gcodeSettings.cuttingSettings.speed =
      movementSpeedCutting.value;
    imageToGcodeConvertorStore.activeImage.gcodeSettings.cuttingSettings.power =
      laserPowerCutting.value;
    imageToGcodeConvertorStore.activeImage.gcodeSettings.cuttingSettings.tool =
      laserToolCutting.value;

    // // marking settings
    imageToGcodeConvertorStore.activeImage.gcodeSettings.markingSettings.speed =
      movementSpeedMarking.value;
    imageToGcodeConvertorStore.activeImage.gcodeSettings.markingSettings.power =
      laserPowerMarking.value;
    imageToGcodeConvertorStore.activeImage.gcodeSettings.markingSettings.tool =
      laserToolMarking.value;

    // engraving settings
    imageToGcodeConvertorStore.activeImage.gcodeSettings.engravingSettings.speed =
      movementSpeedEngraving.value;
    imageToGcodeConvertorStore.activeImage.gcodeSettings.engravingSettings.power =
      laserPowerEngraving.value;
    imageToGcodeConvertorStore.activeImage.gcodeSettings.engravingSettings.tool =
      laserToolEngraving.value;
    imageToGcodeConvertorStore.activeImage.gcodeSettings.mainSettings.thickness =
      selectedMaterialThickness.value.thicknessValue;
    imageToGcodeConvertorStore.activeImage.gcodeSettings.engravingSettings.dithering =
      {
        algorithm: ditheringAlgorithm.value,
        resolution: ditheringResolution.value,
        grayShift: ditheringGrayShift.value,
        blockSize: ditheringBlockSize.value,
        blockDistance: ditheringBlockDistance.value,
      };

    changeProfileOptions();

    applySettings();

    const notifyMessage = showNotifyMessage();

    // show notification to confirm saving settings
    notifyMessage.success('Settings saved successfully');
  }
};

const applySettings = () => {
  if (
    imageToGcodeConvertorStore.activeImage?.imageFile?.type ===
      'image/svg+xml' &&
    (imageToGcodeConvertorStore.activeImage.modifiedSVGCutting ||
      imageToGcodeConvertorStore.activeImage.modifiedSVGMarking)
  ) {
    imageToGcodeConvertorStore.applySVGChanges();
  } else if (imageToGcodeConvertorStore.activeImage?.modifiedEngravingImage) {
    imageToGcodeConvertorStore.applyImageChanges();
  }
};

const changeProfileOptions = () => {
  // initial values
  if (imageToGcodeConvertorStore.activeImage) {
    imageToGcodeConvertorStore.activeImage.singleProfileOptions = [
      Constants.PROFILE_OPTIONS.NOTHING,
    ];
    imageToGcodeConvertorStore.activeImage.allProfileOptions = [
      Constants.PROFILE_ALL_OPTIONS.CUSTOM,
    ];
    if (selectedMaterialThickness.value) {
      selectedMaterialThickness.value.thicknessOperations.forEach(
        (operation) => {
          // set profiles options
          switch (operation.operationType) {
            case Constants.PROFILE_OPTIONS.CUT:
              imageToGcodeConvertorStore.activeImage?.singleProfileOptions.push(
                Constants.PROFILE_OPTIONS.CUT
              );
              imageToGcodeConvertorStore.activeImage?.allProfileOptions.push(
                Constants.PROFILE_ALL_OPTIONS.CUT_EVERYTHING
              );
              break;
            case Constants.PROFILE_OPTIONS.MARK:
              imageToGcodeConvertorStore.activeImage?.singleProfileOptions.push(
                Constants.PROFILE_OPTIONS.MARK
              );
              imageToGcodeConvertorStore.activeImage?.allProfileOptions.push(
                Constants.PROFILE_ALL_OPTIONS.MARK_EVERYTHING
              );
              break;
            case Constants.PROFILE_OPTIONS.ENGRAVE:
              imageToGcodeConvertorStore.activeImage?.singleProfileOptions.push(
                Constants.PROFILE_OPTIONS.ENGRAVE
              );
              imageToGcodeConvertorStore.activeImage?.allProfileOptions.push(
                Constants.PROFILE_ALL_OPTIONS.ENGRAVE_EVERYTHING
              );
              break;
          }
        }
      );
    }
  }
};

// make sure all fields contain values
const isSaveButtonDisabled = computed(
  () =>
    !(
      isValidLaserPowerCutting.value &&
      isValidLaserPowerMarking.value &&
      isValidLaserPowerEngraving.value &&
      isValidMovementSpeedCutting.value &&
      isValidMovementSpeedMarking.value &&
      isValidMovementSpeedEngraving.value &&
      isValidDitheringResolution.value
    )
);

const handleRemoveMaterialThickness = () => {
  selectedMaterialThickness.value = null;
};

const handleThicknessChange = (thickness: MaterialThickness | null) => {
  if (thickness) {
    // clear selected operation
    selectedOperation.value = null;

    // Handle operations individually
    thickness.thicknessOperations.forEach((operation) => {
      switch (operation.operationType) {
        case Constants.PROFILE_OPTIONS.CUT:
          laserPowerCutting.value = operation.power;
          movementSpeedCutting.value = operation.speed;
          laserToolCutting.value = operation.tool;
          break;

        case Constants.PROFILE_OPTIONS.MARK:
          laserPowerMarking.value = operation.power;
          movementSpeedMarking.value = operation.speed;
          laserToolMarking.value = operation.tool;
          break;

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
      }
    });
  }
};

const setupSettingBasedOnGcodeSettings = () => {
  if (materialsList.value) {
    selectedMaterial.value = materialsList.value.find(
      (material) =>
        material.materialName ===
        imageToGcodeConvertorStore.activeImage?.gcodeSettings.mainSettings
          .material
    );
    selectedMaterialThickness.value =
      selectedMaterial.value?.materialThicknesses.find(
        (thickness) =>
          thickness.thicknessValue ===
          imageToGcodeConvertorStore.activeImage?.gcodeSettings.mainSettings
            .thickness
      );
  }
};

onMounted(() => {
  setupSettingBasedOnGcodeSettings();
});
</script>
<style scoped>
.settings-selector {
  max-width: max(20vh, 20vw);
}
.material-img {
  flex-direction: row;
  align-self: self-end;
  max-width: max(4vh, 4vw);
  max-height: max(4vh, 4vw);
}
.note {
  color: red;
}

::v-deep(.q-field) {
  font-size: 2vh;
}
</style>
