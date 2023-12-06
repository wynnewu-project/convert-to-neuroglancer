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


  parseProperties(params_count) {
    if(params_count > 6) {
      this.infoContent.properties.push({
        "id": "ellipsoidColor",
        "type": "rgba"
      });
    }
  }
  parseAnnotation(annotation) {
    const [x, y, z, rx, ry, rz, r, g, b, a=255] = annotation; 
    const parseResult = {
      "float32": [x, y, z, ...[rx, ry, rz].map(x => x > 0 ? x : this.radii)]
    } 
    if(r !== undefined) {
      parseResult["uint8"] = [r, g, b, a];
    }
    return parseResult;
  }

}

Annotation.run(EllipsoidAnnotation);
