import { defineStore } from 'pinia';
import { QCard, QInput, useQuasar } from 'quasar';
import { VirtualKeyboard } from 'src/services/virtual.keyboard.service';

export const useVirtualKeyboardStore = defineStore('virtualKeyboard', {
  state: () => ({
    keyboard: new VirtualKeyboard(),
    isNativeApplication: useQuasar().platform.is.electron,
  }),

  actions: {
    handleSanitizeNumberInput(event: KeyboardEvent | TouchEvent) {
      return this.keyboard.sanitizeNumberInput(event);
    },
    handleInputTouchStart(
      dialogBoxElement: QCard | null,
      inputElement: QInput | null
    ) {
      if (this.isNativeApplication) {
        this.keyboard.setUpInputBoxElements(dialogBoxElement, inputElement);
        this.keyboard.show();
      }
    },

    handleInputBlur() {
      if (this.isNativeApplication) {
        this.keyboard.remove();
      }
    },
  },
});
