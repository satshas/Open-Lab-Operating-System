<template>
  <q-dialog ref="dialogRef" @hide="onDialogHide" :persistent="true">
    <q-card
      ref="renameCardElement"
      class="position-relative full-width q-pa-sm bg-blue-grey-1"
    >
      <q-card-section class="row items-center q-pa-sm">
        <span class="text-bold title-text-size">Rename File</span>
        <q-space />
      </q-card-section>
      <q-card-section>
        <q-input
          ref="renameInputElement"
          v-model="filenameData.filename"
          placeholder="Enter file name"
          :rules="[
            () => !!filenameData.filename || '* Required',
            () =>
              !filesListData.find(
                (file) =>
                  `
                  ${filenameData.filename}.${filenameData.fileExtension}` ===
                  file.file
              ) || 'File name already exist',
          ]"
          reactive-rules
          @touchstart="
            virtualKeyboardStore.handleInputTouchStart(
              renameCardElement,
              renameInputElement
            )
          "
          @blur="virtualKeyboardStore.handleInputBlur"
          @change="handleChangeFilenameValue"
          :suffix="`.${filenameData.fileExtension}`"
          data-kioskboard-specialcharacters="true"
        />
      </q-card-section>

      <q-card-actions align="right">
        <q-btn flat label="Cancel" @click="onDialogCancel" />
        <q-btn
          label="Rename"
          color="primary"
          @click="setNewFilename"
          :disable="isRenameButtonDisabled"
        />
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script setup lang="ts">
import { computed, ref, reactive, onMounted } from 'vue';
import { JobFileData } from 'src/interfaces/jobsFilesManagement.interface';
import { ImageFileData } from 'src/interfaces/imageFilesManagement.interface';
import { useDialogPluginComponent, QInput, QCard } from 'quasar';
import { useVirtualKeyboardStore } from 'src/stores/virtual-keyboard';

const { dialogRef, onDialogHide, onDialogOK, onDialogCancel } =
  useDialogPluginComponent();
defineEmits([...useDialogPluginComponent.emits]);

const props = defineProps<{
  filesListData: JobFileData[] | ImageFileData[];
  filename: string;
  imageData?: ImageFileData;
  renameImage?: (newFilename: string, imageData: ImageFileData) => void;
  renameJob?: (newFilename: string) => void;
}>();

const virtualKeyboardStore = useVirtualKeyboardStore();

const filenameData = reactive({
  filename: '',
  fileExtension: '',
});

const renameInputElement = ref<QInput | null>(null);
const renameCardElement = ref<QCard | null>(null);

// Watch for changes to the input value to make sure if the set button disabled
const isRenameButtonDisabled = computed(() => {
  // make sure it is not an already file name from the files list
  if (
    filenameData.filename.length > 0 &&
    !props.filesListData.find(
      (file) =>
        `${filenameData.filename}.${filenameData.fileExtension}` === file.file
    )
  ) {
    return false;
  }
  return true;
});

// Methods
const setNewFilename = () => {
  const newFilename = filenameData.filename + '.' + filenameData.fileExtension;
  if (props.imageData && props.renameImage) {
    props.renameImage(newFilename, props.imageData);
  } else if (props.renameJob) {
    props.renameJob(newFilename);
  }
  onDialogOK();
};

// Function to update filename and fileExtension based on selectedFilename
const updateFileInfo = () => {
  const fileNameParts = props.filename.split('.');
  filenameData.filename = fileNameParts[0];
  filenameData.fileExtension =
    fileNameParts.length > 1 ? fileNameParts[fileNameParts.length - 1] : '';
};

const handleChangeFilenameValue = (value: string) => {
  filenameData.filename = value;
};
onMounted(() => {
  updateFileInfo();
});
</script>
<style scoped></style>
