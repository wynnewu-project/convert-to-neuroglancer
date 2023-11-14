import { Annotation } from "./annotation.mjs";
import { open } from "node:fs/promises";
import { TYPE_BYTES_LENGTH, parseParams } from "./utils.mjs";

export class SphereAnnotations extends Annotation {
  constructor(...args) {
    super(...args);
    this.type = "SPHERE";
  }

  get bytesPerAnnotation() {
    const { properties=[] } = this.infoContent;
    let bytes = 3 * 4;
    for(let propery of properties) {
      const { type } = propery;
      bytes += TYPE_BYTES_LENGTH[type];
    }
    return bytes;
  }
  
  async getRawData() {
    const rawData = new Map();
    const file = await open(this.infoFile);
    let count = 0;
    for await (const annotation of file.readLines()) {
      count += 1;
      const sphere = annotation.split(" ").map(x => Number(x))
      rawData.set(count, { id: count, sphere });
    }
    file.close();
    return rawData;
  }

  encodingSingleAnnotation(dv, offset, sphereItem) {
    const { sphere } = sphereItem;
    for(let i of sphere) {
      dv.setFloat32(offset, i, true);
      offset += 4;
    }
    return offset;
  }
}

const args = parseParams(process.argv.slice(2));
const { infoFile, upperBound, properties='{}', targetDir="sphere" } = args;
const sphereAnnotations = new SphereAnnotations({
  infoFile,
  upperBound: JSON.parse(upperBound),
  infoSpec: {
    properties: JSON.parse(properties)
  }
})
sphereAnnotations.writeToPrecomputed(targetDir);

