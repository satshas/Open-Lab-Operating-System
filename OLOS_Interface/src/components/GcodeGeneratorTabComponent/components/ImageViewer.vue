<template>
  <q-card class="fit relative-position" flat bordered>
    <transition
      appear
      enter-active-class="animated fadeIn"
      leave-active-class="animated fadeOut"
    >
      <div ref="imageViewerArea" class="column overflow-hidden">
        <images-source-choices :config="config" />
        <div
          ref="result"
          class="result-container self-center"
          @wheel="handleWheelZoom"
          @touchstart="handleTouchZoom"
        >
          <div ref="stageContainer" id="stage" class="zoom-container"></div>
        </div>
      </div>
    </transition>

    <q-inner-loading :showing="imageToGcodeConvertorStore.isImageLoading">
      <q-spinner-gears size="100" color="primary" />
      <p class="text-h5 q-pa-md">Please wait...</p>
    </q-inner-loading>
  </q-card>
</template>
<script setup lang="ts">
import { Constants } from 'src/constants';
import ImagesSourceChoices from 'src/components/GcodeGeneratorTabComponent/components/components/ImagesSourceChoices.vue';
import { drawSVGOnCanvas } from 'src/services/svg.editor.service';
import { drawImageOnCanvas } from 'src/services/image.editor.service';
import { onMounted, ref, watch } from 'vue';
import { useImageToGcodeConvertor } from 'src/stores/image-to-gcode';
import { Config } from 'src/interfaces/configSettings.interface';

let zoomLevel = 1;
const maxZoomLevel = 10;

const imageToGcodeConvertorStore = useImageToGcodeConvertor();

const imageViewerArea = ref<HTMLDivElement | null>(null);
const stageContainer = ref<HTMLDivElement | null>(null);
const result = ref<HTMLElement | null>(null);

const props = defineProps<{
  config: Config | null;
}>();

const handleWheelZoom = (e: WheelEvent) => {
  e.preventDefault();
  if (result.value) {
    handleZoom(e.deltaY, e.clientX, e.clientY);
  }
};

const handleTouchZoom = (e: TouchEvent) => {
  if (e.cancelable) {
    e.preventDefault();
  }

  if (result.value) {
    const touches = e.touches;
    if (touches.length === 2) {
      const touch1 = touches[0];
      const touch2 = touches[1];
      let prevTouchDistance = Math.sqrt(
        Math.pow(touch1.clientX - touch2.clientX, 2) +
          Math.pow(touch1.clientY - touch2.clientY, 2)
      );

      const handleTouchMove = (moveEvent: TouchEvent) => {
        const moveTouches = moveEvent.touches;
        if (moveTouches.length === 2) {
          const moveTouch1 = moveTouches[0];
          const moveTouch2 = moveTouches[1];
          const touchDistance = Math.sqrt(
            Math.pow(moveTouch1.clientX - moveTouch2.clientX, 2) +
              Math.pow(moveTouch1.clientY - moveTouch2.clientY, 2)
          );
          const deltaY = touchDistance - prevTouchDistance;
          handleZoom(
            -deltaY,
            (moveTouch1.clientX + moveTouch2.clientX) / 2,
            (moveTouch1.clientY + moveTouch2.clientY) / 2
          );
          prevTouchDistance = touchDistance;
        }
      };

      const handleTouchEnd = () => {
        window.removeEventListener('touchmove', handleTouchMove);
        window.removeEventListener('touchend', handleTouchEnd);
      };

      window.addEventListener('touchmove', handleTouchMove);
      window.addEventListener('touchend', handleTouchEnd);
    }
  }
};

const handleZoom = (deltaY: number, clientX: number, clientY: number) => {
  const zoomFactor = deltaY > 0 ? 0.9 : 1.1;

  if (result.value) {
    const rect = result.value.getBoundingClientRect();
    const mouseX = clientX - rect.left;
    const mouseY = clientY - rect.top;

    const offsetX = (mouseX / rect.width) * 100;
    const offsetY = (mouseY / rect.height) * 100;

    const newZoomLevel = zoomLevel * zoomFactor;
    zoomLevel = Math.max(1, Math.min(maxZoomLevel, newZoomLevel)); // Ensure zoom doesn't go below 100%

    result.value.style.transformOrigin = `${offsetX}% ${offsetY}%`;
    result.value.style.transform = `scale(${zoomLevel})`;
  }
};

watch(
  () => [
    imageToGcodeConvertorStore.activeImage?.modifiedSVGCutting,
    imageToGcodeConvertorStore.activeImage?.modifiedSVGMarking,
    imageToGcodeConvertorStore.activeImage?.modifiedEngravingImage,
  ],
  async ([newCuttingImage, newMarkingImage, newEngravingImage]) => {
    // cut
    if (newCuttingImage) {
      const svgCanvas = await drawSVGOnCanvas(
        newCuttingImage as SVGGraphicsElement,
        props.config
      );
      await imageToGcodeConvertorStore.addModifiedImage(
        svgCanvas,
        Constants.PROFILE_OPTIONS.CUT
      );
    } else if (newCuttingImage === null) {
      await imageToGcodeConvertorStore.removeModifiedImage(
        Constants.PROFILE_OPTIONS.CUT
      );
    }

    // mark
    if (newMarkingImage) {
      const svgCanvas = await drawSVGOnCanvas(
        newMarkingImage as SVGGraphicsElement,
        props.config
      );
      await imageToGcodeConvertorStore.addModifiedImage(
        svgCanvas,
        Constants.PROFILE_OPTIONS.MARK
      );
    } else if (newMarkingImage === null) {
      await imageToGcodeConvertorStore.removeModifiedImage(
        Constants.PROFILE_OPTIONS.MARK
      );
    }

    // engrave
    if (newEngravingImage) {
      const imageCanvas = drawImageOnCanvas(
        newEngravingImage as HTMLImageElement,
        props.config
      );
      await imageToGcodeConvertorStore.addModifiedImage(
        imageCanvas,
        Constants.PROFILE_OPTIONS.ENGRAVE
      );
    } else if (newEngravingImage === null) {
      await imageToGcodeConvertorStore.removeModifiedImage(
        Constants.PROFILE_OPTIONS.ENGRAVE
      );
    }

    // main
    if (
      newCuttingImage === null &&
      newMarkingImage === null &&
      newEngravingImage === null
    ) {
      // if there is no modification on the elements, just show the main source image
      imageToGcodeConvertorStore.showSourceImageNode();
    }
  }
);

onMounted(() => {
  // set image viewer container
  if (imageViewerArea.value) {
    imageToGcodeConvertorStore.konvaHelper.setImageViewerArea(
      imageViewerArea.value
    );
  }

  // show stage if it is already created
  if (stageContainer.value) {
    imageToGcodeConvertorStore.konvaHelper.showStageIfExist(
      stageContainer.value
    );
  }
});
</script>
<style scoped>
.remove-image {
  position: absolute;
  top: 0;
  right: 0;
  z-index: 1;
}
.result-container {
  transition: 0.5s ease;
  background-color: white;
}
.zoom-container {
  transition: 0.3s ease;
  min-width: 30vw;
}
</style>
