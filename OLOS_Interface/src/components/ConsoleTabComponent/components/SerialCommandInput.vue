<template>
  <q-input
    ref="serialCommandsInputElement"
    outlined
    color="black"
    bg-color="white"
    dense
    v-model="command"
    placeholder="Type GRBL Command"
    @keyup.enter="onEnter"
    @keydown="handleUserKeyInput"
    @touchstart="
      virtualKeyboardStore.handleInputTouchStart(
        null,
        serialCommandsInputElement
      )
    "
    @blur="virtualKeyboardStore.handleInputBlur"
    @change="handleChangeCommandValue"
    class="row fit flex-center q-gutter-x-sm"
    :disable="isConsoleDisabled()"
    data-kioskboard-specialcharacters="true"
  >
    <template v-slot:append>
      <q-icon
        v-if="command !== ''"
        name="close"
        @click="command = ''"
        class="cursor-pointer"
      />
    </template>

    <template v-slot:after>
      <q-btn
        label="Send"
        @click="onSubmitCommand"
        color="grey-4"
        size="2vh"
        text-color="black"
        :disable="isConsoleDisabled()"
      />
    </template>
  </q-input>
</template>

<script setup lang="ts">
import { storeToRefs } from 'pinia';
import { Constants } from 'src/constants';
import { useMachineStatusStore } from 'src/stores/machine-status';
import { useWebSocketStore } from 'src/stores/websocket-connection';
import { useVirtualKeyboardStore } from 'src/stores/virtual-keyboard';
import { onMounted, ref } from 'vue';
import { QInput } from 'quasar';

const websocketStore = useWebSocketStore();
const machineStatusStore = useMachineStatusStore();
const virtualKeyboardStore = useVirtualKeyboardStore();

const { machineState } = storeToRefs(machineStatusStore);
let keyCount = 0;

const command = ref<string>('');
const formSubmitted = ref<boolean>(false);
const serialCommandsInputElement = ref<QInput | null>(null);

const onSubmitCommand = () => {
  formSubmitted.value = true;

  if (command.value) {
    addCommandToUserHistory(command.value);
    // send to server using websocket
    const req = {
      type: Constants.SERIAL_COMMAND_DATA_TYPE,
      data: {
        command: command.value,
      },
    };
    websocketStore.send(req);
    // reset the value after send
    command.value = '';
  }
};

const onEnter = () => {
  if (command.value || formSubmitted.value) {
    // Handle Enter key press (you can call the same onSubmit function)
    onSubmitCommand();
  }
};

// when user enter a command add it to local storage(user's history)
const addCommandToUserHistory = (command: string) => {
  const history = JSON.parse(localStorage.history);
  if (history) {
    // make sure that the history doesn't exceed 500 commands
    if (history.length >= 500) {
      history.shift();
    }
    history.push(command);
    localStorage.setItem('history', JSON.stringify(history));
  }
};

// // local storage for the user commands (history for user command)
const checkForUserCommandsHistoryStorage = () => {
  // there is no local storage
  if (!localStorage.getItem('history')) {
    createLocalStorage();
  }
};

const createLocalStorage = () => {
  localStorage.setItem('history', JSON.stringify([]));
};

const handleUserKeyInput = (e: KeyboardEvent) => {
  const keyCode = e.keyCode || e.which;
  const history = JSON.parse(localStorage.history);

  if (keyCode == 38 && keyCount !== history.length - 1) {
    e.preventDefault();
    //arrow up key
    // did not reach the last command
    keyCount++;
    command.value = history[history.length - keyCount - 1];
  } else if (keyCode == 40 && keyCount > 0) {
    e.preventDefault();
    //arrow down key
    keyCount--;

    const history = JSON.parse(localStorage.history);
    command.value = history[history.length - keyCount - 1];
  }
};

const isConsoleDisabled = () => {
  if (
    machineState.value === Constants.RUN ||
    machineState.value === Constants.HOLD
  )
    return true;
  else return false;
};

const handleChangeCommandValue = (value: string) => {
  command.value = value;
};
// check if there is a local storage already created
onMounted(() => {
  checkForUserCommandsHistoryStorage();
});
</script>
