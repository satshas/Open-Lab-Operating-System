import { Constants } from 'src/constants';
import {
  IColorElement,
  IShapeElement,
} from 'src/interfaces/imageToGcode.interface';
import { INode } from 'svgson';
import {
  calculateTransformationValue,
  convertColorToRgb,
} from './svg.editor.service';

export class SVGParser {
  svgElementAttributes: Record<string, string>;
  elementId: number;

  shapeElements: Array<IShapeElement>;
  colorElements: Array<IColorElement>;

  constructor() {
    this.svgElementAttributes = {};
    this.elementId = 0;
    this.shapeElements = [];
    this.colorElements = [];
  }

  filterSvgElements = (json: INode, attributes?: Record<string, string>) => {
    // get svg element attributes to apply on the modified svg
    if (json.name === 'svg') {
      this.svgElementAttributes = json.attributes;
    }

    // filter svg sub elements/nodes
    json.children.forEach((childElement) => {
      // check the element name and if it match the allowed elements used to draw on the svg
      if (Constants.SVG_ALLOWED_ELEMENTS.includes(childElement.name)) {
        childElement.attributes = this.addParentAttributesToChild(
          childElement.attributes,
          attributes
        );
        // give the element an id for sorting and deleting
        childElement.attributes.id = this.elementId.toString();
        this.elementId++;

        this.checkElementBasedOnShape(childElement);
        this.checkElementBasedOnColor(childElement);
      }

      // check if the element contains children elements and try to filter its elements
      if (childElement.children.length) {
        this.filterSvgElements(childElement, {
          ...attributes,
          ...childElement.attributes,
        });
      }
    });
  };

  // export const clearFilteredSVGArrays = () => {
  //   elementsFilterByColor.length = 0;
  //   elementsFilterByShape.length = 0;
  //   elementId = 0;
  // };

  addParentAttributesToChild = (
    childAttributes: Record<string, string>,
    parentAttributes?: Record<string, string>
  ) => {
    if (parentAttributes) {
      // apply the correct transformation incase of inherited attributes
      childAttributes.transform = calculateTransformationValue(
        childAttributes,
        parentAttributes
      );
    }
    // add the rest of attributes inherited from the parent node
    childAttributes = {
      ...parentAttributes,
      ...childAttributes,
    };

    return childAttributes;
  };

  checkElementBasedOnShape = (childElement: INode) => {
    let found = false;

    this.shapeElements.forEach((element) => {
      // If the shape already exists in the array
      if (element.shape === childElement.name) {
        element.elements.push(childElement);
        found = true; // Set flag to indicate shape was found
      }
    });

    // If the shape doesn't exist in the array, create a new entry
    if (!found) {
      this.shapeElements.push({
        shape: childElement.name,
        elements: [childElement],
      });
    }
  };

  checkElementBasedOnColor = (childElement: INode) => {
    this.checkElementStrokeColor(childElement);
    this.checkElementFillColor(childElement);
  };

  checkElementStrokeColor = (childElement: INode) => {
    let rgbColor;
    // for stroke attribute
    if (childElement.attributes.stroke) {
      const color = childElement.attributes.stroke;
      rgbColor = convertColorToRgb(color);
    } else if (childElement.attributes.style) {
      // Extract the stroke value from the style attribute
      const strokeValueMatch = childElement.attributes.style.match(
        /stroke:\s*(.*?)(?:;|$)/
      );
      const color = strokeValueMatch ? strokeValueMatch[1] : null;
      // check if there is a color value and convert it to rgb color
      if (color && color !== 'none') {
        rgbColor = convertColorToRgb(color);
      }
    }

    // add a new color
    if (rgbColor) {
      this.addColorToElement(childElement, rgbColor);
    }
  };

  checkElementFillColor = (childElement: INode) => {
    let rgbColor;
    if (childElement.attributes.fill) {
      // for fill attribute
      const color = childElement.attributes.fill;
      rgbColor = convertColorToRgb(color);
    } else if (childElement.attributes.style) {
      // Extract the fill value from the style attribute
      const fillValueMatch =
        childElement.attributes.style.match(/fill:\s*(.*?)(?:;|$)/);
      const color = fillValueMatch ? fillValueMatch[1] : null;
      // check if there is a color value and convert it to rgb color
      if (color && color !== 'none') {
        rgbColor = convertColorToRgb(color);
      } else {
        rgbColor = Constants.RGB_COLOR.BLACK;
      }
    } else {
      // there is no fill attribute give it a black color
      rgbColor = Constants.RGB_COLOR.BLACK;
    }

    // add new element based on color value
    if (rgbColor) {
      this.addColorToElement(childElement, rgbColor);
    }
  };

  addColorToElement = (childElement: INode, rgbColor: string) => {
    let found = false;

    this.colorElements.forEach((element) => {
      // If the color already exists in the array
      if (element.color === rgbColor) {
        // check if it is not already added from stroke before
        if (!element.elements.includes(childElement)) {
          element.elements.push(childElement);
        }
        found = true; // Set flag to indicate color was found
      }
    });

    // If the color doesn't exist in the array, create a new entry
    if (!found) {
      this.colorElements.push({
        color: rgbColor,
        elements: [childElement],
      });
    }
  };
}
