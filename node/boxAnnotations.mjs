import { Annotation } from "./annotation.mjs";

export class BoxAnnotation extends Annotation {
  constructor(args) {
    super(args);
    this.type = "AXIS_ALIGNED_BOUNDING_BOX";
  }

  get basicBytesPerAnnotation() {
    return 2 * 3 * 4;
  }
}

Annotation.run(BoxAnnotation);
