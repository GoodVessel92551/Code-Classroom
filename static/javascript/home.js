let classesContainer = document.getElementById("classesContainer");
const template = document.getElementById("classroomTemplate");

console.log(classes);

Object.keys(classes).forEach(key => {
    let classInfo = classes[key].classInfo;
    

    const clone = template.content.cloneNode(true);
    

    const link = clone.querySelector("a");
    const img = clone.querySelector("img");
    const title = clone.querySelector("h3");
    const description = clone.querySelector("p");
    

    link.href = "/classroom/" + key;
    img.src = "/static/coverImages/classroomCovers/" + classInfo.coverImage + "Gradient.png";
    title.textContent = classInfo.name;
    description.textContent = classInfo.description;
    

    classesContainer.prepend(clone);
});