let classesContainer = document.getElementById("classesContainer");

console.log(classes);
classes.forEach(usersClass => {
    let classInfo = usersClass.classInfo;
    let classContainer = document.createElement("a");
    let classImage = document.createElement("img");
    let textContainer = document.createElement("div");
    let textContainerSpan = document.createElement("span");
    let classTitle = document.createElement("h3");
    let classDescription = document.createElement("p");
    classImage.src = "/static/coverImages/classroomCovers/" + classInfo.coverImage + "Gradient.png";
    classTitle.textContent = classInfo.name
    classDescription.textContent = classInfo.description
    textContainer.classList.add("textContainer");
    textContainerSpan.appendChild(classTitle);
    textContainerSpan.appendChild(classDescription);
    textContainer.appendChild(textContainerSpan);
    classContainer.appendChild(classImage);
    classContainer.appendChild(textContainer);
    classesContainer.prepend(classContainer);
});
