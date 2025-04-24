<template>
  <div class="column full-width">
    <span class="title-text-size">AI Models List:</span>
    <q-select
      outlined
      v-model="aiGeneratorSettingsData.model"
      :options="aiModelsList"
      bg-color="white"
      behavior="menu"
      :disable="isLoadingImages"
    >
      <template v-slot:option="scope">
        <q-item v-bind="scope.itemProps">
          <q-item-section>
            <q-item-label>{{ scope.opt }}</q-item-label>
            <q-item-label caption>{{
              getAIModelDescription(scope.opt)
            }}</q-item-label>
          </q-item-section>
        </q-item>
      </template>
    </q-select>
  </div>
</template>
<script setup lang="ts">
import { storeToRefs } from 'pinia';
import { useAiImageGeneratorStore } from 'src/stores/ai-image-generator';
import { Constants } from 'src/constants';

const aiImageGeneratorDialogStore = useAiImageGeneratorStore();

const { aiGeneratorSettingsData, aiModelsList, isLoadingImages } = storeToRefs(
  aiImageGeneratorDialogStore
);

const getAIModelDescription = (modelName: string) => {
  // check if the ai model is supported by olos
  const supportedModels = Constants.SUPPORTED_AI_MODELS.map(
    (model) => model.name
  );
  if (supportedModels.includes(modelName)) {
    return Constants.SUPPORTED_AI_MODELS.find(
      (model) => model.name === modelName
    )?.description;
  }
  return 'This model is not supported. Use on your own risk';
};
</script>
