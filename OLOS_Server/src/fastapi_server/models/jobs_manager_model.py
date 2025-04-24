from typing import Dict, List,  Optional
from pydantic import BaseModel


class JobsManagerData(BaseModel):
    process: str = ''
    fileData: Dict[str, str] = {'fileName': '', 'fileContent': '',
                                'materialName': '', 'materialImage': '', 'materialThickness': ''}
    filesListData: list[str] = []
    success: bool = False


class JobsManagerResponse(BaseModel):
    type: str
    data: JobsManagerData


class RenameJobData(BaseModel):
    old_filename: str = ''
    new_filename: str = ''


class USBJobFileData(BaseModel):
    filename: str = ''
    file_path: str = ''


class ImageMetrics(BaseModel):
    x: float
    y: float
    width: float
    height: float
    rotation: float
    scaleX: float
    scaleY: float
    offsetX: float
    offsetY: float


class DitheringSettings(BaseModel):
    algorithm: str
    grayShift: float
    resolution: float
    blockSize: float
    blockDistance: float


class OperationMainSettings(BaseModel):
    power: float
    speed: float
    tool: str


class ThicknessOperation(OperationMainSettings):
    operationId: Optional[int] = None
    operationType: Optional[str] = None
    dithering: Optional[DitheringSettings] = None


class EngravingSettings(OperationMainSettings):
    dithering: DitheringSettings


class MainSettings(BaseModel):
    material: str
    thickness: float
    metrics: ImageMetrics
    filename: str


class GcodeFileSettings(BaseModel):
    mainSettings: MainSettings
    cuttingSettings: ThicknessOperation
    markingSettings: ThicknessOperation
    engravingSettings: EngravingSettings


class ModifiedImageData(BaseModel):
    modifiedSVGCutting: Optional[str] = None
    modifiedSVGMarking: Optional[str] = None
    modifiedEngravingImage: Optional[str] = None
    gcodeSettings: GcodeFileSettings


class GcodeFileData(BaseModel):
    name: str
    modifiedImagesData: List[ModifiedImageData]
