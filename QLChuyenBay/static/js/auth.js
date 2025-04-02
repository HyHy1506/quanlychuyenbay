function checkPasswordStrength(password) {
  const strongPasswordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;
  return strongPasswordRegex.test(password);
}
function typePasswordCheck(password){
    let passwordCheck = document.getElementById('invalid-password')
    console.info(123)
    if(checkPasswordStrength(password)){

        passwordCheck.innerText= "Valid"
    }else{
        passwordCheck.innerText= "Mật khẩu chưa đủ mạnh"
    }
}
