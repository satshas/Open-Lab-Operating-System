<template>
  <div
    class="column col-lg col-md col-sm-12 col-xs-12 q-gutter-sm items-center q-py-lg"
  >
    <div class="row col q-px-md q-gutter-x-md">
      <q-btn
        icon="arrow_drop_down"
        round
        color="white"
        text-color="blue-grey-10"
        class="button-size rotate-135"
        @click="jogControlsStore.XYZJog(-xJogStep, yJogStep, 0, xyJogSpeed)"
        :disable="isDisabled"
      />
      <q-btn
        icon="arrow_drop_up"
        label="Y"
        color="white"
        stack
        text-color="blue-grey-10"
        class="button-size"
        push
        @click="jogControlsStore.XYZJog(0, yJogStep, 0, xyJogSpeed)"
        :disable="isDisabled"
      />
      <q-btn
        icon="arrow_drop_up"
        round
        color="white"
        text-color="blue-grey-10"
        class="button-size rotate-45"
        @click="jogControlsStore.XYZJog(xJogStep, yJogStep, 0, xyJogSpeed)"
        :disable="isDisabled"
      />
    </div>
    <div class="row col q-px-md q-gutter-x-md items-center">
      <q-btn
        label="X"
        icon="arrow_left"
        class="button-size"
        color="white"
        text-color="blue-grey-10"
        push
        @click="jogControlsStore.XYZJog(-xJogStep, 0, 0, xyJogSpeed)"
        :disable="isDisabled"
      />
      <q-btn class="button-size" disable flat />
      <q-btn
        label="X"
        class="button-size"
        icon-right="arrow_right"
        color="white"
        text-color="blue-grey-10"
        push
        @click="jogControlsStore.XYZJog(xJogStep, 0, 0, xyJogSpeed)"
        :disable="isDisabled"
      />
    </div>
    <div class="row col q-px-md q-gutter-x-md items-end">
      <q-btn
        icon="arrow_drop_down"
        round
        class="button-size rotate-45"
        color="white"
        text-color="blue-grey-10"
        @click="jogControlsStore.XYZJog(-xJogStep, -yJogStep, 0, xyJogSpeed)"
        :disable="isDisabled"
      />
      <q-btn
        stack
        class="button-size"
        color="white"
        text-color="blue-grey-10"
        push
        @click="jogControlsStore.XYZJog(0, -yJogStep, 0, xyJogSpeed)"
        :disable="isDisabled"
      >
        <span>Y</span>
        <q-icon name="arrow_drop_down" />
      </q-btn>
      <q-btn
        icon="arrow_drop_up"
        round
        class="button-size rotate-135"
        color="white"
        text-color="blue-grey-10"
        @click="jogControlsStore.XYZJog(xJogStep, -yJogStep, 0, xyJogSpeed)"
        :disable="isDisabled"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { storeToRefs } from 'pinia';
import { useJogControlsStore } from 'src/stores/jog-controls';

defineProps<{
  isDisabled: boolean;
}>();

const jogControlsStore = useJogControlsStore();
const { xJogStep, yJogStep, xyJogSpeed } = storeToRefs(jogControlsStore);
</script>
<style scoped>
.button-size {
  font-size: 1.5vh;
  width: 7vh;
  height: 7vh;

  i {
    padding: 0;
    margin: -5;
  }
}
</style>
