<template>
  <q-dialog
    v-model="isUSBImageFilesDialogShown"
    transition-show="scale"
    transition-hide="scale"
    persistent
  >
    <q-card class="dialog-box">
      <div class="column fit">
        <q-bar
          class="row full-width text-white bg-purple-5 items-center justify-between q-py-lg"
        >
          <span class="dialog-header-font">{{ usbDeviceName }}</span>
          <q-btn
            dense
            flat
            icon="close"
            size="2.5vh"
            @click="usbMonitorStore.closeImageUSBFilesDialog"
          >
            <q-tooltip>Close</q-tooltip>
          </q-btn>
        </q-bar>
        <q-table
          class="header-table-top bg-white fit"
          flat
          row-key="id"
          bordered
          :rows="usbImageFilesListData"
          :columns="columns"
          :dense="$q.screen.lt.md"
          :filter="filter"
          virtual-scroll
          :virtual-scroll-item-size="10"
          :virtual-scroll-sticky-size-start="10"
          :rows-per-page-options="[0]"
          hide-bottom
          :loading="usbImageFilesListData === undefined"
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
              color="purple-5"
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
              v-if="selectedImageFiles.length"
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
                label="Upload Selected Files"
                size="1.5vh"
                color="teal-5"
                unelevated
                @click="handleUploadMultipleImageFiles"
              />
            </div>
          </template>

          <template v-slot:header-selection="scope">
            <q-checkbox v-model="scope.selected" color="purple-5"></q-checkbox>
          </template>

          <template v-slot:body="props">
            <q-tr :props="props" class="bg-white cursor-pointer">
              <q-td>
                <q-checkbox
                  v-model="props.selected"
                  color="purple-5"
                ></q-checkbox>
              </q-td>
              <q-td key="path" :props="props">
                <span class="row-sub-text-size">{{
                  getShortenPath(props.row)
                }}</span>
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
                  @click="handleUseImageFileFromUSB(props.row)"
                  icon="edit"
                  size="2vh"
                />
              </q-td>
              <q-td key="upload" :props="props">
                <div v-if="!props.row.uploaded">
                  <q-spinner
                    v-if="props.row.loading"
                    color="positive"
                    size="2vh"
                    :thickness="5"
                  />
                  <q-btn
                    flat
                    v-else
                    @click="handleUploadImageFileFromUSB(props.row)"
                    icon="upload"
                    size="2vh"
                  />
                </div>
                <q-icon v-else name="task_alt" color="positive" size="2vh" />
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
import { useQuasar, QTableProps, QInput, QCard } from 'quasar';
import { useUSBMonitorStore } from 'src/stores/usb-monitor';
import { useImageFilesManagementStore } from 'src/stores/image-files-management';
import { useImageToGcodeConvertor } from 'src/stores/image-to-gcode';
import { useMaterialLibraryStore } from 'src/stores/material-library';
import { USBFileData } from 'src/interfaces/usbMonitor.interface';
import { showNotifyMessage } from 'src/services/notify.messages.service';
import { Constants } from 'src/constants';
import { useVirtualKeyboardStore } from 'src/stores/virtual-keyboard';

const $q = useQuasar();

const columns: QTableProps['columns'] = [
  {
    name: 'path',
    label: 'File Path',
    align: 'left',
    sortable: true,
    required: true,
    field: (row) => row.file,
    format: (val) => `${val}`,
    style: 'max-width: max(15vh, 15vw);',
  },
  {
    name: 'file',
    label: 'USB File',
    align: 'left',
    sortable: true,
    required: true,
    field: (row) => row.file,
    format: (val) => `${val}`,
    style: 'max-width: max(15vh, 15vw);',
  },
  {
    name: 'date',
    label: 'Creation Date',
    align: 'center',
    sortable: true,
    required: false,
    sort: (a, b) => new Date(a).getTime() - new Date(b).getTime(),
    field: (row) => row.date,
    style: 'width: max(5vh, 5vw);',
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
    name: 'upload',
    label: '',
    align: 'center',
    sortable: true,
    required: false,
    field: (row) => row.uploaded,
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

const usbMonitorStore = useUSBMonitorStore();
const imageFilesManagementStore = useImageFilesManagementStore();
const imageToGcodeConvertorStore = useImageToGcodeConvertor();
const materialLibraryStore = useMaterialLibraryStore();
const virtualKeyboardStore = useVirtualKeyboardStore();

const { isUSBImageFilesDialogShown, usbDeviceName, usbImageFilesListData } =
  storeToRefs(usbMonitorStore);

// const { imageFile } = storeToRefs(imageToGcodeConvertorStore);

const notifyMessage = showNotifyMessage();

// filter for the search bar
const filter = ref<string>('');

const searchInputElement = ref<QInput | null>(null);

// selected job files
const selectedImageFiles = ref<Array<USBFileData>>([]);

const handleUseMultipleImageFiles = () => {
  selectedImageFiles.value.map(
    async (imageFile) => await handleUseImageFileFromUSB(imageFile)
  );
};

const handleUploadMultipleImageFiles = () => {
  selectedImageFiles.value.map(
    async (imageFile) => await handleUploadImageFileFromUSB(imageFile)
  );
};

const handleUploadImageFileFromUSB = (fileData: USBFileData) => {
  return new Promise<void>((resolve, reject) => {
    fileData.loading = true;
    // incase the file is not uploaded before
    if (!fileData.uploaded) {
      imageFilesManagementStore
        .uploadImageFileFromUSB(fileData.path)
        .then(() => {
          notifyMessage.success(Constants.API_SUCCESS_MESSAGES.UPLOAD_MESSAGE);
          fileData.loading = false;
          fileData.uploaded = true;
          resolve();
        })
        .catch((error) => {
          fileData.loading = false;
          notifyMessage.error(error.message);
          reject(error);
        });
    }
    resolve();
  });
};

const handleUseImageFileFromUSB = async (fileData: USBFileData) => {
  // first upload automatically the image to the system
  await handleUploadImageFileFromUSB(fileData).then(() => {
    // get the image data from the system
    imageFilesManagementStore
      .fetchImageFile(fileData.file)
      .then(async (image) => {
        if (image) {
          await imageToGcodeConvertorStore.addNewImageData(image);
          // update the gcode settings for the image
          materialLibraryStore.updateGcodeFileSettings();
        }
        // close the dialog after uploading all the images and using them
        usbMonitorStore.closeImageUSBFilesDialog();
      })
      .catch((error) => {
        notifyMessage.error(error.message);
      });
  });
};

const getShortenPath = (imageData: USBFileData) => {
  // remove the mount point path from the full path
  const path = imageData.path.replace(imageData.mountPoint, '');
  // normalize the path for all operation systems paths
  const normalizedPath = path.replace(/\\/g, '/');
  const pathParts = normalizedPath.split('/');

  // Get the last two directories
  const lastTwoDirectories = pathParts.slice(-3, -1).join('/') + '/';
  return lastTwoDirectories;
};

const handleChangeFilterValue = (value: string) => {
  filter.value = value;
};
</script>

<style lang="scss">
.dialog-box {
  min-width: 80vw;
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
