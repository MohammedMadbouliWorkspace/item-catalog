const imagePreviewer = document.getElementById("imagePreviewer"),
    imageLoaderButton = document.getElementById("imageLoaderButton");

function shortFileName(str, length) {
    var strArr = str.split("."),
        extension = strArr[strArr.length - 1];

    if(str.length > length) {
        return str.slice(0, length - (extension.length + 4)) + "…" + str.slice(str.length - (extension.length + 4), str.length - (extension.length + 1)) + "." + extension
    }
    return str
}

function readURL(loader){
    if(loader.files && loader.files[0]) {
        let reader = new FileReader();
        reader.onload = function(e) {
            imageLoaderButton.style.cssText = `--file-name: '${shortFileName(loader.files[0].name, 15)}';`;
            imagePreviewer.style.cssText = `--image: url('${e.target.result}'); --placeholder-text: unset`;
        };
        reader.readAsDataURL(loader.files[0])
    }
}