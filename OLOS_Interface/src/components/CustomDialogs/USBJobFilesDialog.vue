<template>
  <q-dialog
    v-model="isJobUSBFilesDialogShown"
    transition-show="scale"
    transition-hide="scale"
    persistent
  >
    <q-card class="dialog-box">
      <div class="column fit">
        <q-bar class="row full-width items-center justify-between q-py-lg">
          <span class="dialog-header-font">{{ usbDeviceName }}</span>
          <q-btn
            dense
            flat
            icon="close"
            size="2.5vh"
            @click="usbMonitorStore.closeJobUSBFilesDialog"
          >
            <q-tooltip>Close</q-tooltip>
          </q-btn>
        </q-bar>
        <q-table
          class="header-table-top bg-white fit"
          flat
          row-key="id"
          bordered
          :rows="usbJobFilesListData"
          :columns="columns"
          :dense="$q.screen.lt.md"
          :filter="filter"
          virtual-scroll
          :virtual-scroll-item-size="10"
          :virtual-scroll-sticky-size-start="10"
          :rows-per-page-options="[0]"
          hide-bottom
          :loading="usbJobFilesListData === undefined"
          style="max-height: 80vh"
          no-data-label="Could not find files"
          selection="multiple"
          v-model:selected="selectedJobFiles"
        >
          <template v-slot:top-right>
            <q-input
              ref="searchInputElement"
              dense
              debounce="300"
              v-model="filter"
              color="positive"
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
            <q-btn
              v-if="selectedJobFiles.length"
              label="Upload Selected Files"
              size="1.5vh"
              color="grey-4"
              text-color="black"
              unelevated
              @click="handleUploadMultipleJobFiles"
            />
          </template>

          <template v-slot:body="props">
            <q-tr :props="props" class="bg-white cursor-pointer">
              <q-td>
                <q-checkbox v-model="props.selected" color="grey"></q-checkbox>
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
                    @click="handleUploadJobFileFromUSB(props.row)"
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
import { useQuasar, QTableProps, QInput } from 'quasar';
import { useUSBMonitorStore } from 'src/stores/usb-monitor';
import { useJobsFilesManagementStore } from 'src/stores/jobs-files-management';
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
    style: 'max-width: max(20vh, 20vw);',
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
    field: 'upload',
    style: 'width: max(5vh, 5vw);',
  },
];

const jobManagerStore = useJobsFilesManagementStore();
const usbMonitorStore = useUSBMonitorStore();
const virtualKeyboardStore = useVirtualKeyboardStore();

const { isJobUSBFilesDialogShown, usbDeviceName, usbJobFilesListData } =
  storeToRefs(usbMonitorStore);

const notifyMessage = showNotifyMessage();

// filter for the search bar
const filter = ref<string>('');

const searchInputElement = ref<QInput | null>(null);

// selected job files
const selectedJobFiles = ref<Array<USBFileData>>([]);

const handleUploadMultipleJobFiles = () => {
  selectedJobFiles.value.map((jobFile) => handleUploadJobFileFromUSB(jobFile));
};

const handleUploadJobFileFromUSB = (fileData: USBFileData) => {
  if (!fileData.uploaded) {
    fileData.loading = true;
    jobManagerStore
      .uploadJobFileFromUSB(fileData.path)
      .then(() => {
        notifyMessage.success(Constants.API_SUCCESS_MESSAGES.UPLOAD_MESSAGE);
        fileData.loading = false;
        fileData.uploaded = true;
      })
      .catch((error) => {
        fileData.loading = false;
        notifyMessage.error(error.message);
      });
  }
};

const getShortenPath = (fileData: USBFileData) => {
  // remove the mount point path from the full path
  const path = fileData.path.replace(fileData.mountPoint, '');
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
    font-size: 1.25rem;
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
