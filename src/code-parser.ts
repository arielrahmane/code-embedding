import { Project, Node, ts } from "ts-morph";
import fs from "fs";
import path from "path";

const project = new Project();

const filePath = path.join(__dirname, "../data/action_sd_generations.ts");
const sourceFile = project.addSourceFileAtPath(filePath);

const chunks: Array<{
  type: string;
  width: number;
  position: number;
  startLineNumber: number;
  code: string;
}> = [];

function addChunk(
  type: string,
  width: number,
  position: number,
  startLineNumber: number,
  code: string
) {
  chunks.push({ type, width, position, startLineNumber, code });
}

const handlerVariable = sourceFile.getVariableDeclaration("handler");
const handlerFunction = handlerVariable?.getInitializerIfKindOrThrow(
  ts.SyntaxKind.ArrowFunction
);

if (handlerFunction) {
  let index = 0;
  handlerFunction.getBody().forEachChild((node) => {
    addChunk(
      node.getKindName(),
      node.getFullWidth(),
      node.getPos(),
      node.getStartLineNumber(),
      node.getText()
    );
    index++;
  });
}

console.log(chunks.length);
const outputFilePath = path.join(__dirname, "../chunks/handler_chunks.json");
fs.writeFileSync(outputFilePath, JSON.stringify(chunks, null, 2));
