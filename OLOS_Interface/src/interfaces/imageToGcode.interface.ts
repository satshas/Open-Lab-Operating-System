import Konva from 'konva';
import { QTableProps } from 'quasar';
import { INode } from 'svgson';

export interface GcodeGeneratorImageData {
  imageId: string;
  imageName: string;
  imageFile: File | null;
  imageContent: string;
  imageConfig: Konva.ImageConfig;
  imageNode: Konva.Image | null;
  imageMetrics: ImageMetrics;
  originalImageConfig: ImageMetrics | null;
  imageKonvaTransformerGroup: Konva.Group | null;

  activeTab: string;
  svgElementsToModify: Array<DrawElement>;
  gcodeSettings: GcodeFileSettings;
  modifiedSVGCutting: SVGGraphicsElement | null;
  modifiedSVGMarking: SVGGraphicsElement | null;
  modifiedEngravingImage: HTMLImageElement | null;
  // table reactive states
  tableFilterType: string;
  tableSelectedElements: QTableProps['selected'];
  tableProfileModels: Record<string, string>;
  tableProfileAllModels: string;
  singleProfileOptions: Array<string>;
  allProfileOptions: Array<string>;
  filteredElementsByShape: Array<IShapeElement>;
  filteredElementsByColor: Array<IColorElement>;
  svgElementAttributes: Record<string, string>;
}

export interface GcodeFileData {
  name: string;
  modifiedImagesData: Array<ModifiedImageData>;
}

export interface ModifiedImageData {
  modifiedSVGCutting: string | null;
  modifiedSVGMarking: string | null;
  modifiedEngravingImage: string | null;
  gcodeSettings: GcodeFileSettings;
}

export interface DitheringSettings {
  algorithm: string;
  grayShift: number;
  resolution: number;
  blockSize: number;
  blockDistance: number;
}

export interface TransformData {
  [key: string]: number | number[];
}

export interface IColorElement {
  color: string;
  elements: INode[];
}

export interface IShapeElement {
  shape: string;
  elements: INode[];
}

export interface SelectedElementType {
  identifier: string;
  elements: INode[];
  profileType: string;
  added: boolean;
}

export interface DrawElement {
  identifier: string;
  elements: INode[];
  type: string;
}

export interface KonvaImageResult {
  imageNode: Konva.Image;
  imageConfig: Konva.ImageConfig;
}

export interface ImageMetrics {
  x: number;
  y: number;
  width: number;
  height: number;
  rotation: number;
  scaleX: number;
  scaleY: number;
  offsetX: number;
  offsetY: number;
}

export interface MainSettings {
  material: string;
  thickness: number;
  metrics: ImageMetrics;
}

export interface EngravingSettings extends OperationMainSettings {
  dithering: DitheringSettings;
}

export interface GcodeFileSettings {
  mainSettings: MainSettings;
  cuttingSettings: ThicknessOperation;
  markingSettings: ThicknessOperation;
  engravingSettings: EngravingSettings;
}

export interface RejectedFileEntry {
  failedPropValidation: string;
  file: File;
}

export interface MaterialData {
  materialId: number;
  materialName: string;
  materialImage: string | null;
  materialThicknesses: Array<MaterialThickness>;
  isEditable?: boolean;
}

export interface MaterialThickness {
  thicknessId: number;
  thicknessValue: number;
  thicknessOperations: Array<ThicknessOperation>;
}

export interface ThicknessOperation extends OperationMainSettings {
  operationId?: number;
  operationType?: string;
  dithering?: DitheringSettings;
}

export interface OperationMainSettings {
  power: number;
  speed: number;
  tool: string;
}
