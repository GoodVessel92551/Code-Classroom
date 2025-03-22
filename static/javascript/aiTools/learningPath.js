const aiText = document.getElementById("aiText");
const aiMarkdown = document.getElementById("aiMarkdown")
const taskMarkdown1 = document.getElementById("taskMarkdown1")
const taskTitle1 = document.getElementById("taskTitle1")
const taskText1 = document.getElementById("taskText1")
const taskMarkdown2 = document.getElementById("taskMarkdown2")
const taskTitle2 = document.getElementById("taskTitle2")
const taskText2 = document.getElementById("taskText2")
const taskMarkdown3 = document.getElementById("taskMarkdown3")
const taskTitle3 = document.getElementById("taskTitle3")
const taskText3 = document.getElementById("taskText3")
const taskMarkdown4 = document.getElementById("taskMarkdown4")
const taskTitle4 = document.getElementById("taskTitle4")
const taskText4 = document.getElementById("taskText4")
const taskMarkdown5 = document.getElementById("taskMarkdown5")
const taskTitle5 = document.getElementById("taskTitle5")
const taskText5 = document.getElementById("taskText5")
const createText = document.getElementById("createText")
const tasksLearningPath = document.getElementById("tasksLearningPath")
const learningPathText = document.getElementById("learningPathText")
const learningPathButton = document.getElementById("learningPathButton")
const learningPathThininking = document.getElementById("learningPathThininking")
const learningPathButtonStart = document.getElementById("learningPathButtonStart")

let masterData = {}
let taskNumCount = 0;
Object.keys(usersClasses).forEach(key => {
    usersClasses[key].members.forEach(member => {
        if(member.id == userID){
            if(member.role == "teacher"){
                classRole = "teacher";
            }else{
                classRole = "student";
            }
        }
    })
    if(classRole == "teacher"){
        return
    }
    Object.keys(usersClasses[key].tasks).forEach(task => {
        let taskInfo = usersClasses[key].tasks[task];
        let taskInfoSimple = taskInfo
        let studentData = taskInfoSimple.student_data[Object.keys(taskInfo.student_data)[0]];
        console.log(studentData)
        if(studentData == undefined){
            taskInfoSimple.status = "Not Started";
        }else{
            taskInfoSimple.feedback = studentData.feedback;
            taskInfoSimple.taskStatus = studentData.status;
        }
        delete taskInfoSimple.student_data;
        delete taskInfoSimple.taskPoints;
        delete taskInfoSimple.taskId;
        delete taskInfoSimple.taskDue;
        delete taskInfoSimple.id;
        delete taskInfoSimple.status
        masterData[taskNumCount] = taskInfoSimple;
        taskNumCount++;
    })
});

var available_ai = false;
document.addEventListener("DOMContentLoaded", async () => {
  try{
    var capabilities = await ai.languageModel.availability();
  }catch{
    console.log(capabilities)
      console.error("No AI")
        return
  }
  if (capabilities.available == "no" || capabilities.available == "after-download")console.error("No AI")
  available_ai = true;
    session = await ai.languageModel.create({
        systemPrompt: "You will have to summarize what topics in python the user is currently doing. To do this you will be given two things the first the 2 two weak topics and then you will get a json object of the task that the students is doing currently. Try to keep it concise and to the point and do not name tasks only comment on the topics and skills that they currently doing. Also output like you are think about this. Do **NOT** name any task just say the topics/areas that the student is currently working on.",
  })
})

const create_result = async () => {
    createText.textContent = "Creating"
    console.log(available_ai);
    if (available_ai) {
        var totalOutput = "";
        const stream = await session.promptStreaming("Tasks: " + JSON.stringify(masterData)+ "\n\n Weak Topics: " + JSON.stringify(weakTopics[0][0]) + ", " + JSON.stringify(weakTopics[0][1]));
        for await (const chunk of stream) {
            aiMarkdown.style.display = "block"
            console.log(chunk);
            totalOutput += chunk;
            aiText.textContent = totalOutput;
        }
        console.log(totalOutput);
    }
    session.destroy()
    session = await ai.languageModel.create({
        initialPrompts: [
            { "role": "system", "content": "You will receive details about a student's coding strengths and weaknesses. Generate 5 relevant task titles in the **JSON** list format to help them improve make the titles as concise as possible and make sure not use any task in the input prompt. The task should be able to be completed in Python **without any** libraries and the tasks should be simple. The task can not use any libraries apart from the random and math libraries. The tasks can also not use anything that needs access to files. The first task should be the easiest and the task can build on each other." },
          
            { "role": "user", "content": "The student understands basic Python functions and conditional statements but struggles with loops, especially nested loops and while loops. They also need more practice with function parameters and return values." },
            { "role": "assistant", "content": '["Practice with While Loops: Counting Down","Understanding Nested Loops: Multiplication Table","Functions with Parameters: Greeting Generator","Using Return Values: Simple Calculator","Loop Practice: Finding the Largest Number"]' },
          
            { "role": "user", "content": "The student has a solid grasp of variables and functions but struggles with manipulating lists and strings. They need more practice with slicing, list comprehension, and string formatting." },
            { "role": "assistant", "content": '["String Slicing: Extracting Substrings","List Comprehension: Squaring Numbers","Basic String Formatting: Creating Sentences","Reversing Strings Without Built-in Functions","Summing Numbers in a List"]' },
          
            { "role": "user", "content": "The student understands basic loops and lists but struggles with recursion. They need more practice with breaking down problems into smaller recursive steps and understanding the base case concept." },
            { "role": "assistant", "content": '["Recursive Counting Down","Finding Factorial Recursively","Summing a List Recursively","Recursive String Reversal","Understanding Base Cases with Simple Addition"]' },
          
            { "role": "user", "content": "The student understands Python basics but struggles with debugging. They often face logical errors and need help identifying mistakes in their code." },
            { "role": "assistant", "content": '["Finding and Fixing Syntax Errors","Spot the Logical Error","Debugging a Simple Loop","Fixing Incorrect Function Outputs","Understanding Error Messages"]' },
          
            { "role": "user", "content": "The student can write basic Python scripts but needs to develop better problem-solving skills. They struggle with breaking down problems and designing efficient solutions." },
            { "role": "assistant", "content": '["Breaking a Problem into Steps","Finding the Most Efficient Loop","Sorting Numbers Manually","Designing a Simple Algorithm","Solving a Basic Puzzle with Code"]' }
          ]
          });
        console.log("Prompting")
        let attempts = 0;
        let result;
        const maxAttempts = 3;

        while (attempts < maxAttempts) {
            result = await session.prompt(totalOutput);
            try {
                const parsedResult = JSON.parse(result);
                if (Array.isArray(parsedResult)) {
                    result = parsedResult;
                    break;
                }
                console.log(`Attempt ${attempts + 1}: Result is not an array, retrying...`);
            } catch (e) {
                console.log(`Attempt ${attempts + 1}: Invalid JSON, retrying...`);
            }
            attempts++;
        }

        if (attempts === maxAttempts) {
            console.warn("Failed to get valid array result after maximum attempts");
            result = [];
        }
        console.log(result);
        tasksLearningPath.style.display = "flex"
        learningPathText.style.display = "none"
        learningPathButton.style.display = "none"
        learningPathThininking.style.display = "none"
        if (result.length == 0) {
            return;
        }else if (result.length == 1){
            taskTitle1.textContent = result[0];
        }else if (result.length == 2){
            taskTitle1.textContent = result[0];
            taskTitle2.textContent = result[1];
        }else if (result.length == 3){
            taskTitle1.textContent = result[0];
            taskTitle2.textContent = result[1];
            taskTitle3.textContent = result[2];
        }else if (result.length == 4){
            taskTitle1.textContent = result[0];
            taskTitle2.textContent = result[1];
            taskTitle3.textContent = result[2];
            taskTitle4.textContent = result[3];
        }else{
            taskTitle1.textContent = result[0];
            taskTitle2.textContent = result[1];
            taskTitle3.textContent = result[2];
            taskTitle4.textContent = result[3];
            taskTitle5.textContent = result[4];
        }
        session.destroy()
        session = await ai.languageModel.create({
                systemPrompt: "You will be given a title for a task that will be completed in python. You need to write the instructions for the tasks not not include the code need to complete it. Keep the instructions clear and concise and **SHORT** and make sure to include all the information needed to complete the task also teach the user what they need to know. The task should be able to be completed in Python **without any** libraries and the tasks should be simple. The task can not use any libraries apart from the random and math libraries. The tasks can also not use anything that needs access to files.",
        })
        var learningPath = {
            "info":{
                "started": false,
                "completed": false,
                "currentTask": 0
            },
            "tasks": {}
        }
        for (let i = 0; i < result.length; i++) {
            const task = result[i];
            learningPath["tasks"][task] = {"task": task, "instructions": "","code": ""}
            if (available_ai) {
            var totalOutput = "";
            aiMarkdown.style.display = "block";
            const stream = await session.promptStreaming("Task Title: "+ task);
            let currentTaskText;
            let currentTaskMarkdown;
            for await (const chunk of stream) {
                console.log(i);
                totalOutput += chunk;
                
                
                if (i == 0) {
                    taskMarkdown1.style.display = "block";
                    taskText1.textContent = totalOutput;
                    currentTaskText = taskText1;
                    currentTaskMarkdown = taskMarkdown1;
                } else if (i == 1) {
                    taskMarkdown2.style.display = "block";
                    taskText2.textContent = totalOutput;
                    currentTaskText = taskText2;
                    currentTaskMarkdown = taskMarkdown2;
                } else if (i == 2) {
                    taskMarkdown3.style.display = "block";
                    taskText3.textContent = totalOutput;
                    currentTaskText = taskText3;
                    currentTaskMarkdown = taskMarkdown3;
                } else if (i == 3) {
                    taskMarkdown4.style.display = "block";
                    taskText4.textContent = totalOutput;
                    currentTaskText = taskText4;
                    currentTaskMarkdown = taskMarkdown4;
                } else if (i == 4) {
                    taskMarkdown5.style.display = "block";
                    taskText5.textContent = totalOutput;
                    currentTaskText = taskText5;
                    currentTaskMarkdown = taskMarkdown5;
                }
                
                // Scroll to the bottom of the current taskMarkdown element
                if (currentTaskMarkdown) {
                    currentTaskMarkdown.scrollTop = currentTaskMarkdown.scrollHeight;
                }
            }
            currentTaskMarkdown.classList.add("closeMarkdown")
            console.log(totalOutput);
            learningPath["tasks"][task].instructions = totalOutput;
            }
        }
        createText.textContent = ""
    session.destroy()
    learningPathButtonStart.style.display = "flex"
    localStorage.setItem("learningPath", JSON.stringify(learningPath));
}
