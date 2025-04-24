import io
import os
import re
import subprocess
import tempfile
import numpy as np
from PIL import Image, ImageOps

from core.constants import CoreConstants as constants
from utils.image_convertor_helper import convert_base64_to_image
from utils.configuration_loader import ConfigurationLoader

# handle all sizes of images
Image.MAX_IMAGE_PIXELS = None


class ImageToGcodeGenerator:
    def __init__(self):
        # configuration settings
        self._config = ConfigurationLoader.from_yaml()
        self._images_bounding_box = None

    @classmethod
    def generate_gcode(cls, gcode_file_data):
        generator = cls()
        modified_images_data_list = gcode_file_data.modifiedImagesData

        # full gcode file content
        gcode_file_content = ''

        engraving_images_data, marking_images_data, cutting_images_data, materials_settings_list = \
            generator._classify_images_data(modified_images_data_list)

        # add the material setting at the top of the file
        gcode_file_content += generator._add_material_settings_comment(
            materials_settings_list)

        gcode_file_content += generator._add_images_bounding_box_comment()

        if engraving_images_data:
            gcode_file_content += generator._generate_gcode_for_images_data(
                images_data=engraving_images_data, process=constants.IMAGE_GENERATOR_ENGRAVE_PROCESS)

        if marking_images_data:
            gcode_file_content += generator._generate_gcode_for_images_data(
                images_data=marking_images_data, process=constants.IMAGE_GENERATOR_MARK_PROCESS)

        if cutting_images_data:
            gcode_file_content += generator._generate_gcode_for_images_data(
                images_data=cutting_images_data, process=constants.IMAGE_GENERATOR_CUT_PROCESS)

        # Add some modification to the generated gcode
        gcode_file_content = generator._modify_gcode_content(
            gcode_file_content)

        return gcode_file_content.encode('utf-8')

    def _classify_images_data(self, images_list):
        # list to group the images data based operation
        engraving_images_data = []
        marking_images_data = []
        cutting_images_data = []

        # list for material settings for all the images
        materials_settings_list = []

        for image_data in images_list:
            # Prepare images data based on image processing type
            if image_data.modifiedEngravingImage:
                engraving_image_data, engraving_image_settings = self._prepare_image_data(
                    image=image_data.modifiedEngravingImage,
                    settings=image_data.gcodeSettings,
                    process=constants.IMAGE_GENERATOR_ENGRAVE_PROCESS)

                engraving_images_data.append({
                    'image': engraving_image_data,
                    'settings': engraving_image_settings
                })

            if image_data.modifiedSVGMarking:
                marking_image_data, marking_image_settings = self._prepare_image_data(
                    image=image_data.modifiedSVGMarking,
                    settings=image_data.gcodeSettings,
                    process=constants.IMAGE_GENERATOR_MARK_PROCESS)

                marking_images_data.append({
                    'image': marking_image_data,
                    'settings': marking_image_settings
                })

            if image_data.modifiedSVGCutting:
                cutting_image_data, cutting_image_settings = self._prepare_image_data(
                    image=image_data.modifiedSVGCutting,
                    settings=image_data.gcodeSettings,
                    process=constants.IMAGE_GENERATOR_CUT_PROCESS)

                cutting_images_data.append({
                    'image': cutting_image_data,
                    'settings': cutting_image_settings
                })

            material_settings, thickness_settings = \
                image_data.gcodeSettings.mainSettings.material, \
                image_data.gcodeSettings.mainSettings.thickness

            materials_settings_list.append({
                'material': material_settings,
                'thickness': thickness_settings
            })

        return engraving_images_data, marking_images_data, cutting_images_data, materials_settings_list

    def _prepare_image_data(self, image, settings, process):
        image_file_content = convert_base64_to_image(image)
        image_settings = {}

        if process == constants.IMAGE_GENERATOR_ENGRAVE_PROCESS:
            image_settings = self._fetch_specific_settings(
                settings, ['mainSettings', 'engravingSettings'])
        elif process == constants.IMAGE_GENERATOR_MARK_PROCESS:
            image_settings = self._fetch_specific_settings(
                settings, ['mainSettings', 'markingSettings'])
        elif process == constants.IMAGE_GENERATOR_CUT_PROCESS:
            image_settings = self._fetch_specific_settings(
                settings, ['mainSettings', 'cuttingSettings'])

        # find the min/max points for the images
        if image_settings:
            self._check_images_bounding_box_metrics(image_settings)

        return image_file_content, image_settings

    def _check_images_bounding_box_metrics(self, image_settings):
        if self._images_bounding_box:
            # compare previous metrics
            if self._images_bounding_box['min_point']['x'] > image_settings.get('metrics').x:
                self._images_bounding_box['min_point']['x'] = image_settings.get(
                    'metrics').x
            else:
                self._images_bounding_box['max_point']['x'] = image_settings.get(
                    'metrics').x + (image_settings.get('metrics').width * image_settings.get('metrics').scaleX)

            if self._images_bounding_box['min_point']['y'] > image_settings.get('metrics').y:
                self._images_bounding_box['min_point']['y'] = image_settings.get(
                    'metrics').y
            else:
                self._images_bounding_box['max_point']['y'] = image_settings.get(
                    'metrics').y + (image_settings.get('metrics').height * image_settings.get('metrics').scaleY)
        else:
            # init metrics for the bounding box
            self._images_bounding_box = dict(
                min_point=dict(x=image_settings.get(
                    'metrics').x, y=image_settings.get(
                    'metrics').y),
                max_point=dict(x=image_settings.get(
                    'metrics').x + (image_settings.get('metrics').width * image_settings.get('metrics').scaleX),
                    y=image_settings.get(
                    'metrics').y + (image_settings.get('metrics').height * image_settings.get('metrics').scaleY)
                )
            )

    def _generate_gcode_for_images_data(self, images_data, process):
        gcode_content = ''
        for image_data in images_data:
            image_file_content = image_data.get('image')
            image_settings = image_data.get('settings')

            if process == constants.IMAGE_GENERATOR_ENGRAVE_PROCESS:
                gcode_content += self._generate_gcode_for_image(
                    image_file_content, image_settings)
            else:
                gcode_content += self._generate_gcode_for_svg(
                    image_file_content, image_settings)

        return gcode_content

    def _generate_gcode_for_svg(self, svg_file_content, svg_settings):
        main_gcode_content = ''

        svg_tmp_file_path = self._save_spooled_temp_file_to_disk(
            svg_file_content)
        gcode_tmp_file_path = self._generate_temp_gcode_file()

        command = [
            'svg2gcode',
            '--cuttingpower', str(int(svg_settings.get('power'))),
            '--cuttingspeed', str(int(svg_settings.get('speed'))),
            '--constantburn',
            '--pixelsize', str(100),
            '--xmaxtravel', str(self._config.machine_bed_size.width),
            '--ymaxtravel', str(self._config.machine_bed_size.height),
            '--nofill',
            svg_tmp_file_path,
            gcode_tmp_file_path
        ]

        # Apply user-provided scaling and rotation factors (scaleX, scaleY, rotation) and adjust the origin accordingly
        rotation = round(svg_settings.get('metrics').rotation)
        user_scale_x = svg_settings.get('metrics').scaleX
        user_scale_y = svg_settings.get('metrics').scaleY
        user_shift_x = svg_settings.get('metrics').x
        user_shift_y = svg_settings.get('metrics').y

        # Find the shift and scale for the SVG to match the image
        scale_x, scale_y, shift_x, shift_y = self._calculate_shift_and_scale(
            svg_file_content.decode('utf-8'), user_scale_x, user_scale_y, user_shift_x, user_shift_y, rotation)

        # Add commands for origin and scaling to the gcode generation command
        command.extend([
            '--rotate', str(rotation),
            '--origin',
            str(shift_x - self._images_bounding_box['min_point']['x']
                if shift_x - self._images_bounding_box['min_point']['x'] >
                0.000001 else 0),
            str(shift_y - self._images_bounding_box['min_point']['y']
                if shift_y - self._images_bounding_box['min_point']['y'] >
                0.000001 else 0),
            '--scale', str(scale_x), str(scale_y)
        ])

        try:
            subprocess.run(command, check=True,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            # Add tool and material thickness to the generated gcode
            main_gcode_content += self._add_tool_and_thickness_commands(
                gcode_tmp_file_path, svg_settings)

            return main_gcode_content

        except subprocess.CalledProcessError as e:
            print("Error:", e)
            return None

        finally:
            # Remove temp files
            self._remove_temp_file_from_system(svg_tmp_file_path)
            self._remove_temp_file_from_system(gcode_tmp_file_path)

    def _generate_gcode_for_image(self, image_file_content, image_settings):
        main_gcode_content = ''

        image_tmp_file_path = self._save_spooled_temp_file_to_disk(
            image_file_content)

        # apply transformation on image (scale - rotate)
        self._apply_transformation_on_image(
            image_tmp_file_path, image_settings)

        gcode_tmp_file_path = self._generate_temp_gcode_file()

        resolution = image_settings.get('dithering').resolution
        # prevent very small values from passing to the
        user_shift_x = image_settings.get('metrics').x if abs(
            image_settings.get('metrics').x) > 0.000001 else 0
        user_shift_y = image_settings.get('metrics').y if abs(
            image_settings.get('metrics').y) > 0.000001 else 0

        # create the command to run using the subprocess
        command = [
            'image2gcode',
            '--maxpower', str(int(image_settings.get('power'))),
            '--speed', str(int(image_settings.get('speed'))),
            '--pixelsize', str(100 / resolution),
            '--offset', str(user_shift_x - self._images_bounding_box['min_point']['x']), str(
                user_shift_y - self._images_bounding_box['min_point']['y']),
            image_tmp_file_path,
            gcode_tmp_file_path
        ]

        try:
            subprocess.run(command, check=True,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            # Add tool and material thickness to the generated gcode
            main_gcode_content += self._add_tool_and_thickness_commands(
                gcode_tmp_file_path, image_settings)

            return main_gcode_content

        except subprocess.CalledProcessError as e:
            raise subprocess.SubprocessError(e)

        finally:
            # remove the temp files from the system
            self._remove_temp_file_from_system(image_tmp_file_path)
            self._remove_temp_file_from_system(gcode_tmp_file_path)

    def _add_tool_and_thickness_commands(self, gcode_tmp_file_path, image_settings):
        main_gcode_content = ''
        with open(gcode_tmp_file_path, 'r') as gcode_file:
            main_gcode_content = gcode_file.read()

            # add tool command
            if self._config.laser_cutter_settings.tool_changer:
                tool = image_settings.get('tool')
                gcode_content_with_tool = self._add_tool_command(
                    main_gcode_content, tool)

                # Adjust for material thickness and tool type
                material_thickness = image_settings.get('thickness')
                main_gcode_content = self._add_material_thickness_command(
                    gcode_content_with_tool, material_thickness, tool)

        return main_gcode_content

    def _add_material_settings_comment(self, materials_settings_list):
        material_comment = ''
        is_multi_material = False
        is_multi_thickness = False
        # materials settings list is not empty
        if materials_settings_list:
            # use the first material settings as a reference
            material, thickness = materials_settings_list[0].get(
                'material'), materials_settings_list[0].get('thickness')
            # check if all materials settings are the same or are different
            for material_setting in materials_settings_list[1:]:
                if material != material_setting.get('material'):
                    is_multi_material = True
                    material = 'Multi-Materials'
                if thickness != material_setting.get('thickness'):
                    is_multi_thickness = True
                    thickness = 'Multi-Thicknesses'
                # break when it is already known that the materials settings are different
                if is_multi_material and is_multi_thickness:
                    break

        material_comment = (f";Material Settings:\n;Material Name: {material}\n"
                            f";Material Thickness: {thickness} {'' if thickness == 'Multi-Thicknesses' else 'mm'}\n\n")
        return material_comment

    def _add_images_bounding_box_comment(self):
        if self._images_bounding_box:
            return (
                f";ImagesBoundingBox: (X{self._images_bounding_box['min_point']['x']},"
                f"Y{self._images_bounding_box['min_point']['y']}:"
                f"X{self._images_bounding_box['max_point']['x']},"
                f"Y{self._images_bounding_box['max_point']['y']})\n\n"
            )
        return ''

    def _add_padding_to_image(self, image_file_path):
        # Open the image using PIL
        image = Image.open(image_file_path)

        # Concatenate the white boxes with the original image
        new_image = ImageOps.expand(image, border=(
            constants.BOUNDING_DIMENSION, 0, constants.BOUNDING_DIMENSION, 0), fill='white')

        # Convert the resulting image back to binary data
        image_with_padding = io.BytesIO()
        new_image.save(image_with_padding, format='PNG')

        # Update the image content with the new transformed image
        self._update_image_content(
            image_with_padding.getvalue(), image_file_path)

    def _apply_transformation_on_image(self, image_file_path, image_settings):
        # Open the image using PIL
        image = Image.open(image_file_path)

        # Scale the image
        scaled_image = self._apply_scaling_on_image(image, image_settings)

        # Rotate the image
        rotated_scaled_image = self._apply_rotation_on_image(
            scaled_image, image_settings)

        # Convert the rotated, scaled, and cropped image back to binary data
        image_with_transformation = io.BytesIO()
        rotated_scaled_image.save(image_with_transformation, format='PNG')

        # Update the image content
        self._update_image_content(
            image_with_transformation.getvalue(), image_file_path)

    def _apply_scaling_on_image(self, image, image_settings):
        # get resolution value
        resolution = image_settings.get('dithering').resolution

        # Scale the image based on the image settings
        user_scale_x = image_settings.get('metrics').scaleX * resolution / 100
        user_scale_y = image_settings.get('metrics').scaleY * resolution / 100

        # If scale_y is negative, flip the image vertically
        if user_scale_y < 0:
            image = ImageOps.flip(image)
            # Make scale_y positive after flipping
            user_scale_y = abs(user_scale_y)

        # Get the original width and height
        original_width, original_height = image_settings.get(
            'metrics').width, image_settings.get('metrics').height

        # Scale the image while maintaining aspect ratio if only one scale is provided
        new_width = round(original_width * user_scale_x)
        new_height = round(original_height * user_scale_y)

        # Resize the image using the new dimensions
        scaled_image = image.resize(
            (new_width, new_height), Image.Resampling.LANCZOS)

        return scaled_image

    def _apply_rotation_on_image(self, image, image_settings):
        # Rotate the image based on the image settings
        rotation_angle = image_settings.get('metrics').rotation

        # Rotate using PIL's rotate (expand=True to prevent cropping)
        rotated_image = image.rotate(
            rotation_angle, expand=True, fillcolor=(255, 255, 255))

        return rotated_image

    def _update_image_content(self, new_image_content, image_file_path):
        with open(image_file_path, 'wb') as image_file:
            image_file.write(new_image_content)

    def _generate_temp_gcode_file(self):
        with tempfile.NamedTemporaryFile(delete=False, suffix='.gcode') as temp_file:
            return temp_file.name

    def _save_spooled_temp_file_to_disk(self, spooled_temp_file_content):
        with tempfile.NamedTemporaryFile(delete=False, suffix='.svg') as temp_file:
            temp_file.write(spooled_temp_file_content)
        return temp_file.name

    def _remove_temp_file_from_system(self, temp_file_path):
        os.unlink(temp_file_path)

    # add the tool which the user pick from the settings
    def _add_tool_command(self, gcode_content, tool):
        # Find the index of the relative position command
        relative_position_index = gcode_content.find(
            constants.GRBL_COMMAND_RELATIVE_POSITION + constants.NEW_LINE)
        if relative_position_index != -1:
            insertion_index = relative_position_index + \
                len(constants.GRBL_COMMAND_RELATIVE_POSITION) + \
                len(constants.NEW_LINE)

            # Construct the tool command
            tool_command = self._generate_tool_command(tool)

            # Insert the tool command into the G-code content
            modified_gcode_content = gcode_content[:insertion_index] + \
                tool_command + \
                gcode_content[insertion_index:]
            return modified_gcode_content
        else:
            # If the relative position command is not found, return the original G-code content
            return gcode_content

    def _generate_tool_command(self, tool):
        tool_command = ''
        machines_tools = self._get_machine_tools()
        # get the tool settings for each tool in the configuration file
        for tool_settings in machines_tools.values():
            if tool == tool_settings['name']:
                tool_command += tool_settings['command']
        return tool_command

    def _get_machine_tools(self):
        return self._config.get_dict(
            'laser_cutter_settings.tools')

    def _add_material_thickness_command(self, gcode_content, material_thickness, tool):
        # check the metrics for the bed based on the used tool
        min_z_axis_value = 0
        max_z_axis_value = 0

        # get the tool settings for each tool in the configuration file
        machines_tools = self._get_machine_tools()
        for tool_settings in machines_tools.values():
            if tool == tool_settings['name']:
                min_z_axis_value = tool_settings['z_axis']['min']
                max_z_axis_value = tool_settings['z_axis']['max']

        # Ensure the value stays inside the range of the bed
        if material_thickness + max_z_axis_value < min_z_axis_value:
            # Define regex pattern for tool changer commands
            pattern = rf'{re.escape(constants.GRBL_TOOL_CHANGE)}T\d+'
            # Compile the regular expression pattern
            regex_pattern = re.compile(pattern)
            # Search for the pattern in the gcode content
            match = regex_pattern.search(gcode_content)
            if match:
                tool_changer_index = match.end()
                # Construct the material thickness command
                material_thickness_command = constants.GRBL_COMMAND_MOVE_BED + str(max_z_axis_value + material_thickness) + \
                    constants.GRBL_MATERIAL_THICKNESS_COMMENT + \
                    constants.NEW_LINE

                # Insert the material thickness command into the G-code content
                modified_gcode_content = gcode_content[:tool_changer_index] + constants.NEW_LINE + \
                    material_thickness_command + \
                    gcode_content[tool_changer_index:]
                return modified_gcode_content
            else:
                # If the relative position command is not found, return the original G-code content
                return gcode_content

    # customize the generated gcode
    def _modify_gcode_content(self, gcode_content):
        # remove M2 and M9 from the gcode to prevent stopping the machine
        modified_gcode_content = self._remove_unnecessary_commands(
            gcode_content)

        # replace eular numbers to decimal (because previewer can't recognize numbers that contains characters)
        modified_gcode_content = self._convert_scientific_notation_to_decimal(
            modified_gcode_content)

        # remove all the commands that contains S1 (not necessary commands)
        modified_gcode_content = self._remove_lines_containing_S1(
            modified_gcode_content)

        # remove the tool at the end of the generated gcode
        modified_gcode_content = self._add_remove_tool_command_at_end(
            modified_gcode_content)

        # at the end of the job add M9 to finish the job
        modified_gcode_content = self._add_end_of_job_commands(
            modified_gcode_content)

        return modified_gcode_content

    def _remove_lines_containing_S1(self, gcode_content):
        # Split the input string into lines
        lines = gcode_content.split('\n')

        # Filter out lines that contain the specific substring "S1" but not "S10", "S11", etc.
        filtered_lines = [
            line for line in lines if not re.search(r'S1(?!\d)', line)]

        # Join the remaining lines back into a single string
        result_string = '\n'.join(filtered_lines)

        return result_string

    def _remove_unnecessary_commands(self, gcode_content):
        gcode_content = gcode_content.replace(
            constants.GRBL_END_PROGRAM, '')
        gcode_content = gcode_content.replace(
            constants.GRBL_COOLANT_OFF, '')
        return gcode_content

    def _add_remove_tool_command_at_end(self, gcode_content):
        return gcode_content + constants.NEW_LINE + \
            constants.GRBL_TOOL_CHANGE + constants.GRBL_NO_TOOL

    def _add_end_of_job_commands(self, gcode_content):
        return gcode_content + constants.NEW_LINE + \
            constants.GRBL_COOLANT_OFF + constants.NEW_LINE + constants.GRBL_END_PROGRAM

    def _calculate_shift_and_scale(self, svg_file_content, user_scale_x=1, user_scale_y=1, user_shift_x=0, user_shift_y=0, rotation=0):
        # Extract viewBox and width/height attributes from the SVG string
        viewbox_match = re.search(r'viewBox="([^"]+)"', svg_file_content)
        width_match = re.search(r'width="([^"]+)"', svg_file_content)
        height_match = re.search(r'height="([^"]+)"', svg_file_content)

        if viewbox_match and width_match and height_match:
            # Parse viewBox, width, and height values
            viewbox_values = list(map(float, viewbox_match.group(1).split()))
            width, width_unit = self._extract_value_with_unit(width_match)
            height, height_unit = self._extract_value_with_unit(height_match)

            # Convert width and height to pixels
            width_px = self._convert_to_pixels(
                width, width_unit, reference=viewbox_values[2])
            height_px = self._convert_to_pixels(
                height, height_unit, reference=viewbox_values[3])

            # Adjust viewBox if units are not pixels
            if width_unit != 'px':
                viewbox_values[2] = width_px
            if height_unit != 'px':
                viewbox_values[3] = height_px

            # Calculate initial scale and shift factors
            scale_x = (width_px / viewbox_values[2]) * user_scale_x
            scale_y = (height_px / viewbox_values[3]) * user_scale_y
            shift_x = user_shift_x - viewbox_values[0]
            shift_y = user_shift_y - viewbox_values[1]

            # Apply rotation and find shifts
            if rotation != 0:
                shift_x_rot, shift_y_rot = self._apply_rotation_and_find_shift(
                    viewbox_values[2] * scale_x, viewbox_values[3] * scale_y, rotation)

                return scale_x, scale_y, shift_x + shift_x_rot, shift_y + shift_y_rot

            else:
                # no rotation
                return scale_x, scale_y, shift_x, shift_y
        else:
            # Apply rotation and find shifts
            if rotation != 0:
                width, width_unit = self._extract_value_with_unit(width_match)
                height, height_unit = self._extract_value_with_unit(
                    height_match)

                # Convert width and height to pixels
                width_px = self._convert_to_pixels(
                    width, width_unit)
                height_px = self._convert_to_pixels(
                    height, height_unit)

                if width_px and height_px:
                    shift_x_rot, shift_y_rot = self._apply_rotation_and_find_shift(
                        width_px * user_scale_x, height_px * user_scale_y, rotation)

                    return user_scale_x, user_scale_y, shift_x_rot, shift_y_rot
                else:
                    return user_scale_x, user_scale_y, user_shift_x, user_shift_y

            else:
                return user_scale_x, user_scale_y, 0, 0

    def _apply_rotation_and_find_shift(self, width, height, rotation):
        theta = np.radians(rotation)

        # Define original corners of the bounding box (before any transformations)
        corners = np.array([
            [0, height],
            [width, height],
            [0, 0],
            [width, 0]
        ])

        # Rotation matrix
        rotation_matrix = np.array([
            [np.cos(theta), -np.sin(theta)],
            [np.sin(theta), np.cos(theta)]
        ])

        # Rotate corners
        rotated_corners = np.dot(corners, rotation_matrix.T)

        # Find minimum x and y values after rotation
        min_x = np.min(rotated_corners[:, 0])
        min_y = np.min(rotated_corners[:, 1])

        # Calculate the shifts to move the shape to the positive quadrant
        shift_x = -min_x if min_x < 0 else 0
        shift_y = -min_y if min_y < 0 else 0

        return shift_x, shift_y

    def _extract_value_with_unit(self, match, default_unit='px'):
        if match:
            value_with_unit = match.group(1)
            value, unit = re.match(r'([\d.]+)(\D+)?', value_with_unit).groups()
            if unit:
                return float(value), unit
            else:
                return float(value), default_unit
        else:
            return None, default_unit

    def _convert_to_pixels(self, value, unit, reference=None, dpi=96):
        if unit == 'px':
            return value
        elif unit == 'in':
            return value * dpi
        elif unit == 'cm':
            return value * dpi / 2.54
        elif unit == 'mm':
            return value * dpi / 25.4
        elif unit == 'pt':
            return value * dpi / 72
        elif unit == '%':
            if reference is not None:
                return value * reference / 100
            else:
                return None  # Return None if no reference is available
        else:
            raise ValueError(f"Unsupported unit: {unit}")

    # create new dictionary based on specific keys
    def _fetch_specific_settings(self, gcode_settings, type_of_settings):
        specific_settings = {}
        gcode_settings = dict(gcode_settings)
        for setting in type_of_settings:
            specific_settings.update(gcode_settings.get(setting))
        return specific_settings

    def _convert_scientific_notation_to_decimal(self, content):
        # Regular expression to find numbers in scientific notation
        scientific_notation_pattern = re.compile(
            r'([-+]?\d*\.?\d+[eE][-+]?\d+)(?![\d])')

        # Function to convert a match to its decimal representation
        def convert_match(match):
            scientific_notation = match.group(1)
            decimal_representation = format(
                float(scientific_notation), '.15f').rstrip('0').rstrip('.')
            return decimal_representation

        # Substitute all scientific notation numbers with their decimal representation
        result_string = scientific_notation_pattern.sub(
            convert_match, content)

        return result_string
