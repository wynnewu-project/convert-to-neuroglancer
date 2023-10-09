import { Annotation } from "./annotation.mjs";

export class LineAnnotations extends Annotation {

  constructor(...args) {
    super(...args);
    this.type = "LINE"
  }


  get bytesPerAnnotation() {
    return 2 * 3 * 4;
  }

  encodingSingleAnnotation(dv, offset, line) {
    const { point1, point2 } = line;
    for(let p of [...point1.position, ...point2.position]) {
      dv.setFloat32(offset, p, true);
      offset += 4;
    }
    return offset
  }

  parseSourceData(indices, sheetObj, rawData) {
    const { start_row=0, end_row=1, end_col="F"} = indices;
    if(end_col.charCodeAt(0) < "F".charCodeAt(0)) {
      throw new Error("至少需要两个端点的坐标");
    }
    let count = 0;
    for(let i = Number(start_row); i <= Number(end_row); i++) {
      count += 1;
      const line = {
        id: count,
        point1: {
          position: [sheetObj[`A${i}`].v, sheetObj[`B${i}`].v, sheetObj[`C${i}`].v]
        },
        point2: {
          position: [sheetObj[`D${i}`].v, sheetObj[`E${i}`].v, sheetObj[`F${i}`].v]
        }
      }
      if(end_col === "G") {
        line.value = sheetObj[`G${i}`].v;
      }
      rawData.set(count, line);
    }
  }
}
