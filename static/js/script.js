// JQuery Phone number mask
$('[name="phone_number"]').mask('+00000000000', {placeholder: '+7__________'});

// Chosen Autocomplete specialty option
$('#id_specialty').chosen();
$('#id_current_specialty').chosen();
$('#id_specialty_on_previous_university').chosen();

// Проверка основы обучения
const selectedOption = $("#id_foundation option:selected").val();
const checkbox = $("#id_with_grant_preservation");
if (selectedOption === "на платной основе") {
    checkbox.prop('checked', false);
    checkbox.prop('disabled', true);
}

// При изменении dropdown меню
$(document).ready(function () {
    $("#id_foundation").change(function () {
        const selectedOption = $(this).children("option:selected").val();
        if (selectedOption === "на платной основе") {
            checkbox.prop('checked', false);
            checkbox.prop('disabled', true);
        }
        if (selectedOption === "на основе образовательного гранта") {
            checkbox.prop('disabled', false);
        }
    });
});

