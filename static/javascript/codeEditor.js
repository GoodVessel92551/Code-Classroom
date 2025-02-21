const params = new URLSearchParams(window.location.search);
const topic = params.get("project");
const projects = JSON.parse(localStorage.getItem("codeProjects"));


function outf(text) {
  const consoleText = document.getElementById("consoleText");
  consoleText.innerText += text;
}

// Skulpt uses builtinRead to load its standard library modules.
function builtinRead(x) {
  if (Sk.builtinFiles === undefined || Sk.builtinFiles["files"][x] === undefined) {
    throw "File not found: '" + x + "'";
  }
  return Sk.builtinFiles["files"][x];
}
var received_input = false
let currentHandler = null;

function inputFunction(promptText) {
  console.log("Input function called")
  received_input = false
  return new Promise((resolve) => {
      const inputElem = document.getElementById("consoleInput");
      inputElem.focus();
      inputElem.placeholder = promptText || "";
      inputElem.value = "";

      if (currentHandler) {
          inputElem.removeEventListener("keydown", currentHandler);
      }

      function handler(event) {
          if (event.key === "Enter" && !received_input) {
              received_input = true;
              event.preventDefault();
              const value = inputElem.value;
              inputElem.value = "";
              inputElem.removeEventListener("keydown", handler);
              currentHandler = null;
              resolve(value);
              inputElem.placeholder = "Type here and press Enter";
          }
      }

      currentHandler = handler;
      inputElem.addEventListener("keydown", handler);
  });
}

Sk.configure({
output: outf,
read: builtinRead,
inputfun: inputFunction,
inputfunTakesPrompt: true
});


function runPython(code) {
  if(!code.includes("input(")){
    console.log("Input detected");
    Sk.execLimit = 5000; 
    Sk.timeoutMsg = function () { return "Execution timed out."; };
  }
  const consoleText = document.getElementById("consoleText");
  consoleText.innerHTML = "";
  consoleText.style.color = "white";
  // Configure Skulpt to use our output and input functions.


  Sk.misceval.asyncToPromise(function() {
    return Sk.importMainWithBody("<stdin>", false, code, true);
  }).then(
    function(mod) {
      console.log("Success");
    },
    function(err) {
      consoleText.style.color = "#ff8f8f";
      create_result(err.toString());
      outf(err.toString());
    }
  );
}

// Initialize the Monaco editor.
require.config({ 
  paths: { 'vs': 'https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.44.0/min/vs' }
});
require(["vs/editor/editor.main"], function () {
  monaco.editor.defineTheme('myDarkTheme', {
    base: 'vs-dark',
    inherit: true,
    rules: [],
    colors: {
      'editor.background': '#1c202b',
      'editor.foreground': '#ffffff'
    }
  });
  monaco.editor.setTheme('myDarkTheme');
  monaco.languages.registerCompletionItemProvider('python', {
        provideCompletionItems: function () {
          return {
            suggestions: [
            {
                label: 'print',
                kind: monaco.languages.CompletionItemKind.Function,
                insertText: "print(${1:text})",
                insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
                documentation: "Prints the specified message to the console."
              },
              {
                label: 'input',
                kind: monaco.languages.CompletionItemKind.Function,
                insertText: "input('${1:Prompt}')",
                insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
                documentation: "Reads a line of input from the user."
              },
              {
                label: 'def',
                kind: monaco.languages.CompletionItemKind.Keyword,
                insertText: "def ${1:function_name}(${2:args}):\n    ${3:pass}",
                insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
                documentation: "Defines a new function."
              },
              {
                label: 'class',
                kind: monaco.languages.CompletionItemKind.Keyword,
                insertText: "class ${1:ClassName}:\n    def __init__(self, ${2:args}):\n        ${3:pass}",
                insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
                documentation: "Defines a new class."
              },
              {
                label: 'if',
                kind: monaco.languages.CompletionItemKind.Keyword,
                insertText: "if ${1:condition}:\n    ${2:pass}",
                insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
                documentation: "Creates an if statement."
              },
              {
                label: 'elif',
                kind: monaco.languages.CompletionItemKind.Keyword,
                insertText: "elif ${1:condition}:\n    ${2:pass}",
                insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
                documentation: "Creates an elif statement."
              },
              {
                label: 'else',
                kind: monaco.languages.CompletionItemKind.Keyword,
                insertText: "else:\n    ${1:pass}",
                insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
                documentation: "Creates an else statement."
              },
              {
                label: 'for',
                kind: monaco.languages.CompletionItemKind.Keyword,
                insertText: "for ${1:var} in ${2:iterable}:\n    ${3:pass}",
                insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
                documentation: "Creates a for loop."
              },
              {
                label: 'while',
                kind: monaco.languages.CompletionItemKind.Keyword,
                insertText: "while ${1:condition}:\n    ${2:pass}",
                insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
                documentation: "Creates a while loop."
              },
              {
                label: 'try',
                kind: monaco.languages.CompletionItemKind.Keyword,
                insertText: "try:\n    ${1:pass}\nexcept ${2:Exception} as e:\n    ${3:print(e)}",
                insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
                documentation: "Creates a try-except block."
              },
              {
                label: 'with',
                kind: monaco.languages.CompletionItemKind.Keyword,
                insertText: "with open('${1:file}', '${2:mode}') as ${3:var}:\n    ${4:pass}",
                insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
                documentation: "Creates a with open statement."
              },
              {
                label: 'open',
                kind: monaco.languages.CompletionItemKind.Function,
                insertText: "open('${1:file}', '${2:mode}')",
                insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
                documentation: "Opens a file."
              },
              {
                label: 'import',
                kind: monaco.languages.CompletionItemKind.Keyword,
                insertText: "import ${1:module_name}",
                insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
                documentation: "Imports a module."
              },
              {
                label: 'from_import',
                kind: monaco.languages.CompletionItemKind.Keyword,
                insertText: "from ${1:module_name} import ${2:function_name}",
                insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
                documentation: "Imports a specific function from a module."
              },
              {
                label: 'lambda',
                kind: monaco.languages.CompletionItemKind.Keyword,
                insertText: "lambda ${1:args}: ${2:expression}",
                insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
                documentation: "Creates a lambda function."
              },
              {
                label: 'range',
                kind: monaco.languages.CompletionItemKind.Function,
                insertText: "range(${1:start}, ${2:stop}, ${3:step})",
                insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
                documentation: "Generates a sequence of numbers."
              },
              {
              label: 'try',
              kind: monaco.languages.CompletionItemKind.Keyword,
              insertText: "try:\n    ${1:pass}\nexcept ${2:Exception} as e:\n    ${3:print(e)}",
              insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
              documentation: "Creates a try-except block."
            },
            {
              label: 'except',
              kind: monaco.languages.CompletionItemKind.Keyword,
              insertText: "except ${1:Exception} as e:\n    ${2:pass}",
              insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
              documentation: "Handles exceptions."
            },
            {
              label: 'finally',
              kind: monaco.languages.CompletionItemKind.Keyword,
              insertText: "finally:\n    ${1:pass}",
              insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
              documentation: "Defines a final block after try-except."
            },
            {
              label: 'break',
              kind: monaco.languages.CompletionItemKind.Keyword,
              insertText: "break",
              documentation: "Exits a loop."
            },
            {
              label: 'continue',
              kind: monaco.languages.CompletionItemKind.Keyword,
              insertText: "continue",
              documentation: "Skips the rest of the current iteration of a loop."
            },
            {
              label: 'pass',
              kind: monaco.languages.CompletionItemKind.Keyword,
              insertText: "pass",
              documentation: "Does nothing; used as a placeholder."
            }
            ]
          };
        }
      });
    if (projects){
      const project = projects[topic];
      console.log(project);
        if (project){
          loadedCode = project.code;
          pageTitleDivButtons.style.display = "flex";
          projectName.value = project.name;
        }else{
          var loadedCode = localStorage.getItem("code");
          if(!loadedCode){
            loadedCode = "print('Hello, world!')";
          }
        }
      }else{
        var loadedCode = localStorage.getItem("code");
        if(!loadedCode){
          loadedCode = "print('Hello, world!')";
        }
      }
  window.editor = monaco.editor.create(document.getElementById("editor"), {
    value: loadedCode,
    language: "python",
    theme: "myDarkTheme"
  });
});

window.editor.addEventListener("keydown", (event) => {
  const code = window.editor.getValue();
  if (projects){
    const project = projects[topic];
      if (project){
        projects[topic].code = code;
        localStorage.setItem("codeProjects", JSON.stringify(projects));
      }else{
        localStorage.setItem("code", code);
      }
    }else{
      localStorage.setItem("code", code);
    }
  if (event.key === "Enter" && event.ctrlKey) {
    event.preventDefault();
    const code = window.editor.getValue();
    runPython(code);
  }
});


document.getElementById("runButton").addEventListener("click", () => {
  const code = window.editor.getValue();
  runPython(code);
});

// (Optional) Bind the clear button to clear the console.
document.getElementById("clearConsole").addEventListener("click", () => {
  document.getElementById("consoleText").innerHTML = "";
});

window.addEventListener("resize", function () {
  if (window.editor) {
    window.editor.layout();
  }
});
