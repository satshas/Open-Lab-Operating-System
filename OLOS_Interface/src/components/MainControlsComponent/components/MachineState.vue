<template>
  <div
    :class="[
      'column',
      'q-pa-sm',
      'flex-center',
      'full-width',
      {
        'bg-light-blue-2': state === Constants.IDLE,
        'bg-orange-3': state === Constants.DOOR,
        'bg-light-green-4': state === Constants.RUN,
        'bg-yellow-4': state === Constants.HOLD,
        'bg-white': state === Constants.DISCONNECTED,
        'bg-lime-3': state === Constants.CONNECTING,
        'bg-purple-2': state === Constants.HOMING,
        'bg-red-3': state === Constants.ALARM || isError,
      },
    ]"
    style="border-radius: 10px"
  >
    <span class="state-text">{{ state }}</span>
    <span class="small-note-text">{{ smallMessage }}</span>
  </div>
</template>

<script setup lang="ts">
import { storeToRefs } from 'pinia';
import { Constants } from 'src/constants';
import { useMessageOutputStore } from 'src/stores/message-output';

const store = useMessageOutputStore();
const { state, smallMessage, isError } = storeToRefs(store);
</script>

<style scoped>
.state-text {
  font-size: 3vh;
  color: gray;
  font-weight: bold;
  text-transform: uppercase;
}

.small-note-text {
  font-size: 1.5vh;
  color: gray;
  text-align: center;
}
</style>
