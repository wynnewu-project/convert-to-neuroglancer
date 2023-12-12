import { Annotation } from "./annotation.mjs";

export class EllipsoidAnnotation extends Annotation {
  constructor({radii=10, ...args}) {
    super(args);
    this.type = "ELLIPSOID";
    this.radii = radii;
  }

  get basicBytesPerAnnotation() {
    return 2 * 3 * 4;
  }

  parseAnnotation(annotation) {
    const [ x, y, z, rx, ry, rz, r, g, b, a=255 ] = annotation; 

    let parseResult = [x, y, z].map(value => ({ type: "float32", value }))
    parseResult = [
      ...parseResult,
      ...[rx, ry, rz].map(value => ({ type: "float32", value: value > 0 ? value : this.radii}))
    ]

    if(r !== undefined) {
      parseResult = [
        ...parseResult, 
        ...this.parseProperties("ellipsoidColor", [r,g,b,a], "rgba")
      ]
    }
    return parseResult;
  }

}

Annotation.run(EllipsoidAnnotation);
