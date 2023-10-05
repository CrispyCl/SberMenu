const container = document.querySelector('.white_container')
const RegistrationButton = document.querySelector('.RegisterNewAccount')
const LoginButton = document.querySelector('.Login')


RegistrationButton.addEventListener('click', () => {
    container.classList.add('Active');
})

LoginButton.addEventListener('click', () => {
    container.classList.remove('Active');
})