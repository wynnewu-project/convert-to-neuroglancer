import { readWorkbookFromLocalFile, makeDir} from "./utils.mjs";
import { writeFile, open } from "node:fs/promises";
import { cwd } from "node:process";
import { parseParams } from "./utils.mjs";
import path from "node:path";

export const TYPE_BYTES_LENGTH = {
  "rgb": 3,
  "rgba": 4,
  "uint8": 1,
  "int8": 1,
  "uint16": 2,
  "int16": 2,
  "uint32": 4,
  "int32": 4,
  "float32": 4
}

export const TYPE_HANDLER = {
  "int8": "setInt8",
  "uint8": "setUint8",
  "uint16": "setUint16",
  "int16": "setInt16",
  "uint32": "setUint32",
  "int32": "setInt32",
  "float32": "setFloat32"
}

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
   * @param {*} infoFile - excel, csv, txt, swc
   */
  constructor({ 
    infoFile, 
    targetDir,
    resolution=[ 1e-9, 1e-9, 1e-9 ], 
    upperBound=[1000, 1000, 1000], 
    lowerBound=[0, 0, 0],
    infoSpec={},
    generateIndex=false
  }) {
    if( new.target === Annotation) {
      throw new Error("本类不能实例化")
    }
    this.infoFile = infoFile;
    this.resolution = resolution;
    this.generateIndex = generateIndex;
    this.targetDir = targetDir;
    this.infoContent = {
      ...this.infoContent,
      lower_bound: lowerBound,
      upper_bound: upperBound,
      ...infoSpec
    }
    this.infoContent["spatial"][0]["chunk_size"] = upperBound;
  }

  /**
   * Implement these methods in subclasses 
   */ 
  parseAnnotation(annotation) {
    return annotation.map(value => ({type: "float32", value}))
  }
  encodingSingleAnnotation() {}

  getBytesPerAnnotation() {
    const { properties=[] } = this.infoContent;
    let bytes = this.basicBytesPerAnnotation;
    for(let propery of properties) {
      const { type } = propery;
      bytes += TYPE_BYTES_LENGTH[type];
    }
    return bytes;
  }

  parseProperties(propertyId, properties, type="float32") {
    if(!this.infoContent.properties.filter(item => item.id === propertyId).length) {
      this.infoContent.properties.push({
        "id": propertyId,
        "type": type
      })
    }
    return properties.map(value => ({ type: type.startsWith("rgb") ? "uint8" : type, value }));
  }



  async getRawDataFromExcel(rawData) {
    await readWorkbookFromLocalFile(this.infoFile, (workbook) => {
      let sheetObj = workbook.Sheets.Sheet1;
      let [start_col, start_row, end_col, end_row] = sheetObj['!ref'].match(/([A-Z]*)([0-9]*):([A-Z]*)([0-9]*)/).slice(1);
      let count = 0;
      for(let row = Number(start_row); row <= Number(end_row); row++) {
        count += 1;
        const annotation = [];
        for(let col = start_col.charCodeAt(0); col <= end_col.charCodeAt(0); col++) {
          const col_tag = String.fromCharCode(col)
          annotation.push(sheetObj[col_tag + row].v)
        }
        rawData.set(count, { 
          id: count,
          annotation: this.parseAnnotation(annotation)
        });
      }
    });
  }


  async getRawDataFromText(rawData) {
    const file = await open(this.infoFile);
    let count = 0;
    for await (const line of file.readLines()) {
      count += 1;
      const annotation = line.split(/[,\s|\t;]/).map(x => Number(x))
      rawData.set(count, { 
        id: count,
        annotation: this.parseAnnotation(annotation)
      });
    }
    file.close();
  }

  encodingSingleAnnotation(dv, offset, annotation) {
    for(let item of annotation) {
      const { type, value } = item;
      if(type.endsWith("int8")) {
        dv[TYPE_HANDLER[type]](offset, value);
      } else {
        dv[TYPE_HANDLER[type]](offset, value, true);
      }
      offset += TYPE_BYTES_LENGTH[type];
    }
    return offset;
  }



  encodingAnnotation(rawDatas) {
    let offset = 0;
    let ids = [];
    const rawAnnotations = rawDatas.values();
    const count = rawDatas.size;
    const arrayBuffer = new ArrayBuffer(8 + count * (this.getBytesPerAnnotation() + 8));
    const dv = new DataView(arrayBuffer);
    dv.setBigUint64(0, BigInt(count), true);
    offset = 8;
    for(let item of rawAnnotations) {
      const { id, annotation } = item;
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
    const buffer = new ArrayBuffer(this.getBytesPerAnnotation());
    const dv = new DataView(buffer);
    this.encodingSingleAnnotation(dv, 0, annotation);
    return dv;
  }

  async getRawData(extname, annotations) {
    if(extname === ".xlsx" || extname === ".xls") {
      await this.getRawDataFromExcel(annotations);
    } else {
      await this.getRawDataFromText(annotations);
    }
  }

  async writeToPrecomputed() {
    const annotations = new Map();
    const extname = path.extname(this.infoFile);
    await this.getRawData(extname, annotations);
    const encodedAnnotations = this.encodingAnnotation(annotations);

    const dirPath = this.targetDir?.startsWith("/") ? this.targetDir : `${cwd()}/${this.targetDir ?? `annotations_${this.type}`}`;
    const spatial0Dir = `${dirPath}/spatial0`;
    await makeDir(spatial0Dir);
    writeFile(`${spatial0Dir}/0_0_0`, encodedAnnotations);

    if(this.generateIndex) {
      const byIdDir = `${dirPath}/by_id`;
      await makeDir(byIdDir)
      for(let item of annotations.values()) {
        const { id, annotation } = item;
        await writeFile(`${byIdDir}/${id}`, this.encodingAnnotationIndex(annotation))
      }
    }

    this.infoContent["annotation_type"] = this.type;
    this.infoContent["dimensions"] = {
      "x": [ this.resolution[0], "m" ],
      "y": [ this.resolution[1], "m" ],
      "z": [ this.resolution[2], "m" ]
    }
    writeFile(`${dirPath}/info`, JSON.stringify(this.infoContent))
  }

  static run(AnnotationType) {
    const helpInfo = `
Required options:
--infoFile: File path to store the defined information of annotations 
--resolution: physical resolution in unit 'm'

Optional Options:
--lowerBound: Array of numbers of length rank specifying the lower bound in the units specified by resolution. Default is [0,0,0]
--upperBound: Array of numbers of length rank specifying the exclusive upper bound in the units specified by resolution. All annotation geometry should be contained within the bounding box defined by lower_bound and upper_bound.Default is [1000, 1000, 1000]
--targetDir: Output folder
--generateIndex: Whether to generate encoded respresentation for each single annotation and save it in a separate file. It will be used by Neuroglancer when selecting or hovering over an annotation. Default is false.
    `
    const args = parseParams(process.argv.slice(2), helpInfo, true);
    if(JSON.stringify(args) === "{}" ) {
      return;
    }
    const annotation = new AnnotationType(args);
    annotation.writeToPrecomputed()
  }
}