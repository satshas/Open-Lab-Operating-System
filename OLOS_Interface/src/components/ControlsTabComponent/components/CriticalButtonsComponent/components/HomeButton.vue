<template>
  <q-btn
    icon="home"
    label="Homing"
    stack
    color="grey-4"
    text-color="black"
    class="col q-mb-md q-pa-lg"
    style="font-size: 1.5vh"
    @click="homingMachine()"
    :disable="isHomeBtnDisabled()"
  />
</template>
<script setup lang="ts">
import { storeToRefs } from 'pinia';
import { Constants } from 'src/constants';
import { executeNormalGCommands } from 'src/services/execute.commands.service';
import { useMachineStatusStore } from 'src/stores/machine-status';
import { Config } from 'src/interfaces/configSettings.interface';

const props = defineProps<{
  config: Config | null;
}>();

const store = useMachineStatusStore();
const { machineState } = storeToRefs(store);

const isHomeBtnDisabled = () => {
  if (
    machineState.value !== Constants.IDLE &&
    machineState.value !== Constants.ALARM
  )
    return true;
  return false;
};

const homingMachine = () => {
  if (props.config?.machine_type === Constants.MACHINE_TYPE.VINYL_CUTTER) {
    executeNormalGCommands(Constants.GRBL_COMMAND_HOMING_VINYL_CUTTER);
    executeNormalGCommands(Constants.GRBL_COMMAND_RESET_ZERO_XY);
  } else {
    executeNormalGCommands(Constants.GRBL_COMMAND_HOMING);
  }
};
</script>
