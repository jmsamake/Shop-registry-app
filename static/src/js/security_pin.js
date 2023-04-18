//Security pin hide and show function
function myFunction() {
  var securityPin = document.getElementById("password");
  if (securityPin.type === "password") {
    securityPin.type = "text";
  } else {
    securityPin.type = "password";
  }
}