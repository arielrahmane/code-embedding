import { Project, Node, ts } from "ts-morph";
import fs from "fs";
import path from "path";

const project = new Project();

const filePath = path.join(__dirname, "../data/action_sd_generations.ts");
const sourceFile = project.addSourceFileAtPath(filePath);

const chunks: Array<{
  type: string;
  details: string;
  code: string;
}> = [];

function addChunk(type: string, details: string, code: string) {
  chunks.push({ type, details, code });
}

const handlerVariable = sourceFile.getVariableDeclaration("handler");
const handlerFunction = handlerVariable?.getInitializerIfKindOrThrow(
  ts.SyntaxKind.ArrowFunction
);

if (handlerFunction) {
  let index = 0;
  handlerFunction.getBody().forEachChild((node) => {
    if (Node.isIfStatement(node)) {
      addChunk("if statement", "Conditional Check", node.getText());
    } else if (Node.isSwitchStatement(node)) {
      addChunk("switch statement", "Switch Case Check", node.getText());
    } else if (Node.isVariableDeclaration(node)) {
      const varName = node.getName();
      addChunk("variable declaration", `Variable: ${varName}`, node.getText());
    } else if (Node.isAwaitExpression(node)) {
      addChunk("await expression", "Asynchronous Action", node.getText());
    } else if (Node.isCallExpression(node)) {
      const funcName = node.getExpression().getText();
      addChunk("function call", `Function Call: ${funcName}`, node.getText());
    } else {
      addChunk("other", "Other type of chunk", node.getText());
    }
    index++;
  });
}

console.log(chunks.length);
const outputFilePath = path.join(__dirname, "../chunks/handler_chunks.json");
fs.writeFileSync(outputFilePath, JSON.stringify(chunks, null, 2));
