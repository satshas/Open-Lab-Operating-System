<template>
  <div v-if="imageToGcodeConvertorStore.activeImage" class="column">
    <q-table
      ref="mappingTable"
      :columns="getMappingColumns()"
      :rows="getFilteredElements()"
      :row-key="imageToGcodeConvertorStore.activeImage.tableFilterType"
      flat
      selection="multiple"
      v-model:selected="
        imageToGcodeConvertorStore.activeImage.tableSelectedElements
      "
      @selection="handleSelectingRowsProcess"
      virtual-scroll
      :virtual-scroll-item-size="10"
      :virtual-scroll-sticky-size-start="10"
      :rows-per-page-options="[0]"
      hide-bottom
      card-style="font-size: 1.5vh"
    >
      <template v-slot:top>
        <div class="row full-width items-center justify-between">
          <div class="row q-gutter-x-lg flex-center">
            <span class="text-bold">Filtered By:</span>

            <q-radio
              v-model="imageToGcodeConvertorStore.activeImage.tableFilterType"
              val="shape"
              label="Shape"
              size="4vh"
              @update:model-value="handleFilterChange"
            />
            <q-radio
              v-model="imageToGcodeConvertorStore.activeImage.tableFilterType"
              val="color"
              label="Color"
              size="4vh"
              @update:model-value="handleFilterChange"
            />
          </div>
          <div class="row q-gutter-x-lg flex-center">
            <span class="text-bold">All Profiles:</span>
            <q-select
              square
              outlined
              dense
              input-style="font-size: 10px !important"
              behavior="menu"
              :options="
                imageToGcodeConvertorStore.activeImage.allProfileOptions
              "
              v-model="
                imageToGcodeConvertorStore.activeImage.tableProfileAllModels
              "
              @update:model-value="handleChangeOfAllProfiles"
            />
          </div>
        </div>
      </template>

      <template v-slot:header-selection="scope">
        <q-checkbox
          v-model="scope.selected"
          :disable="
            imageToGcodeConvertorStore.activeImage.tableProfileAllModels !==
            Constants.PROFILE_ALL_OPTIONS.CUSTOM
          "
        ></q-checkbox>
      </template>

      <template v-slot:body-selection="scope">
        <q-checkbox
          v-model="scope.selected"
          :disable="scope.row.disable"
        ></q-checkbox>
      </template>

      <template v-slot:body-cell-color="props">
        <q-td key="color" :props="props">
          <div class="row full-width flex-center">
            <div
              class="color-boxes"
              :style="{
                'background-color': props.row.color,
              }"
            ></div>
          </div>
        </q-td>
      </template>

      <template v-slot:body-cell-shapeProfile="props">
        <q-td key="color" :props="props">
          <div class="row full-width flex-center">
            <q-select
              square
              outlined
              dense
              behavior="menu"
              v-model="
                imageToGcodeConvertorStore.activeImage.tableProfileModels[
                  props.row.shape
                ]
              "
              :options="
                imageToGcodeConvertorStore.activeImage.singleProfileOptions
              "
              :disable="props.row.disable"
              @update:model-value="handleChangeOfSVGElementProfile(props)"
            />
          </div>
        </q-td>
      </template>

      <template v-slot:body-cell-colorProfile="props">
        <q-td key="color" :props="props">
          <div class="row full-width flex-center">
            <q-select
              square
              outlined
              behavior="menu"
              v-model="
                imageToGcodeConvertorStore.activeImage.tableProfileModels[
                  props.row.color
                ]
              "
              :options="
                imageToGcodeConvertorStore.activeImage.singleProfileOptions
              "
              style="width: 8vw"
              :disable="props.row.disable"
              @update:model-value="handleChangeOfSVGElementProfile(props)"
            />
          </div>
        </q-td>
      </template>
    </q-table>
  </div>
</template>
<script setup lang="ts">
import { INode } from 'svgson';
import { useImageToGcodeConvertor } from 'src/stores/image-to-gcode';
import { ref, toRaw } from 'vue';
import { QTableProps, QTableSlots } from 'quasar';
import { Constants } from 'src/constants';
import { SelectedElementType } from 'src/interfaces/imageToGcode.interface';

const imageToGcodeConvertorStore = useImageToGcodeConvertor();

const mappingTable = ref<QTableProps | null>(null);
// setup the mapping
const mappingColorColumns: QTableProps['columns'] = [
  {
    name: 'color',
    required: true,
    label: 'Color',
    align: 'center',
    field: (row) => row.color,
  },
  {
    name: 'counter',
    align: 'center',
    label: 'Number of Elements',
    field: (row) => row.elements.length,
    required: false,
  },
  {
    name: 'colorProfile',
    align: 'center',
    label: 'Profile',
    field: '',
    required: false,
  },
];

const mappingShapeColumns: QTableProps['columns'] = [
  {
    name: 'shape',
    required: true,
    label: 'Shape',
    align: 'center',
    field: (row) => row.shape,
  },
  {
    name: 'counter',
    align: 'center',
    label: 'Number of Elements',
    field: (row) => row.elements.length,
    required: false,
  },
  {
    name: 'shapeProfile',
    align: 'center',
    label: 'Profile',
    field: '',
    required: false,
  },
];

const getMappingColumns = () => {
  const activeImage = imageToGcodeConvertorStore.activeImage;
  if (!activeImage) return;

  if (activeImage.tableFilterType === Constants.SVG_ELEMENTS_FILTER.SHAPE) {
    return mappingShapeColumns;
  } else if (
    activeImage.tableFilterType === Constants.SVG_ELEMENTS_FILTER.COLOR
  ) {
    return mappingColorColumns;
  }
};

const getFilteredElements = () => {
  const activeImage = imageToGcodeConvertorStore.activeImage;
  if (!activeImage) return [];

  if (activeImage.tableFilterType === Constants.SVG_ELEMENTS_FILTER.SHAPE) {
    return activeImage.filteredElementsByShape;
  } else if (
    activeImage.tableFilterType === Constants.SVG_ELEMENTS_FILTER.COLOR
  ) {
    return activeImage.filteredElementsByColor;
  }
  return [];
};

const handleSelectingRowsProcess = (
  event: Parameters<NonNullable<QTableProps['onSelection']>>[0]
) => {
  const activeImage = imageToGcodeConvertorStore.activeImage;
  if (!activeImage) return;

  // create an array for all the selected elements
  const selectedElements = event.rows?.reduce((elements, row) => {
    const selectedElement = getSelectedElementData(
      row[activeImage.tableFilterType],
      row.elements,
      event.added
    );
    elements.push(selectedElement);
    return elements;
  }, [] as SelectedElementType[]);

  imageToGcodeConvertorStore.setSvgElementsToModify(selectedElements);
  imageToGcodeConvertorStore.applySVGChanges();
};

const handleChangeOfSVGElementProfile = (
  props: Parameters<QTableSlots['item']>[0]
) => {
  const activeImage = imageToGcodeConvertorStore.activeImage;
  if (!activeImage || !props.selected) return;

  // reset the profiling all option
  activeImage.tableProfileAllModels = Constants.PROFILE_ALL_OPTIONS.CUSTOM;

  const selectedElement = getSelectedElementData(
    props.row[activeImage.tableFilterType],
    props.row.elements,
    activeImage.tableProfileModels[props.row[activeImage.tableFilterType]] !==
      Constants.PROFILE_OPTIONS.NOTHING
  );

  imageToGcodeConvertorStore.setSvgElementsToModify([selectedElement]);
  imageToGcodeConvertorStore.applySVGChanges();
};

const handleChangeOfAllProfiles = () => {
  const activeImage = imageToGcodeConvertorStore.activeImage;
  if (!activeImage) return;

  // disable all rows in case of profile all value other than 'Custom'
  if (
    activeImage.tableProfileAllModels !== Constants.PROFILE_ALL_OPTIONS.CUSTOM
  ) {
    disableAllTableRows();
  } else {
    enableAllTableRows();
  }

  processProfiling();
};

const disableAllTableRows = () => {
  mappingTable.value?.rows.forEach((row) => (row.disable = true));
};

const enableAllTableRows = () => {
  mappingTable.value?.rows.forEach((row) => (row.disable = false));
};

const processProfiling = () => {
  const activeImage = imageToGcodeConvertorStore.activeImage;
  if (!activeImage) return;

  if (activeImage.imageContent.startsWith('data:image/svg+xml;base64')) {
    // Process SVG file
    processProfilingForSVGFile();
  } else {
    // Process other image files
    processProfilingForImageFile();
  }
};

const processProfilingForSVGFile = () => {
  const activeImage = imageToGcodeConvertorStore.activeImage;
  if (!activeImage) return;

  let selectedElements: ReturnType<typeof processAllRows> = [];

  // Define profiling actions as a mapping
  const profilingActions = {
    [Constants.PROFILE_ALL_OPTIONS.CUT_EVERYTHING]:
      Constants.PROFILE_OPTIONS.CUT,
    [Constants.PROFILE_ALL_OPTIONS.MARK_EVERYTHING]:
      Constants.PROFILE_OPTIONS.MARK,
    [Constants.PROFILE_ALL_OPTIONS.ENGRAVE_EVERYTHING]:
      Constants.PROFILE_OPTIONS.ENGRAVE,
  };

  // Determine profiling action
  const action = profilingActions[activeImage.tableProfileAllModels];

  if (action) {
    selectedElements = processAllRows(action, true);
  } else {
    // Default: Do nothing and unselect all rows.
    selectedElements = processAllRows(Constants.PROFILE_OPTIONS.NOTHING, false);
    activeImage.tableSelectedElements = [];
  }

  // Apply modifications
  imageToGcodeConvertorStore.setSvgElementsToModify(selectedElements);
  imageToGcodeConvertorStore.applySVGChanges();
};

const processAllRows = (option: string, isSelectAll: boolean) => {
  const activeImage = imageToGcodeConvertorStore.activeImage;

  if (activeImage) {
    // helper function to get the key value for the profile option
    const profileKeys = Object.keys(Constants.PROFILE_OPTIONS);

    const profile =
      profileKeys.find((key) => Constants.PROFILE_OPTIONS[key] === option) ||
      Constants.PROFILE_OPTIONS.NOTHING;

    // select all rows
    activeImage.tableSelectedElements = mappingTable.value
      ?.rows as QTableProps['selected'];

    // give all rows the specified profile option value
    return activeImage.tableSelectedElements?.reduce((elements, row) => {
      activeImage.tableProfileModels[row[activeImage.tableFilterType]] =
        Constants.PROFILE_OPTIONS[profile];
      const selectedElement = getSelectedElementData(
        row[activeImage.tableFilterType],
        row.elements,
        isSelectAll
      );
      elements.push(selectedElement);
      return elements;
    }, []);
  }

  return [];
};

const processProfilingForImageFile = () => {
  imageToGcodeConvertorStore.applyImageChanges();
};

const handleFilterChange = async () => {
  imageToGcodeConvertorStore.isImageLoading = true;
  // reset table
  imageToGcodeConvertorStore.resetMappingTable();
  // reset modified image
  imageToGcodeConvertorStore.resetAllImageModifications();
  // reset the canvas elements array
  if (imageToGcodeConvertorStore.activeImage)
    imageToGcodeConvertorStore.activeImage.svgElementsToModify = [];
  // finish loading
  imageToGcodeConvertorStore.isImageLoading = false;
};

const getSelectedElementData = (
  identifier: string,
  elements: INode[],
  added: boolean
) => {
  if (imageToGcodeConvertorStore.activeImage) {
    // get the profile type for an element based on its name
    const elementProfileType =
      imageToGcodeConvertorStore.activeImage.tableProfileModels[identifier];

    // create an object that contains the selected element data plus its profile type
    const selectedElement = {
      identifier,
      // prevent modifying the main elements
      // crate a copy of the elements
      elements: structuredClone(toRaw(elements)),
      profileType: elementProfileType,
      added: added,
    };

    return selectedElement;
  }
  return {} as SelectedElementType;
};
</script>
<style scoped>
.color-boxes {
  width: 2rem;
  height: 2rem;
  border: solid black 1px;
  border-radius: 10px;
}

::v-deep(.q-field) {
  font-size: 1.5vh;
  max-width: max(15vh, 15vh);
}
</style>
