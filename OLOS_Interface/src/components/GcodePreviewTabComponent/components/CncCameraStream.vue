<template>
  <div class="column fit q-gutter-y-md">
    <u class="row message-text text-bold">Webcam Stream:</u>
    <canvas
      v-if="cameraFrame"
      ref="webcamCanvas"
      class="fit camera-stream"
    ></canvas>
  </div>
</template>

<script setup lang="ts">
import { storeToRefs } from 'pinia';
import { useGcodePreviewStore } from 'src/stores/gcode-preview';
import { ref, watch } from 'vue';

const webcamCanvas = ref<HTMLCanvasElement | null>(null);

const gcodePreviewStore = useGcodePreviewStore();
const { cameraFrame } = storeToRefs(gcodePreviewStore);

watch(cameraFrame, (newCameraFrame) => {
  if (newCameraFrame && webcamCanvas.value) {
    const context = webcamCanvas.value.getContext('2d');
    const img = new Image();
    img.style.width = '100px';
    img.style.height = '100px';

    img.onload = function () {
      if (webcamCanvas.value)
        context?.drawImage(
          img,
          0,
          0,
          webcamCanvas.value.width,
          webcamCanvas.value.height
        );
    };
    img.src = newCameraFrame;
  } else {
  }
});
</script>
<style scoped>
.camera-stream {
  width: 50%;
  height: 50%;
}
</style>
