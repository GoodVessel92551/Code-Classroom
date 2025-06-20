let classesContainer = document.getElementById("classesContainer");
const template = document.getElementById("classroomTemplate");
const noClasses = document.getElementById("noClasses");
let classesNum = 0;

Object.keys(classes).forEach(key => {
    classesNum++;
    let classInfo = classes[key].classInfo;


    const clone = template.content.cloneNode(true);

    
    const link = clone.querySelector("a");

    link.addEventListener("click", function() {
        link.classList.add("openClassroom");
    });
    
        

    const img = clone.querySelector("img");
    const title = clone.querySelector("h3");
    const description = clone.querySelector("p");


    img.src = "/static/coverImages/classroomCovers/" + classInfo.coverImage + "Gradient.webp";
    title.textContent = classInfo.name;
    description.textContent = classInfo.description;
    link.href = "/classroom/" + key;

    classesContainer.prepend(clone);
});

console.log(classesNum);

if (classesNum == 0) {
    noClasses.style.display = "flex";
}