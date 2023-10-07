const ddw = document.querySelector('.dd-menu-wrap');
const basket = document.querySelector('.basket');

basket.addEventListener('click', () => {
    if (ddw.classList.contains('show')) {
        ddw.classList.remove('show');
    } else {
        ddw.classList.add('show');
    };
})

console.log('akjshd')
