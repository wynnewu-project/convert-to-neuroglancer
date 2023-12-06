import { read } from "xlsx";
import { readFile, mkdir } from "node:fs/promises";
import { generate } from "@ant-design/colors"
import jspkg from 'jstat';
const { jStat } = jspkg;

export function parseColorSpec(colorStr) {
  console.log('color', colorStr)
  const hexPattern = /^#([0-9a-fA-F]{2})([0-9a-fA-F]{2})([0-9a-fA-F]{2})$/;
  {
    const m = colorStr.match(hexPattern);
    if (m !== null) {
      return [parseInt(m[1], 16), parseInt(m[2], 16), parseInt(m[3], 16) ];
    }
  }
}

export function parseColorSpecToFloat(colorStr) {
  const color = parseColorSpec(colorStr);
  return color.map(x => Number((x/255).toFixed(3)))
}

export function getColorMap(color) {
  return generate(color, {
    theme: "dark",
    backgroundColor: "#000"
  })
}

export function linearColorAlpha(value) {
  if(value < 1E-5) return 26;
  let alphaMap = {5: 51, 4:77, 3: 102, 2: 153, 1:255};
  let alphaLevel = Math.abs(Math.floor(Math.log10(value))); 
  return alphaMap[alphaLevel];
}

export function linearColorSaturation(color, value, alpha=255) {
  console.log('linerColor saturation color', color, value)
  let m = {5:1, 4:3, 3:5, 2:7, 1:9};
  let colorMap = getColorMap(color);
  if(value < 1E-5) return [...parseColorSpec(colorMap[1]), alpha];
  let colorLevel = m[Math.abs(Math.floor(Math.log10(value)))];
  console.log('color map', colorMap)
  console.log('color level', colorLevel)
  return defaultColorHandler(colorMap[colorLevel], null, alpha);
}

export function linearSegmentLineColor(color, lineArr, value, alpha=255) {
  const colorMap = getColorMap(color);
  const colorLevel = getColorLevel(lineArr, value);
  console.log('value:', value, 'colorLevel:', colorLevel)
  return defaultColorHandler(colorMap[colorLevel], null, alpha);
}

export function linearLineWidth(value) {
  if(value < 1E-5) return 1;
  return Math.floor(Math.log10(value)) + 7;
}

export async function readWorkbookFromLocalFile(file, callback) {
  let fileContents = await readFile(file);
  let fileForXlsx = read(fileContents, { type: 'buffer'});
  if(callback) {
    callback(fileForXlsx)
  }
}

export function defaultRadiiHandler() {
  return 10;
}

export function defaultColorHandler(color, sid, alpha=255) {
  return [...parseColorSpec(color), alpha];
}

export function defaultLineWidthHandler(value) {
  return 1;
}

export function getColorLevel(numArray, value) {
  let percentile = jStat.percentileOfScore(numArray, value, "strict");
  let level = Math.round(percentile * 10) - 1;
  if(level < 0) return 0;
  return level;
}

export async function makeDir(dirPath, callback) {
  await mkdir(dirPath, { recursive: true });
}

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

export function parseParams(argvs, helpInfo="", params=false) {
  if(params && !argvs.length) {
    console.log("Help: \n", helpInfo);
  }
  return Object.fromEntries(
    argvs.reduce((pre, item) => {
      if(item.startsWith("--")) {
        const [option, value] = item.slice(2).split("=");
        if(option === "help") {
          console.log("Help: \n", helpInfo);
        } else {
          let v;
          try {
            v = JSON.parse(value);
          } catch (e) {
            v = value;
          }
          return [...pre, [option, v]];
        }
      }
      return pre;
    }, [])
  )
}


