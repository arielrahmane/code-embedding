import { Project, Node, ts } from "ts-morph";
import fs from "fs";
import path from "path";

const project = new Project();

// Replace with the path to your TypeScript file
const filePath = path.join(__dirname, "../data/action_sd_generations.ts");
const sourceFile = project.addSourceFileAtPath(filePath);

const chunks: Array<{
  type: string;
  details: string;
  code: string;
  parent: {
    code: string;
    type: string;
  };
}> = [];

// Helper function to add a chunk
function addChunk(
  type: string,
  details: string,
  code: string,
  parent: {
    code: string;
    type: string;
  }
) {
  chunks.push({ type, details, code, parent });
}

// Find the handler function
const handlerVariable = sourceFile.getVariableDeclaration("handler");
const handlerFunction = handlerVariable?.getInitializerIfKindOrThrow(
  ts.SyntaxKind.ArrowFunction
);

let numberOfLargeParents = 0;

if (handlerFunction) {
  // Traverse the body of the handler function
  let index = 0;
  handlerFunction.forEachDescendant((node) => {
    let parent = node.getParent();
    if (
      parent?.getKindName() === "ArrowFunction" ||
      parent?.getEndLineNumber() === 3400
    ) {
      parent = undefined;
    }
    if (Node.isIfStatement(node)) {
      addChunk("if statement", "Conditional Check", node.getText(), {
        code: parent?.getText() || "",
        type: parent?.getKindName() || ""
      });
    } else if (Node.isSwitchStatement(node)) {
      addChunk("switch statement", "Switch Case Check", node.getText(), {
        code: parent?.getText() || "",
        type: parent?.getKindName() || ""
      });
    } else if (Node.isVariableDeclaration(node)) {
      const varName = node.getName();
      addChunk("variable declaration", `Variable: ${varName}`, node.getText(), {
        code: parent?.getText() || "",
        type: parent?.getKindName() || ""
      });
    } else if (Node.isAwaitExpression(node)) {
      addChunk("await expression", "Asynchronous Action", node.getText(), {
        code: parent?.getText() || "",
        type: parent?.getKindName() || ""
      });
    } else if (Node.isCallExpression(node)) {
      const funcName = node.getExpression().getText();
      addChunk("function call", `Function Call: ${funcName}`, node.getText(), {
        code: parent?.getText() || "",
        type: parent?.getKindName() || ""
      });
    } else {
      addChunk("other", "Other type of chunk", node.getText(), {
        code: parent?.getText() || "",
        type: parent?.getKindName() || ""
      });
    }
    index++;
  });
}

// Write the parsed chunks to a file for inspection
const outputFilePath = path.join(__dirname, "../chunks/handler_chunks.json");
fs.writeFileSync(outputFilePath, JSON.stringify(chunks, null, 2));
