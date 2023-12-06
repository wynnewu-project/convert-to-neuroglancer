import { Annotation } from "./annotation.mjs";
import { parseParams } from "./utils.mjs";

export class AtlasEllipsoidAnnotation extends Annotation {
  constructor(args) {
    super(args)
    this.type = "ATLAS_ELLIPSOID";
  }

  get basicBytesPerAnnotation() {
    return 4 * 4 * 3;
  }

}

Annotation.run(AtlasEllipsoidAnnotation);