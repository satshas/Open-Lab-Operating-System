from diffusers import AutoencoderTiny

from optimum.exporters.openvino import export
from optimum.exporters.onnx.model_configs import VaeDecoderOnnxConfig, VaeEncoderOnnxConfig

taesd = AutoencoderTiny.from_pretrained("madebyollin/taesd")

# Config in root of repo

taesd.save_config("./")

# TAESD Decoder

taesd.forward = lambda latent_sample: taesd.decode(x=latent_sample)
export(model = taesd, config = VaeDecoderOnnxConfig( config = taesd.config, task = "semantic-segmentation"), output = "./vae_decoder/openvino_model.xml")
taesd.save_config("./vae_decoder")

# TAESD Encoder

taesd.forward = lambda sample: {"latent_sample": taesd.encode(x=sample)["latents"]}
export(model = taesd, config = VaeEncoderOnnxConfig( config = taesd.config, task = "semantic-segmentation"), output = "./vae_encoder/openvino_model.xml")
taesd.save_config("./vae_encoder")
