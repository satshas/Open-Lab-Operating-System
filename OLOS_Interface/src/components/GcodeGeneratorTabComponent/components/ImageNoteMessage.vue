<template>
  <div
    class="column fit rounded-borders q-pa-sm q-gutter-y-sm bg-grey-1"
    style="border: 1px solid grey"
  >
    <span class="text-red text-style text-bold">
      - Images are processed in order of operation type (Engraving → Marking →
      Cutting), starting from the highest Y-axis position value (Down → Up).
    </span>
    <span class="text-red text-style q-pb-sm">
      - Overlapping images may cause unintended results.
    </span>
  </div>
</template>
<style scoped>
.text-style {
  font-size: 1.5vh;
  font-weight: bold;
}
</style>
