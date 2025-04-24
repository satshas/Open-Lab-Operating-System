<template>
  <div class="column col-lg-2 col-md-2 col-sm col-xs-12 flex-center q-py-lg">
    <q-btn
      label="Return to zero"
      color="white"
      text-color="blue-grey-10"
      class="button-size"
      push
      @click="returnToZero"
      :disable="isDisabled"
    />
  </div>
</template>

<script setup lang="ts">
import { Constants } from 'src/constants';
import { executeNormalGCommands } from 'src/services/execute.commands.service';

defineProps<{
  isDisabled: boolean;
}>();

const returnToZero = () => {
  executeNormalGCommands(Constants.GRBL_COMMAND_RETURN_ZERO);
};
</script>
<style scoped>
.button-size {
  font-size: 1.5vh;
  width: 12vh;
  height: 12vh;

  i {
    padding: 0;
    margin: -5;
  }
}
</style>
