<template>
  <div class="column col fit items-center q-gutter-y-md q-pa-lg">
    <console-output />
    <serial-command-input />
    <debugger-button />
  </div>
</template>

<script setup lang="ts">
import SerialCommandInput from './components/SerialCommandInput.vue';
import ConsoleOutput from './components/ConsoleOutput.vue';
import DebuggerButton from './components/DebuggerButton.vue';
</script>
