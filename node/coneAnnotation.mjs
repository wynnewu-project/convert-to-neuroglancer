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
      const pointMap = new Map();
      for await (const line of file.readLines()) {
        if(line) {
          const [index, reserve, x, y, z, r, root]= line.split(" ").map(x => Number(x))
          pointMap.set(index, [x, y, z, r] );

          if(root !== -1) {
            const base = pointMap.get(root);
            annotations.set(annotations.size, {
              id: annotations.size,
              annotation: this.parseAnnotation([ ...base, x, y, z, r ])
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
