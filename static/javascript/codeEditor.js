// Parse URL params to determine which project (if any) we're editing.
// Example: /quickCode?project=myProject
const params = new URLSearchParams(window.location.search);
const topic = params.get("project");
// Load saved projects from localStorage (may be null if nothing saved yet).
const projects = JSON.parse(localStorage.getItem("codeProjects"));

// If we're on the quickCode page but no valid project is specified, redirect
// back to the main code listing page so the user picks a project first.
if (window.location.href.includes("/quickCode") && (topic == null || topic == "" || !(projects && Object.keys(projects).includes(topic)))) {
  window.location.href = "/code";
}

/**
 * Output function used by Skulpt to write text to the in-page console.
 * Appends text to the `#consoleText` element.
 *
 * @param {string} text Text to append to the console output area.
 */
function outf(text) {
  const consoleText = document.getElementById("consoleText");
  consoleText.innerText += text;
}

// Skulpt uses builtinRead to load its standard library modules.
/**
 * builtinRead is required by Skulpt. It provides access to built-in files
 * (the Skulpt standard library) when Python code running in the browser
 * does an import. If a file can't be found, it throws so Skulpt reports an error.
 *
 * @param {string} x Module/file path requested by Skulpt.
 * @returns {string} Contents of the requested builtin file.
 */
function builtinRead(x) {
  if (Sk.builtinFiles === undefined || Sk.builtinFiles["files"][x] === undefined) {
    throw "File not found: '" + x + "'";
  }
  return Sk.builtinFiles["files"][x];
}
var received_input = false
let currentHandler = null;

/**
 * inputFunction is an async bridge between Skulpt's input() and the DOM.
 * It shows a text input element, waits for the user to press Enter, then
 * resolves the returned Promise with the provided string.
 *
 * Behavior notes:
 *  - Ensures only one handler is active at a time using `currentHandler`.
 *  - Hides the input element after submission and restores a default placeholder.
 *
 * @param {string} promptText Optional prompt to show as the input placeholder.
 * @returns {Promise<string>} Resolves to the user's input string.
 */
function inputFunction(promptText) {
  received_input = false
  return new Promise((resolve) => {
    const inputElem = document.getElementById("consoleInput");
    // Make the input visible and ready for typing.
    inputElem.style.display = "block";
    inputElem.focus();
    inputElem.placeholder = promptText || "";
    inputElem.value = "";

    // Remove any previously attached handler to avoid double resolution.
    if (currentHandler) {
      inputElem.removeEventListener("keydown", currentHandler);
    }

    function handler(event) {
      // Resolve when the user presses Enter. Guard with `received_input`
      // so rapid double events can't resolve twice.
      if (event.key === "Enter" && !received_input) {
        received_input = true;
        event.preventDefault();
        const value = inputElem.value;
        inputElem.value = "";
        inputElem.removeEventListener("keydown", handler);
        currentHandler = null;
        resolve(value);
        inputElem.style.display = "none";
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
  // If the code does not use input(), apply an execution limit to avoid
  // runaway scripts. When input() is present we can't reliably apply the
  // same exec limit because the runtime will wait for user input.
  if (!code.includes("input")) {
    Sk.execLimit = 5000;
    Sk.timeoutMsg = function () { return "Execution timed out."; };
  }

  // Prepare the console output area and reset styles for a new run.
  const consoleText = document.getElementById("consoleText");
  consoleText.innerHTML = "";
  consoleText.style.color = "white";

  // Run the code using Skulpt's async helper. Errors are caught and
  // displayed to the user (colored red-ish) and also passed to `create_result`.
  Sk.misceval.asyncToPromise(function () {
    return Sk.importMainWithBody("<stdin>", false, code, true);
  }).then(
    function (mod) {
      // Successful execution: nothing further to do here.
    },
    function (err) {
      consoleText.style.color = "#ff8f8f";
      // create_result appears to present error info elsewhere in the UI.
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
  // Register a small set of completion snippets for the embedded Python
  // Monaco editor. These are lightweight helpers for beginners.
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
  // Determine the initial editor contents:
  // 1) If a `projects` object exists and a project for `topic` exists, load
  //    that project's code and update UI pieces (title, name).
  // 2) Otherwise fall back to the single `code` value in localStorage.
  if (projects) {
    const project = projects[topic];
    console.log(project);
    if (project) {
      loadedCode = project.code;
      // Show project-specific controls when editing a named project.
      pageTitleDivButtons.style.display = "flex";
      projectName.value = project.name;
    } else {
      var loadedCode = localStorage.getItem("code");
      if (!loadedCode) {
        loadedCode = "print('Hello, world!')";
      }
    }
  } else {
    var loadedCode = localStorage.getItem("code");
    if (!loadedCode) {
      loadedCode = "print('Hello, world!')";
    }
  }

  if (window.location.href.includes("/learningPathTask")) {
    loadedCode = loadedTaskCode;
  }

  if (loadedTaskCode && (window.location.href.includes("/task/") || window.location.href.includes("/view/"))) {
    console.log("Loaded task code");
    loadedCode = loadedTaskCode;
  }
  window.editor = monaco.editor.create(document.getElementById("editor"), {
    value: loadedCode,
    language: "python",
    theme: "myDarkTheme",
    tabSize: 8,
    indentSize: 8,
    detectIndentation: false
  });
});

// Listen for key events in the editor to autosave and run the code when
// Ctrl+Enter is pressed.
window.editor.addEventListener("keydown", (event) => {
  const code = window.editor.getValue();
  // Don't save when viewing code in read-only `view` mode.
  if (!window.location.href.includes("/view/")) {
    if (projects) {
      const project = projects[topic];
      if (project) {
        // Save into the named projects map.
        projects[topic].code = code;
        localStorage.setItem("codeProjects", JSON.stringify(projects));
      }

      else {
        // No projects map — save to the simple `code` key.
        localStorage.setItem("code", code);
      }
    } if (window.location.href.includes("/learningPathTask")) {
      // If this is a learning path task, update the in-memory structure
      // and persist it.
      console.log(learningPath)
      var newlearningPath = learningPath;
      newlearningPath.tasks[taskKeys[currentTask]].code = code;
      localStorage.setItem("learningPath", JSON.stringify(newlearningPath));
    }

    else {
      localStorage.setItem("code", code);
    }
  }

  // Ctrl+Enter -> execute the code in the embedded Python runtime.
  if (event.key === "Enter" && event.ctrlKey) {
    event.preventDefault();
    const code = window.editor.getValue();
    runPython(code);
  }
});


document.getElementById("runButton").addEventListener("click", () => {
  const code = window.editor.getValue();
  if (window.location.href.includes("/task/")) {
    saveCode();
  }
  runPython(code);
});


const saveCode = () => {
  const code = window.editor.getValue();
  fetch("/endpoint/task/save", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      classid: classid,
      taskid: taskid,
      code: code,
    }),
  })
    .then((data) => {
      if (data.status == 200) {
        const editorBottonBar = document.getElementById("editorBottomBar");
        editorBottonBar.textContent = "Saved";
      } else {
        const editorBottonBar = document.getElementById("editorBottomBar");
        editorBottonBar.textContent = "Error saving";
      }
    })
    .catch((error) => {
      console.error("Error:", error);
    });
  return
}

/**
 * Save code for the current task by POSTing to the server endpoint.
 * On success, updates the UI to indicate the save succeeded.
 * On failure, shows an error label and logs the problem.
 */

document.getElementById("clearConsole").addEventListener("click", () => {
  document.getElementById("consoleText").innerHTML = "";
});

window.addEventListener("resize", function () {
  if (window.editor) {
    window.editor.layout();
  }
});

if (window.location.href.includes("/task/")) {
  editor.addEventListener("keydown", (event) => {
    const editorBottonBar = document.getElementById("editorBottomBar");
    editorBottonBar.textContent = "Unsaved changes";
  })
}