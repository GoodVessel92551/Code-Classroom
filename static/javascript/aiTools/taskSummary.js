let masterData = {}
const aiText = document.getElementById("aiText");
let taskNumCount = 0
const taskSummaryContainerTaskList = document.getElementById("taskSummaryContainerTaskList");
const aiMarkdown = document.getElementById("aiMarkdown");
const taskSummaryText = document.getElementById("taskSummaryText");

let classRole = "student";
Object.keys(usersClasses).forEach(key => {
    usersClasses[key].members.forEach(member => {
        if (member.id == userID) {
            if (member.role == "teacher") {
                classRole = "teacher";
            } else {
                classRole = "student";
            }
        }
    })
    if (classRole == "teacher") {
        return
    }
    Object.keys(usersClasses[key].tasks).forEach(task => {
        let taskInfo = usersClasses[key].tasks[task];
        let taskInfoSimple = taskInfo
        let studentData = taskInfoSimple.student_data[Object.keys(taskInfo.student_data)[0]];
        console.log(studentData)
        if (studentData == undefined) {
            taskInfoSimple.status = "Not Started";
        } else {
            taskInfoSimple.feedback = studentData.feedback;
            taskInfoSimple.taskStatus = studentData.status;
        }
        delete taskInfoSimple.student_data;
        delete taskInfoSimple.taskPoints;
        delete taskInfoSimple.taskDescription;
        delete taskInfoSimple.taskId;
        masterData[taskNumCount] = taskInfoSimple;
        taskNumCount++;
    })
});

var available_ai = false;
document.addEventListener("DOMContentLoaded", async () => {
    try {
        var capabilities = await ai.languageModel.availability();
    } catch {
        console.error("No AI")
        taskSummaryText.textContent = "AI Unavailable"
        return
    }
    if (capabilities.available == "no" || capabilities.available == "after-download") console.error("No AI")
    taskSummaryText.textContent = "Loading AI"
    available_ai = true;
    session = await ai.languageModel.create({
        systemPrompt: "You will be given a JSON dictionary containing a list of tasks that a student has due. Your job is to generate a concise, one-short-paragraph summary of these tasks for the student, using direct language with words like 'you.' Avoid bullet points and keep the summary brief while still conveying key details. If feedback is provided, make sure to incorporate it naturally into the summary.Check the status for the task to see if it has been completed. The current date is:" + new Date().toISOString().split('T')[0],
    });
    taskSummaryText.textContent = "AI Loaded"
    create_result()
})


const create_result = async () => {
    console.log(available_ai);
    if (available_ai) {
        console.log("Generating result");
        taskSummaryText.textContent = "Creating Summary"
        var totalOutput = "";

        // Add animated gradient class when generation starts
        taskSummaryContainerTaskList.classList.add('animated-gradient');

        const stream = await session.promptStreaming("Json Data:" + JSON.stringify(masterData, null, 2));
        for await (const chunk of stream) {
            aiMarkdown.style.display = "block";
            console.log(chunk);
            totalOutput += chunk;
            aiText.textContent = totalOutput;
        }

        // Remove animated gradient class when generation completes
        taskSummaryContainerTaskList.classList.remove('animated-gradient');
        taskSummaryText.textContent = "Summary Created"
    }
}
