<template>
  <div class="row full-width q-gutter-sm items-center justify-end">
    <q-btn
      unelevated
      color="positive"
      size="2vh"
      label="Save Settings"
      @click="showSaveAISettingsDialog"
      :disable="isLoadingImages"
    />
    <q-btn
      unelevated
      color="accent"
      size="2vh"
      label="Load Settings"
      @click="showLoadAISettingsDialog"
      :disable="!aiSettingsList.length || isLoadingImages"
    />
    <q-btn
      unelevated
      color="deep-orange-10"
      size="2vh"
      label="Reset All"
      @click="aiImageGeneratorDialogStore.resetAiImageGeneratorSettings"
      :disable="isLoadingImages"
    />
  </div>
</template>
<script setup lang="ts">
import { storeToRefs } from 'pinia';
import { useAiImageGeneratorStore } from 'src/stores/ai-image-generator';
import { useQuasar } from 'quasar';
import { showNotifyMessage } from 'src/services/notify.messages.service';
import { AISetting } from 'src/interfaces/aiGeneratorImage.interface';
import AiSettingsListDialog from 'src/components/CustomDialogs/FullScreenDialogs/components/AIImageGenerator/components/AISettingsListDialog.vue';
import AiSettingsNameDialog from 'src/components/CustomDialogs/FullScreenDialogs/components/AIImageGenerator/components/AISettingsNameDialog.vue';

const $q = useQuasar();

const aiImageGeneratorDialogStore = useAiImageGeneratorStore();

const { isLoadingImages, aiSettingsList, aiSettingName } = storeToRefs(
  aiImageGeneratorDialogStore
);

const notifyMessage = showNotifyMessage();

const showSaveAISettingsDialog = () => {
  $q.dialog({
    component: AiSettingsNameDialog,
    componentProps: {
      handleSaveAISettings,
    },
  });
};

const handleSaveAISettings = async () => {
  const settingsNamesList = aiSettingsList.value.map(
    (setting: AISetting) => setting.name
  );

  // check if the use is changing an already exist setting
  if (settingsNamesList.includes(aiSettingName.value.trim())) {
    showAlreadyExistAISetting(aiSettingName.value).onOk(() => {
      aiImageGeneratorDialogStore
        .modifyAISetting(aiSettingName.value)
        .then(() => notifyMessage.success('AI Setting modified successfully'))
        .catch((error) => {
          notifyMessage.error(error.message);
        });
    });
  } else {
    aiImageGeneratorDialogStore
      .addAISetting(aiSettingName.value)
      .then(() => notifyMessage.success('AI Setting saved successfully'))
      .catch((error) => {
        notifyMessage.error(error.message);
      });
  }
};

const showAlreadyExistAISetting = (settingsName: string) => {
  return $q.dialog({
    title: `<strong>${settingsName}</strong> setting Already exist!`,
    message: 'Are sure you want to modify this setting?',
    html: true,
    color: 'primary',
    ok: {
      label: 'Yes',
      flat: true,
    },
    cancel: {
      flat: true,
      label: 'No',
    },
  });
};

const showLoadAISettingsDialog = () => {
  $q.dialog({
    component: AiSettingsListDialog,
  });
};
</script>
