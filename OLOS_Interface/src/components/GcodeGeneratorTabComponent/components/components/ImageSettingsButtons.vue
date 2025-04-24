<template>
  <q-btn-group class="full-width" push spread stretch>
    <q-btn
      stack
      icon="add_photo_alternate"
      label="Add New Image"
      color="grey-7"
      push
      size="1.5vh"
      @click="handleAddNewImage"
    />
    <q-btn
      stack
      icon="photo_library"
      label="Duplicate Selected Image"
      color="grey-7"
      push
      size="1.5vh"
      @click="handleDuplicateSelectedImage"
    />
    <q-btn
      stack
      icon="delete"
      label="Remove Selected Image"
      color="grey-7"
      push
      size="1.5vh"
      @click="handleRemoveSelectedImage"
    />
    <q-btn
      stack
      icon="tune"
      label="Reset Transformations"
      color="grey-7"
      push
      size="1.5vh"
      @click="handleResetTransformation"
    />
  </q-btn-group>
</template>
<script setup lang="ts">
import { useImageToGcodeConvertor } from 'src/stores/image-to-gcode';
import { Config } from 'src/interfaces/configSettings.interface';
import { useQuasar } from 'quasar';
import DuplicateImageDialog from 'src/components/CustomDialogs/DuplicateImageDialog.vue';

const props = defineProps<{
  config: Config | null;
}>();

const $q = useQuasar();

const imageToGcodeConvertorStore = useImageToGcodeConvertor();

const handleAddNewImage = async () => {
  await imageToGcodeConvertorStore.showAddNewImageDialog();
};

const handleDuplicateSelectedImage = async () => {
  $q.dialog({
    component: DuplicateImageDialog,
  });
};

const handleRemoveSelectedImage = () => {
  imageToGcodeConvertorStore.removeActiveImage();
};

const handleResetTransformation = () => {
  if (
    props.config &&
    imageToGcodeConvertorStore.activeImage?.originalImageConfig
  ) {
    imageToGcodeConvertorStore.konvaHelper.updateMetricsManually(
      imageToGcodeConvertorStore.activeImage,
      imageToGcodeConvertorStore.activeImage?.originalImageConfig,
      props.config
    );
  }
};
</script>
