<template>
  <div class="column flex-center col-lg-4 col-md-4 col-sm col-xs-12 q-pb-md">
    <div class="row q-gutter-md">
      <div class="column self-center justify-around">
        <div class="row q-gutter-x-md q-pb-md">
          <q-btn
            label="X0"
            color="white"
            stack
            text-color="blue-grey-10"
            class="button-size"
            push
            @click="resetXToZero"
            :disable="isDisabled"
          />
          <q-btn
            label="Y0"
            color="white"
            stack
            text-color="blue-grey-10"
            class="button-size"
            push
            @click="resetYToZero"
            :disable="isDisabled"
          />
        </div>
        <q-btn
          label="XY0"
          color="white"
          stack
          text-color="blue-grey-10"
          class="wide-button-size"
          push
          @click="resetXYToZero"
          :disable="isDisabled"
        />
      </div>
      <q-btn
        v-if="config?.machine_type !== Constants.MACHINE_TYPE.VINYL_CUTTER"
        label="Z0"
        color="white"
        stack
        class="long-button-size"
        text-color="blue-grey-10"
        push
        @click="resetZToZero"
        :disable="isDisabled"
      />
    </div>
  </div>
</template>
<script setup lang="ts">
import { Constants } from 'src/constants';
import { Config } from 'src/interfaces/configSettings.interface';
import { executeNormalGCommands } from 'src/services/execute.commands.service';
import { useMachineStatusStore } from 'src/stores/machine-status';

defineProps<{
  isDisabled: boolean;
  config: Config | null;
}>();

const store = useMachineStatusStore();

const resetXToZero = () => {
  executeNormalGCommands(Constants.GRBL_COMMAND_RESET_ZERO_X);
  store.resetXJobPosition();
};

const resetYToZero = () => {
  executeNormalGCommands(Constants.GRBL_COMMAND_RESET_ZERO_Y);
  store.resetYJobPosition();
};

const resetXYToZero = () => {
  executeNormalGCommands(Constants.GRBL_COMMAND_RESET_ZERO_XY);
  store.resetXYJobPosition();
};

const resetZToZero = () => {
  executeNormalGCommands(Constants.GRBL_COMMAND_RESET_ZERO_Z);
  store.resetZJobPosition();
};
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
.wide-button-size {
  font-size: 1.5vh;
  height: 7vh;
}
.long-button-size {
  font-size: 1.5vh;
  width: 7vh;
}
</style>
