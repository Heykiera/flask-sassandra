
function previewImage() {
    var preview = document.querySelector('#chosen_image');
    var file = document.querySelector('#file').files[0];
    var reader = new FileReader();

    reader.addEventListener('load', function () {
        preview.src = reader.result;
    }, false);

    if (file) {
        reader.readAsDataURL(file);
    }
}
