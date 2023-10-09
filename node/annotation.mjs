import { readWorkbookFromLocalFile, makeDir } from "./utils.mjs";
import { writeFile } from "node:fs/promises";
import { cwd } from "node:process";

export class Annotation {

  infoContent = {
    "@type": "neuroglancer_annotations_v1",
    "by_id": {
      "key": "by_id"
    },
    "lower_bound": [ 0, 0, 0 ],
    "relationships": [],
    "properties": [],
    "spatial": [
      {
        "grid_shape": [ 1, 1, 1 ],
        "key": "spatial0",
        "limit": 2000 
      }
    ],
  }

  /**
   * 
   * @param {*} infoFile - excel or csv
   */
  constructor(infoFile, resolution=[ 1e-9, 1e-9, 1e-9 ], upperBound=[0, 0, 0], infoSpec={}) {
    if( new.target === Annotation) {
      throw new Error("本类不能实例化")
    }
    this.infoFile = infoFile;
    this.upperBound = upperBound;
    this.resolution = resolution;
    this.infoSpec = infoSpec;
  }

  /**
   * Implement these methods in subclasses 
   * 
   * - parseSourceData(workbook, rawData) {} 
   * - encodingSingleAnnotation() {} 
   * - get bytesPerAnnotation() {}
   */ 

  async getRawData() {
    const rawData = new Map();
    await readWorkbookFromLocalFile(this.infoFile, (workbook) => {
      let sheetObj = workbook.Sheets.Sheet1;
      let [start_col, start_row, end_col, end_row] = sheetObj['!ref'].match(/([A-Z]*)([0-9]*):([A-Z]*)([0-9]*)/).slice(1);
      this.parseSourceData({
        start_col,
        end_col,
        start_row,
        end_row
      }, sheetObj,  rawData);
    });
    return rawData;
  }

  encodingAnnotation(rawDatas) {
    let offset = 0;
    let ids = [];
    const rawAnnotations = rawDatas.values();
    const count = rawDatas.size;
    const arrayBuffer = new ArrayBuffer(8 + count * (this.bytesPerAnnotation + 8));
    const dv = new DataView(arrayBuffer);
    dv.setBigUint64(0, BigInt(count), true);
    offset = 8;
    for(let annotation of rawAnnotations) {
      const { id } = annotation;
      ids.push(id);
      offset = this.encodingSingleAnnotation(dv, offset, annotation);
    }
    ids.forEach((id) => {
      dv.setBigUint64(offset, BigInt(id), true);
      offset += 8;
    })
    return dv;
  }

  encodingAnnotationIndex(annotation) {
    const buffer = new ArrayBuffer(this.bytesPerAnnotation);
    const dv = new DataView(buffer);
    this.encodingSingleAnnotation(dv, 0, annotation);
    return dv;
  }

  async writeToPrecomputed(targetDir) {
    const annotations = await this.getRawData();
    const encodedAnnotations = this.encodingAnnotation(annotations);

    const dirPath = `${cwd()}/${targetDir}`;
    const spatial0Dir = `${dirPath}/spatial0`;
    await makeDir(spatial0Dir);
    writeFile(`${spatial0Dir}/0_0_0`, encodedAnnotations);

    const byIdDir = `${dirPath}/by_id`;
    await makeDir(byIdDir)
    for(let annotation of annotations.values()) {
      writeFile(`${byIdDir}/${annotation.id}`, this.encodingAnnotationIndex(annotation))
    }

    this.infoContent["annotation_type"] = this.type;
    this.infoContent["spatial"][0]["chunk_size"] = this.upperBound;
    this.infoContent["upper_bound"] = this.upperBound;
    this.infoContent["dimensions"] = {
      "x": [ this.resolution[0], "m" ],
      "y": [ this.resolution[1], "m" ],
      "z": [ this.resolution[2], "m" ]
    }
    this.infoContent = {
      ...this.infoContent,
      ...this.infoSpec
    }
    writeFile(`${dirPath}/info`, JSON.stringify(this.infoContent))
  }

  async test() {
    console.log(await this.getRawData());
  }
}