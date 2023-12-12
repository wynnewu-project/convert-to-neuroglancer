import { Annotation } from "./annotation.mjs";

export class PointAnnotation extends Annotation {
  constructor({ radius, ...args}) {
    super(args);
    this.type = "POINT";
    this.radius = radius;
  }

  get basicBytesPerAnnotation() {
    return 3 * 4;
  }

  parseAnnotation(annotation) {
    const [x, y, z, radius, r, g, b, a=255] = annotation;
    const pointRadius = radius > 0 ? radius : this.radius;
    let parseResult = [x, y, z].map(value => ({ type: "float32", value }));
    if(pointRadius) {
      parseResult = [
        ...parseResult,
        ...this.parseProperties("pointRadius", [pointRadius])
      ]
    }

    if(r!==undefined) {
      parseResult = [
        ...parseResult,
        ...this.parseProperties("pointColor", [r,g,b,a], "rgba")
      ]

    }
    return parseResult;
  }
}
Annotation.run(PointAnnotation);