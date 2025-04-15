<template>
  <transition
    appear
    enter-active-class="animated  fadeIn"
    leave-active-class="animated fadeOut"
  >
    <q-btn
      v-if="isGenerateGcodeButtonDisplayed"
      label="Generate Gcode"
      icon="note_add"
      size="2vh"
      color="primary"
      unelevated
      class="self-start"
      @click="handleGenerateGcode"
      :loading="isGeneratingFile"
    />
  </transition>
</template>

<script setup lang="ts">
import { storeToRefs } from 'pinia';
import { useQuasar } from 'quasar';
import { useTabsStore } from 'src/stores/active-tab';
import { useJobsFilesManagementStore } from 'src/stores/jobs-files-management';
import { showNotifyMessage } from 'src/services/notify.messages.service';
import { useImageToGcodeConvertor } from 'src/stores/image-to-gcode';
import { useMachineStatusStore } from 'src/stores/machine-status';
import { svgElementToBase64 } from 'src/services/svg.editor.service';
import { drawImageOnCanvas } from 'src/services/image.editor.service';
import { Constants } from 'src/constants';
import {
  GcodeFileData,
  ModifiedImageData,
} from 'src/interfaces/imageToGcode.interface';
import { Config } from 'src/interfaces/configSettings.interface';
import GeneratedGcodeFileName from 'src/components/CustomDialogs/GeneratedGcodeFileName.vue';
import { ref, computed } from 'vue';

const props = defineProps<{
  config: Config | null;
}>();

const $q = useQuasar();

const tabsStore = useTabsStore();
const imageToGcodeConvertorStore = useImageToGcodeConvertor();
const jobManagerStore = useJobsFilesManagementStore();
const machineStatusStore = useMachineStatusStore();

const { navList } = storeToRefs(tabsStore);
const { filesListData } = storeToRefs(jobManagerStore);
const { machineState } = storeToRefs(machineStatusStore);

const notifyMessage = showNotifyMessage();
const isGeneratingFile = ref<boolean>(false);
const isGenerateGcodeButtonDisplayed = computed(
  () =>
    imageToGcodeConvertorStore.generatorImagesDataList.filter(
      (imageData) =>
        imageData.modifiedSVGCutting ||
        imageData.modifiedSVGMarking ||
        imageData.modifiedEngravingImage
    ).length && !imageToGcodeConvertorStore.isImageLoading
);

const handleGenerateGcode = async () => {
  // array for saving each image's data
  const modifiedImagesData = [] as Array<ModifiedImageData>;

  // a flag to check if all the images modified or not
  let areAllImagesModified = true;

  for (const imageData of imageToGcodeConvertorStore.generatorImagesDataList) {
    if (
      imageData.modifiedSVGCutting ||
      imageData.modifiedSVGMarking ||
      imageData.modifiedEngravingImage
    ) {
      // create svg and image blobs
      const cuttingSVGBlob = imageData.modifiedSVGCutting
        ? svgElementToBase64(imageData.modifiedSVGCutting)
        : null;
      const markingSVGBlob = imageData.modifiedSVGMarking
        ? svgElementToBase64(imageData.modifiedSVGMarking)
        : null;
      const engravedImageBlob = imageData.modifiedEngravingImage
        ? drawImageOnCanvas(
            imageData.modifiedEngravingImage,
            props.config
          ).toDataURL('image/png')
        : null;

      // add new image Data into the images data array
      modifiedImagesData.push({
        modifiedSVGCutting: cuttingSVGBlob,
        modifiedSVGMarking: markingSVGBlob,
        modifiedEngravingImage: engravedImageBlob,
        gcodeSettings: imageData.gcodeSettings,
      });
    } else {
      // show a warning dialog for the user to check the status of all uploaded images
      showNotAllImagesModifiedDialog();
      areAllImagesModified = false;
      break;
    }
  }

  if (areAllImagesModified) {
    // Sort the images based on y-axis in descending order
    const sortedModifiedImagesData = modifiedImagesData.sort((a, b) => {
      const aMetrics = a.gcodeSettings.mainSettings.metrics;
      const bMetrics = b.gcodeSettings.mainSettings.metrics;

      // Compare by y first
      if (aMetrics.y !== bMetrics.y) {
        return aMetrics.y - bMetrics.y;
      }
      // If y is the same, compare by x
      return aMetrics.x - bMetrics.x;
    });

    // ask the user to enter the job name
    showFileNameDialog().onOk((name: string) => {
      const filename = `${name}.nc`;
      const filesNameList = filesListData.value.map(
        (fileData) => fileData.file
      );
      // file name already exist
      if (filesNameList.includes(filename)) {
        showAlreadyExistFileAlert().onOk(() =>
          startGeneratingGcode(filename, sortedModifiedImagesData)
        );
      } else {
        startGeneratingGcode(filename, sortedModifiedImagesData);
      }
    });
  }
};

const startGeneratingGcode = (
  filename: string,
  modifiedImagesData: Array<ModifiedImageData>
) => {
  isGeneratingFile.value = true;

  const generatingDialog = showGeneratingFileDialog();

  // prepare gcode file data
  const gcodeFileData = {
    name: filename,
    modifiedImagesData,
  } as GcodeFileData;

  // api call
  jobManagerStore
    .generateGcodeFile(gcodeFileData)
    .then(() => {
      if (isGeneratingFile.value) {
        generatingDialog.hide();
        isGeneratingFile.value = false;
        showDoneGeneratingFileDialog();
      }
    })
    .catch((error) => {
      isGeneratingFile.value = false;
      notifyMessage.error(error.message);
    });
  // incase the user cancel the generating process
  generatingDialog.onCancel(async () => {
    if (isGeneratingFile.value) {
      isGeneratingFile.value = false;
      await jobManagerStore.cancelGenerateGcodeFile();
    }
  });
};

const showFileNameDialog = () => {
  return $q.dialog({
    component: GeneratedGcodeFileName,
  });
};

const showGeneratingFileDialog = () => {
  return $q.dialog({
    title: 'Generating...',
    progress: {
      color: 'primary',
    },
    persistent: true,
    ok: false,
    cancel: true,
  });
};

const showNotAllImagesModifiedDialog = () => {
  $q.dialog({
    color: 'primary',
    title: 'Modified Images',
    message:
      'Not all uploaded images in the viewer have been modified. Please ensure all images are updated or remove any unused ones.',
    progress: false,
    ok: true,
  });
};

const showAlreadyExistFileAlert = () => {
  return $q.dialog({
    title: 'Gcode Generator',
    html: true,
    color: 'primary',
    message: 'Do you want to overwrite an already exist job file?',
    ok: {
      color: 'negative',
      label: 'Yes ⚠️',
      push: false,
    },
    cancel: {
      flat: true,
      label: 'No',
    },
  });
};

const showDoneGeneratingFileDialog = () => {
  $q.dialog({
    color: 'primary',
    title: 'Done!',
    message: 'File generated and saved successfully in the Jobs Manager',
    progress: false,
    ok: {
      color: 'primary',
      label: 'Jobs Manager',
      push: false,
      disable: machineState.value === Constants.RUN,
    },
    cancel: true,
  }).onOk(() => tabsStore.changeTab(navList.value.files));
};
</script>
