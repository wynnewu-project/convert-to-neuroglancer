import { Annotation } from "./annotation.mjs";
import { linearColorAlpha, parseParams } from "./utils.mjs";

export class LineAnnotations extends Annotation {

  constructor(args) {
    super(args);
    this.type = "LINE"
  }


  get basicBytesPerAnnotation() {
    return 2 * 3 * 4;
  }

  parseProperties(params_count) {
    if(params_count >= 7) {
      this.infoContent.properties.push({
        "id": "lineWidth",
        "type": "float32"
      })
    }
    if(params_count > 7) {
      this.infoContent.properties.push({
        "id": "lineColor",
        "type": "rgba"
      })
    }
  }

  parseAnnotation(annotation) {
    console.log(annotation)
    const parseResult = {};
    const [x1, y1, z1, x2, y2, z2, width, r, g, b, a=255] = annotation;
    parseResult["float32"] = [x1, y1, z1, x2, y2, z2];
    if(width) {
      parseResult["float32"].push(radius);
    }
    if(r!==undefined) {
      parseResult["uint8"] = [ r, g, b, a];
    }
    return parseResult;
  }
}

Annotation.run(LineAnnotations);
