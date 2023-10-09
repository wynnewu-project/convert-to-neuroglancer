import { Annotation } from "./annotation.mjs";

export class EllipsoidAnnotation extends Annotation {
  constructor(radii=[10, 10, 10], ...args) {
    super(...args);
    this.type = "ELLIPSOID";
    this.radii = radii;
  }

  get bytesPerAnnotation() {
    return 2 * 3 * 4;
  }

  encodingSingleAnnotation(dv, offset, ellipsolid) {
    const { position, radii } = ellipsolid; 
    const radiiFinal = radii ?? this.radii;  
    console.log('radii', radiiFinal);
    [...position, ...radiiFinal ].forEach(p  => {
      dv.setFloat32(offset, p, true);
      offset += 4;
    })
    return offset;
  }

  parseSourceData(indices, sheetObj, rawData) {
    const { start_row=0, end_row=1, end_col="F" } = indices;
    if(end_col.charCodeAt(0) < "C".charCodeAt(0)) {
      throw new Error("至少需要一个点三维坐标")
    }
    let count = 0;
    for(let i = Number(start_row); i <= Number(end_row); i++) {
      count +=1;
      const ellipsolid = {
        id: count,
        position: [sheetObj[`A${i}`].v, sheetObj[`B${i}`].v, sheetObj[`C${i}`].v]
      }
      if(end_col === "F") {
        ellipsolid.radii = [ sheetObj[`D${i}`].v, sheetObj[`E${i}`].v, sheetObj[`F${i}`].v];
      }
      rawData.set(count, ellipsolid );
    }
  }
}
