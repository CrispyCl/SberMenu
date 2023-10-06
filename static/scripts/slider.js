const slider = document.querySelector('.top_container'),
    firstImg = document.querySelectorAll('.it')[0],
    arrowIcons = document.querySelectorAll('.wrapper i');

let isMoveStart = false, prevPageX, prevScrollLeft;



const ShowHideIcon = () => {
    let scrollWidth = slider.scrollWidth - slider.clientWidth;
    arrowIcons[0].style.display = slider.scrollLeft == 0 ? 'none' : 'block';
    arrowIcons[1].style.display = slider.scrollLeft == scrollWidth ? 'none' : 'block';
}

arrowIcons.forEach(icon => {
    icon.addEventListener('click', () => {
        let firstImgWidth = firstImg.clientWidth
        slider.scrollLeft += icon.id == "left" ? -firstImgWidth : firstImgWidth;
        setTimeout(() => ShowHideIcon(), 60);
    })
});

const moveStart = (e) => {
    isMoveStart = true;
    prevPageX = e.pageX;
    prevScrollLeft = slider.scrollLeft;
}


const move = (e) => {
    if (!isMoveStart) return;
    e.preventDefault();
    slider.classList.add('move');
    let positionDiff = e.pageX - prevPageX;
    slider.scrollLeft = prevScrollLeft - positionDiff
    ShowHideIcon();
}

const moveStop = () => {
    isMoveStart = false;
    slider.classList.remove('move');

}

slider.addEventListener('mousedown', moveStart)
slider.addEventListener('mousemove', move)
slider.addEventListener('mouseup', moveStop)
slider.addEventListener('mouseleave', moveStop)