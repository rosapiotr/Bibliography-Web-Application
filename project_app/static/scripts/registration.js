document.addEventListener('DOMContentLoaded', function (event) {

    const GET = "GET";
    const POST = "POST";

    let registrationForm = document.getElementById("registration-form");
    let loginInput = document.getElementById("login");
    let passwordInput = document.getElementById("password");
    let passwordRepeatInput = document.getElementById("repeat-password");
    let firstNameInput = document.getElementById("firstname");
    let lastNameInput = document.getElementById("lastname");

    loginInput.addEventListener("change", checkLoginAvailability);
    passwordInput.addEventListener("change", checkPassword);
    passwordRepeatInput.addEventListener("change", checkRepeatPassword);
    firstNameInput.addEventListener("change", checkFirstName);
    lastNameInput.addEventListener("change", checkLastName);

    registrationForm.addEventListener("submit", function (event) {
        valid = true;
        var n = event.srcElement.length;
        appendix = "_l";
        p_appendix = "_p";

        for (var i = 0; i < n; i++) {
            let id_name = event.srcElement[i].id.concat(appendix);
            let p_id = id_name.concat(p_appendix);
            if (event.srcElement[i].value == "") {
                valid = false;
                event.srcElement[i].classList.add("error_class");
                if (document.getElementById(p_id) == null) {
                    var p = document.createElement("P");
                    var textnode = document.createTextNode("Pole nie może być puste!");
                    p.classList.add("error_message");
                    p.id = p_id;
                    p.appendChild(textnode);
                    field = document.getElementById(id_name);
                    registrationForm.insertBefore(p, field);
                }
            } else if (event.srcElement[i].classList.contains("error_class")) {
                valid = false;
            } else {
                if (document.getElementById(p_id) != null) {
                    document.getElementById(event.srcElement[i].id).classList.remove("error_class");
                    registrationForm.removeChild(document.getElementById(p_id));
                }
            }
        }
        if (!valid) {
            event.preventDefault();
        }
    });

    function checkLoginAvailability() {
        loginInput = document.getElementById("login")
        let baseUrl = "https://localhost:8080/api/user/";
        let userUrl = baseUrl + loginInput.value;
        let errorId = "login_error_mes";
        let errorClass = "error_class";

        if (loginInput.value != "") {
            Promise.resolve(fetch(userUrl, { method: GET }).then(function (resp) {
                if (document.getElementById("login_l_p") != null) {
                    registrationForm.removeChild(document.getElementById("login_l_p"));
                }
                if (resp.status == 200) {
                    loginInput.classList.add(errorClass);
                    if (document.getElementById(errorId) == null) {
                        addWarningMessage("Login zajęty", "login");
                    }
                } else if (resp.status == 404) {
                    removeAll("login", errorClass);
                }
                return resp.status;
            }).catch(function (err) {
                console.log(err);
                return resp.status;
            }));
        } else {
            removeAll("login", errorClass);
        }
    }

    function checkPassword() {
        let elementId = "password";
        let passwordText = document.getElementById(elementId).value;
        let errorId = "password_error_mes";
        let errorClass = "error_class";

        if (passwordText != "") {
            if (document.getElementById("password_l_p") != null) {
                registrationForm.removeChild(document.getElementById("password_l_p"));
            }
            if (passwordText.search(/[^a-zA-Z]/) != -1 || passwordText.length < 8) {
                passwordInput.classList.add(errorClass);
                if (document.getElementById(errorId) == null) {
                    addWarningMessage("Hasło musi składać się z liter i mieć długość conajmniej 8 znaków", elementId);
                }
            } else {
                removeAll(elementId, errorClass);
            }
        } else {
            removeAll(elementId, errorClass);
        }
    }

    function checkRepeatPassword() {
        let elementId = "repeat-password";
        let passwordRepeatText = document.getElementById(elementId).value;
        let errorId = "repeat-password_error_mes";
        let errorClass = "error_class";

        if (passwordRepeatText != "") {
            if (document.getElementById("repeat-password_l_p") != null) {
                registrationForm.removeChild(document.getElementById("repeat-password_l_p"));
            }
            if (passwordRepeatText != document.getElementById("password").value) {
                passwordRepeatInput.classList.add(errorClass);
                if (document.getElementById(errorId) == null) {
                    addWarningMessage("Hasła muszą być takie same", elementId);
                }
            } else {
                removeAll(elementId, errorClass);
            }
        } else {
            removeAll(elementId, errorClass);
        }
    }

    function checkFirstName() {
        let elementId = "firstname";
        let firstNameText = document.getElementById(elementId).value;
        let errorId = "firstname_error_mes";
        let errorClass = "error_class";

        if (firstNameText != "") {
            if (document.getElementById("firstname_l_p") != null) {
                registrationForm.removeChild(document.getElementById("firstname_l_p"));
            }
            if (firstNameText.charAt(0).search(/[A-Z]/) != 0 || firstNameText.substr(1).search(/[A-Z]/) != -1) {
                firstNameInput.classList.add(errorClass);
                if (document.getElementById(errorId) == null) {
                    addWarningMessage("Imię musi zaczynać sie od wielkiej litery", elementId);
                }
            } else {
                removeAll(elementId, errorClass);
            }
        } else {
            removeAll(elementId, errorClass);
        }
    }

    function checkLastName() {
        let elementId = "lastname";
        let lastNameText = document.getElementById(elementId).value;
        let errorId = "lastname_error_mes";
        let errorClass = "error_class";

        if (lastNameText != "") {
            if (document.getElementById("lastname_l_p") != null) {
                registrationForm.removeChild(document.getElementById("lastname_l_p"));
            }
            if (lastNameText.charAt(0).search(/[A-Z]/) != 0 || lastNameText.substr(1).search(/[A-Z]/) != -1) {
                lastNameInput.classList.add(errorClass);
                if (document.getElementById(errorId) == null) {
                    addWarningMessage("Nazwisko musi zaczynać sie od wielkiej litery", elementId);
                }
            } else {
                removeAll(elementId, errorClass);
            }
        } else {
            removeAll(elementId, errorClass);
        }
    }

    function removeAll(elementId, errorClass) {
        document.getElementById(elementId).classList.remove(errorClass);
        errorId = elementId.concat("_error_mes")
        if (document.getElementById(errorId) != null) {
            registrationForm.removeChild(document.getElementById(errorId));
        }
    }

    function addWarningMessage(message, elementName) {
        var para = document.createElement("P");
        para.classList.add("error_message");
        para.id = elementName.concat("_error_mes");
        var textnode = document.createTextNode(message);
        para.appendChild(textnode);
        element_l = document.getElementById(elementName.concat("_l"));
        registrationForm.insertBefore(para, element_l);
    }

});
