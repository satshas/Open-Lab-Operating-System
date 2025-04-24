<template>
  <q-dialog
    v-model="isUploadedImagesDialogShown"
    transition-show="scale"
    transition-hide="scale"
    persistent
  >
    <q-card class="dialog-box">
      <div class="column fit">
        <q-bar
          class="row full-width text-white bg-brown-5 items-center justify-between q-py-lg"
        >
          <span class="dialog-header-font">Uploaded Images</span>
          <q-btn
            dense
            flat
            icon="close"
            size="2.5vh"
            @click="imageFilesManagementStore.closeUploadedImageFilesDialog"
          >
            <q-tooltip>Close</q-tooltip>
          </q-btn>
        </q-bar>
        <q-table
          class="header-table-top bg-white fit"
          flat
          row-key="file"
          bordered
          :rows="imagesListData"
          :columns="columns"
          :dense="$q.screen.lt.md"
          :filter="filter"
          virtual-scroll
          :virtual-scroll-item-size="10"
          :virtual-scroll-sticky-size-start="10"
          :rows-per-page-options="[0]"
          hide-bottom
          :loading="imagesListData === undefined"
          style="max-height: 80vh"
          no-data-label="Could not find images"
          selection="multiple"
          v-model:selected="selectedImageFiles"
        >
          <template v-slot:top-right>
            <q-input
              ref="searchInputElement"
              dense
              debounce="300"
              color="brown-5"
              v-model="filter"
              placeholder="Search"
              @touchstart="
                virtualKeyboardStore.handleInputTouchStart(
                  null,
                  searchInputElement
                )
              "
              @blur="virtualKeyboardStore.handleInputBlur"
              @change="handleChangeFilterValue"
              data-kioskboard-specialcharacters="true"
            >
              <template v-slot:append>
                <q-icon name="search" />
              </template>
            </q-input>
          </template>

          <template v-slot:top-left>
            <div
              v-if="selectedImageFiles.length && imagesListData.length"
              class="row flex-center q-gutter-md"
            >
              <q-btn
                label="Use Selected Files"
                size="1.5vh"
                color="orange-8"
                unelevated
                @click="handleUseMultipleImageFiles"
              />
              <q-btn
                label="Download Selected Files"
                size="1.5vh"
                color="info"
                unelevated
                @click="handleDownloadMultipleImageFiles"
              />
              <q-btn
                label="Delete Selected Files"
                size="1.5vh"
                color="negative"
                unelevated
                @click="handleDeleteMultipleImageFiles"
              />
            </div>
          </template>

          <template v-slot:header-selection="scope">
            <q-checkbox v-model="scope.selected" color="brown-5"></q-checkbox>
          </template>

          <template v-slot:body="props">
            <q-tr :props="props" class="bg-white cursor-pointer">
              <q-td>
                <q-checkbox
                  v-model="props.selected"
                  color="brown-5"
                ></q-checkbox>
              </q-td>

              <q-td key="file" :props="props">
                <span class="row-sub-text-size">{{ props.row.file }}</span>
              </q-td>

              <q-td key="date" :props="props">
                <span class="row-sub-text-size">{{ props.row.date }}</span>
              </q-td>

              <q-td key="size" :props="props">
                <span class="row-sub-text-size">{{ props.row.size }} KB</span>
              </q-td>

              <q-td key="use" :props="props">
                <q-btn
                  flat
                  @click="handleUseImageFile(props.row)"
                  icon="edit"
                  size="2vh"
                />
              </q-td>

              <q-td key="download" :props="props">
                <q-btn
                  flat
                  @click="handleDownloadImage(props.row)"
                  icon="download"
                  size="2vh"
                />
              </q-td>

              <q-td key="rename" :props="props">
                <q-btn
                  flat
                  @click="handleRenameImage(props.row)"
                  icon="edit_square"
                  size="2vh"
                />
              </q-td>

              <q-td key="delete" :props="props">
                <q-btn
                  flat
                  @click="handleDeleteImage(props.row)"
                  icon="delete_forever"
                  size="2vh"
                />
              </q-td>
            </q-tr>
          </template>
        </q-table>
      </div>
    </q-card>
  </q-dialog>
</template>
<script setup lang="ts">
import { storeToRefs } from 'pinia';
import { ref } from 'vue';
import { useQuasar, QTableProps, QInput } from 'quasar';
import { useImageFilesManagementStore } from 'src/stores/image-files-management';
import { useImageToGcodeConvertor } from 'src/stores/image-to-gcode';
import { useMaterialLibraryStore } from 'src/stores/material-library';
import { useUSBMonitorStore } from 'src/stores/usb-monitor';
import { ImageFileData } from 'src/interfaces/imageFilesManagement.interface';
import { showNotifyMessage } from 'src/services/notify.messages.service';
import { Constants } from 'src/constants';
import RenameFileDialog from 'src/components/CustomDialogs/RenameFileDialog.vue';
import { useVirtualKeyboardStore } from 'src/stores/virtual-keyboard';

const $q = useQuasar();

const columns: QTableProps['columns'] = [
  {
    name: 'file',
    label: 'File',
    align: 'left',
    sortable: true,
    required: true,
    field: (row) => row.file,
    format: (val) => `${val}`,
    style: 'max-width: max(15vh, 15vw);',
  },
  {
    name: 'date',
    label: 'Upload Date',
    align: 'center',
    sortable: true,
    required: false,
    sort: (a, b) => new Date(a).getTime() - new Date(b).getTime(),
    field: (row) => row.date,
    style: 'width: min(5vh, 5vw);',
  },
  {
    name: 'size',
    label: 'File Size',
    align: 'center',
    sortable: true,
    required: false,
    field: (row) => row.size,
    style: 'width: max(5vh, 5vw);',
  },
  {
    name: 'download',
    label: '',
    align: 'center',
    sortable: false,
    required: false,
    field: (row) => row.download,
    style: 'width: max(5vh, 5vw);',
  },
  {
    name: 'rename',
    label: '',
    align: 'center',
    sortable: false,
    required: false,
    field: (row) => row.rename,
    style: 'width: max(5vh, 5vw);',
  },
  {
    name: 'delete',
    label: '',
    align: 'center',
    sortable: false,
    required: false,
    field: (row) => row.delete,
    style: 'width: max(5vh, 5vw);',
  },
  {
    name: 'use',
    label: '',
    align: 'center',
    sortable: false,
    required: false,
    field: (row) => row.use,
    style: 'width: max(5vh, 5vw);',
  },
];

const imageFilesManagementStore = useImageFilesManagementStore();
const imageToGcodeConvertorStore = useImageToGcodeConvertor();
const materialLibraryStore = useMaterialLibraryStore();
const usbMonitorStore = useUSBMonitorStore();
const virtualKeyboardStore = useVirtualKeyboardStore();

const { isUploadedImagesDialogShown, imagesListData } = storeToRefs(
  imageFilesManagementStore
);

const notifyMessage = showNotifyMessage();

// filter for the search bar
const filter = ref<string>('');

const searchInputElement = ref<QInput | null>(null);

// selected job files
const selectedImageFiles = ref<Array<ImageFileData>>([]);

const handleDownloadImage = (imageData: ImageFileData) => {
  $q.dialog({
    title: 'Confirm',
    color: 'primary',
    message: `Would you like to download "${imageData.file}"?`,
    style: {
      backdropFilter: 'none',
    },
    ok: {
      label: 'Yes',
      flat: true,
    },
    cancel: {
      label: 'No',
      flat: true,
    },
  }).onOk(() => downloadImage(imageData));
};

const handleUseMultipleImageFiles = () => {
  selectedImageFiles.value.map((file) => handleUseImageFile(file));
};

const handleDownloadMultipleImageFiles = () => {
  selectedImageFiles.value.map((file) => handleDownloadImage(file));
};

const handleDeleteImage = (imageData: ImageFileData) => {
  $q.dialog({
    title: 'Confirm',
    color: 'primary',
    message: `Would you like to delete "${imageData.file}"?`,
    ok: {
      label: 'Yes',
      flat: true,
    },
    cancel: {
      label: 'No',
      flat: true,
    },
  }).onOk(() => deleteImage(imageData));
};

const handleDeleteMultipleImageFiles = () => {
  selectedImageFiles.value.map((file) => handleDeleteImage(file));
};

const handleUseImageFile = (imageData: ImageFileData) => {
  // get the image data from the system
  imageFilesManagementStore
    .fetchImageFile(imageData.file)
    .then(async (file) => {
      if (file) {
        await imageToGcodeConvertorStore.addNewImageData(file);
        materialLibraryStore.updateGcodeFileSettings();
      }
      imageFilesManagementStore.closeUploadedImageFilesDialog();
    })
    .catch((error) => {
      notifyMessage.error(error.message);
    });
};

const handleRenameImage = (imageData: ImageFileData) => {
  $q.dialog({
    component: RenameFileDialog,
    componentProps: {
      filesListData: imagesListData.value,
      filename: imageData.file,
      imageData,
      renameImage,
    },
  });
};

const renameImage = (newImageName: string, imageData: ImageFileData) => {
  imageFilesManagementStore
    .renameImageFile(imageData.file, newImageName)
    .then(() => {
      notifyMessage.success(Constants.API_SUCCESS_MESSAGES.RENAME_MESSAGE);
    })
    .catch((error) => {
      notifyMessage.error(error.message);
    });
};

const deleteImage = (imageData: ImageFileData) => {
  imageFilesManagementStore
    .deleteImageFile(imageData.file)
    .then(() => {
      usbMonitorStore.checkIfDeletedImageExistInUSBImageFiles(imageData.file);
      notifyMessage.success(Constants.API_SUCCESS_MESSAGES.DELETE_MESSAGE);
    })
    .catch((error) => notifyMessage.error(error.message));
};

const downloadImage = (imageData: ImageFileData) => {
  imageFilesManagementStore
    .downloadImageFile(imageData.file)
    .then(() =>
      notifyMessage.success(Constants.API_SUCCESS_MESSAGES.DOWNLOAD_MESSAGE)
    )
    .catch((error) => notifyMessage.error(error.message));
};

const handleChangeFilterValue = (value: string) => {
  filter.value = value;
};
</script>

<style scoped lang="scss">
.dialog-box {
  min-width: 90vw;
}

.dialog-header-font {
  font-size: 3vh;
  font-weight: bold;
}

.header-table-top {
  thead tr:first-child th {
    border-bottom: solid 1px;
  }
  thead tr:first-child th {
    /* bg color is important for th; just specify one */
    background-color: #fff !important;
  }
  thead tr:first-child th {
    font-weight: bold;
    font-size: 2vh;
  }
}
.q-table__top,
thead tr th {
  position: sticky;
  z-index: 1;
}
/* prevent scrolling behind sticky top row on focus */
tbody {
  /* height of all previous header rows */
  scroll-margin-top: 48px;
}

.row-sub-text-size {
  font-size: 1.5vh;
}
</style>
