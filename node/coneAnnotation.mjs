import { open } from "node:fs/promises";
import { Annotation } from "./annotation.mjs";
import { parseParams } from "./utils.mjs";

export class ConeAnnotations extends Annotation {
  constructor(args) {
    super(args);
    this.type = "CONE";
  }

  get basicBytesPerAnnotation() {
    return 2 * 4 * 4;
  }

  async getRawData(extname, annotations) {
    if(extname === ".swc") {
      const file = await open(this.infoFile);
      for await (const line of file.readLines()) {
        if(line) {
          const [index, reserve, x, y, z, r, root]= line.split(" ").map(x => Number(x))
          if(root === -1) {
            annotations.set(index, { id: index, annotation: [x, y, z, r] });
          } else {
            const basic = annotations.get(root);
            annotations.set(root, {
              ...basic,
              annotation: this.parseAnnotation([ ...basic.annotation, x, y, z, r ])
            })
          }
        }
      }
      file.close();
    } else {
      super.getRawData(extname, annotations)
    }
  }

}

Annotation.run(ConeAnnotations);
