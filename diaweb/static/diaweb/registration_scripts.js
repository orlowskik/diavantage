$(document).ready(function () {

    document.getElementById('div_id_registration_patient').hidden = true;
    document.getElementById('div_id_registration_physician').hidden = true;

    document.getElementById('registration_sender').addEventListener('click', function() {
        document.getElementById('div_id_registration_patient').hidden = false;
        document.getElementById('div_id_registration_physician').hidden = false;
    })
})





