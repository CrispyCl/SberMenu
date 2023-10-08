const dropContainer = document.getElementById("dropcontainer")
const fileInput = document.getElementById("images")

dropContainer.addEventListener("dragover", (e) => {
    // prevent default to allow drop
    e.preventDefault()
}, false)

dropContainer.addEventListener("dragenter", () => {
    dropContainer.classList.add("drag-active")
})

dropContainer.addEventListener("dragleave", () => {
    dropContainer.classList.remove("drag-active")
})

dropContainer.addEventListener("drop", (e) => {
    e.preventDefault()
    dropContainer.classList.remove("drag-active")
    fileInput.files = e.dataTransfer.files
})



const fileChosen = document.getElementById('file-chosen');

fileInput.addEventListener('change', function () {
    fileChosen.textContent = this.files[0].name
})



// show img
const droptitle = document.querySelector('.drop-title');

function readURL(input) {
    if (input.files && input.files[0]) {
        var reader = new FileReader();

        reader.onload = function (e) {
            $('#show_img')
                .attr('src', e.target.result)
                .width(150)
                .height(200);
        };
        fileChosen.classList.add('black');
        droptitle.classList.add('black');
        reader.readAsDataURL(input.files[0]);
    }
}