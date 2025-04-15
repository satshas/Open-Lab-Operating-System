<template>
  <div
    v-if="isMachineContainsToolsChanger"
    class="column full-width q-gutter-sm bg-grey-4 rounded-borders"
  >
    <span v-if="machineToolsList" class="text-bold" style="font-size: 2vh">
      Tools Changer
    </span>
    <q-list class="row items-center justify-between q-gutter-md q-pa-md">
      <template v-for="(tool, index) in machineToolsList" :key="index">
        <q-btn
          :label="tool.name"
          color="white"
          text-color="black"
          class="button-size col-lg col-md col-sm-3 col-xs-3"
          push
          @click="toolsChangerStore.useTool(tool)"
          :disable="machineState !== Constants.IDLE"
        />
      </template>
    </q-list>
  </div>
</template>

<script setup lang="ts">
import { Config } from 'src/interfaces/configSettings.interface';
import { storeToRefs } from 'pinia';
import { Constants } from 'src/constants';
import { useMachineStatusStore } from 'src/stores/machine-status';
import { onMounted, ref } from 'vue';
import { configurationSettings } from 'src/services/configuration.loader.service';
import { computed } from 'vue';
import { useToolsChangerStore } from 'src/stores/tools-changer';

const config = ref<Config | null>(null);
const machineStatusStore = useMachineStatusStore();
const toolsChangerStore = useToolsChangerStore();

const { machineState } = storeToRefs(machineStatusStore);

const isMachineContainsToolsChanger = computed(() => {
  if (
    (config.value?.machine_type === Constants.MACHINE_TYPE.LASER_CUTTER &&
      config.value.laser_cutter_settings?.tool_changer) ||
    (config.value?.machine_type === Constants.MACHINE_TYPE.CNC &&
      config.value.cnc_settings?.tool_changer)
  ) {
    return true;
  }
  return false;
});

const machineToolsList = computed(() => {
  if (config.value?.machine_type === Constants.MACHINE_TYPE.LASER_CUTTER) {
    return config.value.laser_cutter_settings?.tools;
  } else if (config.value?.machine_type === Constants.MACHINE_TYPE.CNC) {
    return config.value.cnc_settings?.tools;
  } else return [];
});

onMounted(async () => {
  config.value = await configurationSettings();
});
</script>
<style scoped>
.button-size {
  font-size: 1.5vh;
  height: 7vh;
  max-width: max(15vh, 15vw);
}
</style>
