import { Annotation } from "./annotation.mjs";

export class SphereAnnotations extends Annotation {
  constructor(args) {
    super(args);
    this.type = "SPHERE";
  }

  get basicBytesPerAnnotation() {
    return 3 * 4;
  }

  parseAnnotation(annotation) {
    const [x, y, z, radius, r, g, b, a=255] = annotation;
    let parseResult = [x, y, z].map(value => ({ type: "float32", value }));
    parseResult["float32"] = [x, y, z];
    if(radius) {
      parseResult = [
        ...parseResult,
        ...this.parseProperties("sphereRadius", [radius])
      ]
    }
    if(r!==undefined) {
      parseResult = [
        ...parseResult,
        ...this.parseProperties("sphereColor", [r,g,b,a], "rgba")
      ]
    }
    return parseResult;
  }
}

Annotation.run(SphereAnnotations);



