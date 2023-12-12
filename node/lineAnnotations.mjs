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

  parseAnnotation(annotation) {
    const [x1, y1, z1, x2, y2, z2, width, r, g, b, a=255] = annotation;
    let parseResult = [x1, y1, z1, x2, y2, z2].map(value => ({ type: "float32", value}));
    if(width) {
      parseResult = [
        ...parseResult,
        ...this.parseProperties("lineWidth", [width])
      ]
    }
    if(r!==undefined) {
      parseResult = [
        ...parseResult,
        ...this.parseProperties("lineColor", [r,g,b,a], "rgba")
      ]
    }
    return parseResult;
  }
}

Annotation.run(LineAnnotations);
