var nameLabel = document.getElementById("nameLabel"),
    nameHolder = document.getElementById("nameHolder"),
    nameEditButton = document.getElementById("nameEditButton");

function deleteElement(element){var output = element; element.remove();return output}

nameEditButton.addEventListener("click", ()=>{
    var nameText = nameHolder.textContent,
        nameText = nameHolder.textContent,
        nameEditField = `<span id="nameEditField" class="edit_field"><input type="text" value="Name"><span id="nameApplyEditButton" class="edit_icon"><i class="fas fa-check"></i></span><span id="nameCancelEditButton" class="edit_icon"><i class="fas fa-times"></i></span></span>`;

    nameHolder = deleteElement(nameHolder);

    nameEditButton.style.display = "none";

    nameLabel.insertAdjacentHTML("afterbegin", nameEditField);

    var nameEditField = document.getElementById("nameEditField"),
        nameApplyEditButton = document.getElementById("nameApplyEditButton"),
        nameCancelEditButton = document.getElementById("nameCancelEditButton");

    nameCancelEditButton.addEventListener("click", ()=>{
        nameLabel.insertAdjacentElement("afterbegin", nameHolder);
        nameEditField.remove()
        nameEditButton.style.display = "unset";
    })

})