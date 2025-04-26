window.onload = function() {
    var pattern_curp = /^[A-Z]{4}\d{6}[HM]{1}[A-Z]{2}[B-DF-HJ-NP-TV-Z]{3}[A-Z\d]{1}\d{1}$/;
    var pattern_nombre = /^[A-Za-zÁÉÍÓÚáéíóúüÜñÑ\s]+$/;
    var pattern_telefono = /^[0-9]{10}$/;
    var pattern_celular = /^[0-9]{10}$/;
    var pattern_email = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$/;

    function ValidaCrear() {
        let curp = document.getElementById('curp').value.trim();
        let nombre = document.getElementById('nombre').value.trim();
        let paterno = document.getElementById('paterno').value.trim();
        let materno = document.getElementById('materno').value.trim();
        let telefono = document.getElementById('telefono').value.trim();
        let celular = document.getElementById('celular').value.trim();
        let correo = document.getElementById('correo').value.trim();
        let nivel = document.getElementById('nivel').value;
        let municipio = document.getElementById('municipio').value;
        let asunto = document.getElementById('id_asunto').value;

        // Validaciones normales
        if (curp.length == 0) {
            Swal.fire('Error', 'Debes ingresar la CURP.', 'error');
            return false;
        }
        if (!pattern_curp.test(curp)) {
            Swal.fire('Error', 'La CURP ingresada no es válida.', 'error');
            return false;
        }
        if (nombre.length == 0) {
            Swal.fire('Error', 'Debes ingresar el Nombre.', 'error');
            return false;
        }
        if (!pattern_nombre.test(nombre)) {
            Swal.fire('Error', 'El Nombre ingresado no es válido.', 'error');
            return false;
        }
        if (paterno.length == 0) {
            Swal.fire('Error', 'Debes ingresar el Apellido Paterno.', 'error');
            return false;
        }
        if (!pattern_nombre.test(paterno)) {
            Swal.fire('Error', 'El Apellido Paterno ingresado no es válido.', 'error');
            return false;
        }
        if (materno.length == 0) {
            Swal.fire('Error', 'Debes ingresar el Apellido Materno.', 'error');
            return false;
        }
        if (!pattern_nombre.test(materno)) {
            Swal.fire('Error', 'El Apellido Materno ingresado no es válido.', 'error');
            return false;
        }
        if (telefono.length == 0 || !pattern_telefono.test(telefono)) {
            Swal.fire('Error', 'Debes ingresar un Teléfono válido de 10 dígitos.', 'error');
            return false;
        }
        if (celular.length == 0 || !pattern_celular.test(celular)) {
            Swal.fire('Error', 'Debes ingresar un Celular válido de 10 dígitos.', 'error');
            return false;
        }
        if (correo.length == 0 || !pattern_email.test(correo)) {
            Swal.fire('Error', 'Debes ingresar un Correo válido.', 'error');
            return false;
        }
        if (nivel == "0") {
            Swal.fire('Error', 'Debes seleccionar un Nivel.', 'error');
            return false;
        }
        if (municipio == "0") {
            Swal.fire('Error', 'Debes seleccionar un Municipio.', 'error');
            return false;
        }
        if (asunto == "0") {
            Swal.fire('Error', 'Debes seleccionar un Asunto.', 'error');
            return false;
        }

        // 🎉 Si pasó todas las validaciones, mostramos el SweetAlert de éxito
        Swal.fire({
            icon: 'success',
            title: '¡Registro exitoso!',
            text: 'La solicitud se registró correctamente.',
            confirmButtonText: 'Aceptar'
        }).then(() => {
            document.forms['registro'].submit(); // Envía el formulario manualmente
        });

        return false; // Muy importante: cancelamos el submit normal
    }

    window.ValidaCrear = ValidaCrear;
};
