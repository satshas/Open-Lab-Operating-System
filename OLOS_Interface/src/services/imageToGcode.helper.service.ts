import Konva from 'konva';
import {
  convertDXFToSVGDataURI,
  postProcessSvgDataURI,
} from './svg.editor.service';

export const getImageContentFromFile = (
  file: File,
  imageConfig: Konva.ImageConfig
): Promise<string> => {
  return new Promise((resolve, reject) => {
    let imageContent = '';

    const processFileContent = async (
      fileContent: string,
      fileType: string
    ) => {
      try {
        if (fileType === 'svg') {
          // Handle SVG files
          const svgData = await postProcessSvgDataURI(fileContent);
          imageContent = svgData.svgDataURI as string;
          // set correct dimensions
          imageConfig.width = svgData.svgWidth;
          imageConfig.height = svgData.svgHeight;
        } else if (fileType === 'dxf') {
          // Handle DXF files (convert to SVG)
          const svgContent = convertDXFToSVGDataURI(fileContent);
          const svgData = await postProcessSvgDataURI(svgContent);
          imageContent = svgData.svgDataURI as string;
          // set correct dimensions
          imageConfig.width = svgData.svgWidth;
          imageConfig.height = svgData.svgHeight;
        } else {
          // Handle other image files (Data URL)
          imageContent = fileContent;
        }

        // Resolve the promise with the image content
        resolve(imageContent);
      } catch (error) {
        reject(error); // Reject the promise if an error occurs
      }
    };

    // Utility to determine file type based on the extension
    const getFileType = (fileName: string) => {
      if (fileName.endsWith('.svg')) return 'svg';
      if (fileName.endsWith('.dxf')) return 'dxf';
      return 'other'; // Default case for other image types
    };

    // Utility to read the file based on its type
    const readFile = (reader: FileReader, file: File, fileType: string) => {
      if (fileType === 'dxf') {
        reader.readAsText(file); // DXF files as text
      } else {
        reader.readAsDataURL(file); // Other files as Data URL
      }
    };

    const reader = new FileReader();

    reader.onload = async (e: ProgressEvent<FileReader>) => {
      const fileReader = e.target as FileReader;
      if (fileReader?.result) {
        const fileContent = fileReader.result as string;
        const fileType = getFileType(file.name);
        await processFileContent(fileContent, fileType);
      }
    };

    // Read the file based on its type
    const fileType = getFileType(file.name);
    readFile(reader, file, fileType);
  });
};
