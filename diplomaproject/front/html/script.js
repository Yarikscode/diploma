$(document).ready(function() {
    var dropZone = $('#upload-container');

    $('#file-input').focus(function() {
        $('label').addClass('focus');
    }).focusout(function() {
        $('label').removeClass('focus');
    });

    dropZone.on('drag dragstart dragend dragover dragenter dragleave drop', function() {
        return false;
    });

    dropZone.on('dragover dragenter', function() {
        dropZone.addClass('dragover');
    });

    dropZone.on('dragleave', function(e) {
        let dx = e.pageX - dropZone.offset().left;
        let dy = e.pageY - dropZone.offset().top;
        if ((dx < 0) || (dx > dropZone.width()) || (dy < 0) || (dy > dropZone.height())) {
            dropZone.removeClass('dragover');
        }
    });

    dropZone.on('drop', function(e) {
        dropZone.removeClass('dragover');
        let file = e.originalEvent.dataTransfer.files[0]; 
        sendFile(file);
    });

    $('#file-input').change(function() {
        let file = this.files[0]; 
        sendFile(file);
    });

    function sendFile(file) {
        if (!file) {
            alert("Файл не выбран!");
            return;
        }

        let allowedExtensions = ["xml", "xlsx"];
        let fileExtension = file.name.split('.').pop().toLowerCase();

        if (!allowedExtensions.includes(fileExtension)) {
            alert(`Файл "${file.name}" имеет недопустимый формат!`);
            return;
        }

        let Data = new FormData();
        Data.append('file', file);

        $.ajax({
            url: dropZone.attr('action'),
            type: dropZone.attr('method'),
            data: Data,
            contentType: false,
            processData: false,
            success: function(response) {
				if (response.download_url) {
					let timestamp = new Date().getTime(); // Генерируем timestamp
    				window.location.href = response.download_url + "&_nocache=" + timestamp
				} else {
					alert("Ошибка: сервер не вернул URL скачивания.");
				}
			},			
            error: function() {
                alert('Ошибка при загрузке файла.');
            }
        });
    }
});
