from typing import Any
from app_settings import Settings
from models.interface_types import InterfaceType
from backend.models.lcmdiffusion_setting import DiffusionTask
from backend.lcm_text_to_image import LCMTextToImage
from time import perf_counter
from backend.image_saver import ImageSaver


class Context:
    def __init__(
        self,
        interface_type: InterfaceType,
        device="cpu",
    ):
        self.interface_type = interface_type.value
        self.lcm_text_to_image = LCMTextToImage(device)
        self._latency = 0

    @property
    def latency(self):
        return self._latency

    def generate_text_to_image(
        self,
        settings: Settings,
        result_dir: str = '',
        reshape: bool = False,
        device: str = "cpu",
        save_images=True,
        save_config=True,
    ) -> Any:
        if (
            settings.lcm_diffusion_setting.use_tiny_auto_encoder
            and settings.lcm_diffusion_setting.use_openvino
        ):
            print(
                "WARNING: Tiny AutoEncoder is not supported in Image to image mode (OpenVINO)"
            )
        tick = perf_counter()
        from state import get_settings

        if (
            settings.lcm_diffusion_setting.diffusion_task
            == DiffusionTask.text_to_image.value
        ):
            settings.lcm_diffusion_setting.init_image = None

        if save_config:
            get_settings().save()

        # pprint(settings.lcm_diffusion_setting.model_dump())
        if not settings.lcm_diffusion_setting.lcm_lora:
            return None
        self.lcm_text_to_image.init(
            device,
            settings.lcm_diffusion_setting,
        )
        images = self.lcm_text_to_image.generate(
            settings.lcm_diffusion_setting,
            reshape,
        )

        if not result_dir:
            result_dir = settings.generated_images.path

        if save_images and settings.generated_images.save_image:
            ImageSaver.save_images(
                result_dir,
                images=images,
                lcm_diffusion_setting=settings.lcm_diffusion_setting,
                format=settings.generated_images.format,
            )
