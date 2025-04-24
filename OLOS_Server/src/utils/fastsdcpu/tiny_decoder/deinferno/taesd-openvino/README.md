---
license: mit
pipeline_tag: text-to-image
tags:
  - openvino
  - text-to-image
inference: false
---

## Model Descriptions:

This repo contains OpenVino model files for [madebyollin's Tiny AutoEncoder for Stable Diffusion](https://huggingface.co/madebyollin/taesd).

## Using in 🧨 diffusers:

To install the requirements for this demo, do pip install "optimum-intel[openvino, diffusers]". 

```python
from huggingface_hub import snapshot_download
from optimum.intel.openvino import OVStableDiffusionPipeline
from optimum.intel.openvino.modeling_diffusion import OVModelVaeDecoder, OVModelVaeEncoder, OVBaseModel

# Create class wrappers which allow us to specify model_dir of TAESD instead of original pipeline dir

class CustomOVModelVaeDecoder(OVModelVaeDecoder):
    def __init__(
        self, model, parent_model, ov_config = None, model_dir = None,
    ):
        super(OVModelVaeDecoder, self).__init__(model, parent_model, ov_config, "vae_decoder", model_dir)

class CustomOVModelVaeEncoder(OVModelVaeEncoder):
    def __init__(
        self, model, parent_model, ov_config = None, model_dir = None,
    ):
        super(OVModelVaeEncoder, self).__init__(model, parent_model, ov_config, "vae_encoder", model_dir)

pipe = OVStableDiffusionPipeline.from_pretrained("OpenVINO/stable-diffusion-1-5-fp32", compile=False)

# Inject TAESD

taesd_dir = snapshot_download(repo_id="deinferno/taesd-openvino")
pipe.vae_decoder = CustomOVModelVaeDecoder(model = OVBaseModel.load_model(f"{taesd_dir}/vae_decoder/openvino_model.xml"), parent_model = pipe, model_dir = taesd_dir)
pipe.vae_encoder = CustomOVModelVaeEncoder(model = OVBaseModel.load_model(f"{taesd_dir}/vae_encoder/openvino_model.xml"), parent_model = pipe, model_dir = taesd_dir)

pipe.reshape(batch_size=1, height=512, width=512, num_images_per_prompt=1)
pipe.compile()

prompt = "plant pokemon in jungle"
output = pipe(prompt, num_inference_steps=50, output_type="pil")
output.images[0].save("result.png")
```
