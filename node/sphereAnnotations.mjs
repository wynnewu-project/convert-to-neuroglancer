import { Annotation } from "./annotation.mjs";

export class SphereAnnotations extends Annotation {
  constructor(...args) {
    super(...args);
    this.type = "SPHERE";
  }

  get basicBytesPerAnnotation() {
    return 3 * 4;
  }

  parseProperties(params_count) {
    if(params_count >=4) {
      this.infoContent.properties.push({
        "id": "sphereRadius",
        "type": "float32"
      })
    }
    if(params_count > 4) {
      this.infoContent.properties.push({
        "id": "sphereColor",
        "type": "rgba"
      });
      return;
    }
  }

  parseAnnotation(annotation) {
    const parseResult = {}
    const [x, y, z, radius, r, g, b, a=255] = annotation;
    parseResult["float32"] = [x, y, z];
    if(radius) {
      parseResult["float32"].push(radius);
    }
    if(r!==undefined) {
      parseResult["uint8"] = [ r, g, b, a];
    }
    console.log(parseResult)
    return parseResult;
  }
}

Annotation.run(SphereAnnotations);



