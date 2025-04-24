from argparse import ArgumentParser
import json

import constants
from backend.models.gen_images import ImageFormat
from backend.models.lcmdiffusion_setting import DiffusionTask
from constants import APP_VERSION, DEVICE
from models.interface_types import InterfaceType
from state import get_context, get_settings
from utils import show_system_info

parser = ArgumentParser(description=f"FAST SD CPU {constants.APP_VERSION}")

parser.add_argument(
    "--lcm_model_id",
    type=str,
    help="Model ID or path,Default stabilityai/sd-turbo",
    default="stabilityai/sd-turbo",
)
parser.add_argument(
    "--openvino_lcm_model_id",
    type=str,
    help="OpenVINO Model ID or path,Default rupeshs/sd-turbo-openvino",
    default="rupeshs/sd-turbo-openvino",
)
parser.add_argument(
    "--prompt",
    type=str,
    help="Describe the image you want to generate",
    default="",
)
parser.add_argument(
    "--negative_prompt",
    type=str,
    help="Describe what you want to exclude from the generation",
    default="",
)
parser.add_argument(
    "--image_height",
    type=int,
    help="Height of the image",
    default=512,
)
parser.add_argument(
    "--image_width",
    type=int,
    help="Width of the image",
    default=512,
)
parser.add_argument(
    "--inference_steps",
    type=int,
    help="Number of steps,default : 1",
    default=1,
)
parser.add_argument(
    "--guidance_scale",
    type=float,
    help="Guidance scale,default : 1.0",
    default=1.0,
)

parser.add_argument(
    "--number_of_images",
    type=int,
    help="Number of images to generate ,default : 1",
    default=1,
)
parser.add_argument(
    "--seed",
    type=int,
    help="Seed,default : -1 (disabled) ",
    default=-1,
)
parser.add_argument(
    "--use_openvino",
    action="store_true",
    help="Use OpenVINO model",
)

parser.add_argument(
    "--use_offline_model",
    action="store_true",
    help="Use offline model",
)
parser.add_argument(
    "--clip_skip",
    type=int,
    help="CLIP Skip (1-12), default : 1 (disabled) ",
    default=1,
)
parser.add_argument(
    "--token_merging",
    type=float,
    help="Token merging scale, 0.0 - 1.0, default : 0.0",
    default=0.0,
)

parser.add_argument(
    "--use_safety_checker",
    action="store_true",
    help="Use safety checker",
)
parser.add_argument(
    "--use_lcm_lora",
    action="store_true",
    help="Use LCM-LoRA",
)
parser.add_argument(
    "--base_model_id",
    type=str,
    help="LCM LoRA base model ID,Default Lykon/dreamshaper-8",
    default="Lykon/dreamshaper-8",
)
parser.add_argument(
    "--lcm_lora_id",
    type=str,
    help="LCM LoRA model ID,Default latent-consistency/lcm-lora-sdv1-5",
    default="latent-consistency/lcm-lora-sdv1-5",
)
parser.add_argument(
    "-t",
    "--use_tiny_auto_encoder",
    action="store_true",
    help="Use tiny auto encoder for SD (TAESD)",
)
parser.add_argument(
    "--lora",
    type=str,
    help="LoRA model full path e.g D:\lora_models\CuteCartoon15V-LiberteRedmodModel-Cartoon-CuteCartoonAF.safetensors",
    default=None,
)
parser.add_argument(
    "--lora_weight",
    type=float,
    help="LoRA adapter weight [0 to 1.0]",
    default=0.5,
)

parser.add_argument("--results_directory", type=str,
                    help="Directory to save generated images", default='')

args = parser.parse_args()
app_settings = get_settings()

app_settings.settings.generated_images.save_image = True


context = get_context(InterfaceType.CLI)
config = app_settings.settings

if args.use_openvino:
    config.lcm_diffusion_setting.openvino_lcm_model_id = args.openvino_lcm_model_id
else:
    config.lcm_diffusion_setting.lcm_model_id = args.lcm_model_id

config.lcm_diffusion_setting.prompt = args.prompt
config.lcm_diffusion_setting.negative_prompt = args.negative_prompt
config.lcm_diffusion_setting.image_height = args.image_height
config.lcm_diffusion_setting.image_width = args.image_width
config.lcm_diffusion_setting.guidance_scale = args.guidance_scale
config.lcm_diffusion_setting.number_of_images = args.number_of_images
config.lcm_diffusion_setting.inference_steps = args.inference_steps
config.lcm_diffusion_setting.seed = args.seed
config.lcm_diffusion_setting.use_openvino = args.use_openvino
config.lcm_diffusion_setting.use_tiny_auto_encoder = args.use_tiny_auto_encoder
config.lcm_diffusion_setting.use_lcm_lora = args.use_lcm_lora
config.lcm_diffusion_setting.lcm_lora.base_model_id = args.base_model_id
config.lcm_diffusion_setting.lcm_lora.lcm_lora_id = args.lcm_lora_id
config.lcm_diffusion_setting.diffusion_task = DiffusionTask.text_to_image.value
config.lcm_diffusion_setting.lora.enabled = False
config.lcm_diffusion_setting.lora.path = args.lora
config.lcm_diffusion_setting.lora.weight = args.lora_weight
config.lcm_diffusion_setting.lora.fuse = True
if config.lcm_diffusion_setting.lora.path:
    config.lcm_diffusion_setting.lora.enabled = True
if args.seed > -1:
    config.lcm_diffusion_setting.use_seed = True
else:
    config.lcm_diffusion_setting.use_seed = False
config.lcm_diffusion_setting.use_offline_model = args.use_offline_model
config.lcm_diffusion_setting.clip_skip = args.clip_skip
config.lcm_diffusion_setting.token_merging = args.token_merging
config.lcm_diffusion_setting.use_safety_checker = args.use_safety_checker

# Basic ControlNet settings; if ControlNet is enabled, an image is
# required even in txt2img mode
config.lcm_diffusion_setting.controlnet = None

context.generate_text_to_image(
    settings=config,
    result_dir=args.results_directory
)
