import axios, { AxiosError } from 'axios';
import { defineStore } from 'pinia';
import { Constants } from 'src/constants';
import {
  GcodeGeneratorImageData,
  MaterialData,
  ThicknessOperation,
} from 'src/interfaces/imageToGcode.interface';
import API from 'src/services/API.service';
import { shallowRef } from 'vue';
import { useImageToGcodeConvertor } from './image-to-gcode';

export const useMaterialLibraryStore = defineStore('materialLibrary', {
  state: () => ({
    // material library
    materialsList: shallowRef<Array<MaterialData>>([]),
    imageToGcodeConvertorStore: useImageToGcodeConvertor(),
  }),

  actions: {
    async fetchMaterialLibraryData() {
      await API.getMaterialsList()
        .then((response) => {
          // update material list
          const materialsListData = response.data.data.materialsList;
          this.materialsList = JSON.parse(materialsListData);
        })
        .catch((error: AxiosError | unknown) => {
          if (axios.isAxiosError(error)) {
            throw new Error(error.response?.data.detail);
          }
        });
    },
    async addNewMaterial(material: MaterialData) {
      await API.addNewMaterial(material)
        .then((response) => {
          // update material list
          const materialsListData = response.data.data.materialsList;
          this.materialsList = JSON.parse(materialsListData);
        })
        .catch((error: AxiosError | unknown) => {
          if (axios.isAxiosError(error)) {
            throw new Error(error.response?.data.detail);
          }
        });
    },
    async updateMaterial(material: MaterialData) {
      await API.updateMaterial(material)
        .then((response) => {
          // update material list
          const materialsListData = response.data.data.materialsList;
          this.materialsList = JSON.parse(materialsListData);
          // update gcode settings incase of user updating the same materials data
          if (
            material.materialName ===
            this.imageToGcodeConvertorStore.activeImage?.gcodeSettings
              .mainSettings.material
          ) {
            this.updateGcodeFileSettings(material);
          }
        })
        .catch((error: AxiosError | unknown) => {
          if (axios.isAxiosError(error)) {
            throw new Error(error.response?.data.detail);
          }
        });
    },
    async deleteMaterial(materialId: number) {
      // check if the deleted material is the same material that is used in the settings
      const materialName = this.materialsList.find(
        (material) => material.materialId === materialId
      )?.materialName;

      // set default gcode settings
      if (materialName) {
        this.updateGcodeFileSettings();
      }

      // delete material from database
      await API.deleteMaterial(materialId)
        .then((response) => {
          // update material list
          const materialsListData = response.data.data.materialsList;
          this.materialsList = JSON.parse(materialsListData);
        })
        .catch((error: AxiosError | unknown) => {
          if (axios.isAxiosError(error)) {
            throw new Error(error.response?.data.detail);
          }
        });
    },
    updateGcodeFileSettings(material: MaterialData | null = null) {
      if (material) {
        this.setupGcodeSettings(material);
      } else {
        if (this.materialsList.length) {
          const defaultMaterialSettings = this.materialsList[0];
          this.setupGcodeSettings(defaultMaterialSettings);
        }
      }
    },
    setupGcodeSettings(material: MaterialData) {
      const activeImage = this.imageToGcodeConvertorStore
        .activeImage as GcodeGeneratorImageData;
      if (!activeImage) return;

      // Set material name
      activeImage.gcodeSettings.mainSettings.material = material.materialName;

      // Find or default to the first thickness setting
      const thicknessSettings =
        material.materialThicknesses.find(
          (thickness) =>
            thickness.thicknessValue ===
            activeImage.gcodeSettings.mainSettings.thickness
        ) || material.materialThicknesses[0];

      if (thicknessSettings) {
        // Update thickness
        activeImage.gcodeSettings.mainSettings.thickness =
          thicknessSettings.thicknessValue;

        // Initialize profile options
        activeImage.singleProfileOptions = [Constants.PROFILE_OPTIONS.NOTHING];
        activeImage.allProfileOptions = [Constants.PROFILE_ALL_OPTIONS.CUSTOM];

        // Process thickness operations
        thicknessSettings.thicknessOperations.forEach((operation) =>
          this.applyOperationSettings(activeImage, operation)
        );
      } else {
        // Default to generic material settings if no thickness is available
        this.updateGcodeFileSettings();
      }
    },

    applyOperationSettings(
      activeImage: GcodeGeneratorImageData,
      operation: ThicknessOperation
    ) {
      const operationMapping: Record<string, () => void> = {
        [Constants.PROFILE_OPTIONS.CUT]: () => {
          activeImage.gcodeSettings.cuttingSettings = {
            power: operation.power,
            speed: operation.speed,
            tool: operation.tool,
          };
          activeImage.singleProfileOptions.push(Constants.PROFILE_OPTIONS.CUT);
          activeImage.allProfileOptions.push(
            Constants.PROFILE_ALL_OPTIONS.CUT_EVERYTHING
          );
        },
        [Constants.PROFILE_OPTIONS.MARK]: () => {
          activeImage.gcodeSettings.markingSettings = {
            power: operation.power,
            speed: operation.speed,
            tool: operation.tool,
          };
          activeImage.singleProfileOptions.push(Constants.PROFILE_OPTIONS.MARK);
          activeImage.allProfileOptions.push(
            Constants.PROFILE_ALL_OPTIONS.MARK_EVERYTHING
          );
        },
        [Constants.PROFILE_OPTIONS.ENGRAVE]: () => {
          activeImage.gcodeSettings.engravingSettings = {
            power: operation.power,
            speed: operation.speed,
            tool: operation.tool,
            dithering:
              operation.dithering ??
              Constants.DEFAULT_GCODE_GENERATOR_SETTINGS.ENGRAVING_SETTINGS
                .dithering,
          };
          activeImage.singleProfileOptions.push(
            Constants.PROFILE_OPTIONS.ENGRAVE
          );
          activeImage.allProfileOptions.push(
            Constants.PROFILE_ALL_OPTIONS.ENGRAVE_EVERYTHING
          );
        },
      };

      // Apply the appropriate operation settings
      if (operation.operationType) {
        operationMapping[operation.operationType]?.();
      }
    },
  },
});
