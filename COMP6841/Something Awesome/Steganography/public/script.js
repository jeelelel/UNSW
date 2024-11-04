var swiper = new Swiper('.blog-slider', {
    spaceBetween: 30,
    effect: 'fade',
    loop: true,
    mousewheel: {
        invert: false,
    },
    pagination: {
        el: '.blog-slider__pagination',
        clickable: true,
    }
});

var isAdvancedUpload = function() {
    var div = document.createElement('div');
    return (('draggable' in div) || ('ondragstart' in div && 'ondrop' in div)) && 'FormData' in window && 'FileReader' in window;
}();

var $form = $('.box');
var $input = $form.find('input[type="file"]');
var $label = $form.find('label');
var $errorMsg = $('<div class="box__error"></div>').hide().appendTo($form);
var $restartBtn = $('<button type="button" class="box__restart">Restart</button>').hide().appendTo($form);
var droppedFiles = false;

if (isAdvancedUpload) {
    $form.addClass('has-advanced-upload');

    $form.on('drag dragstart dragend dragover dragenter dragleave drop', function(e) {
        e.preventDefault();
        e.stopPropagation();
    })
    .on('dragover dragenter', function() {
        $form.addClass('is-dragover');
    })
    .on('dragleave dragend drop', function() {
        $form.removeClass('is-dragover');
    })
    .on('drop', function(e) {
        droppedFiles = e.originalEvent.dataTransfer.files;
        handleFiles(droppedFiles);
    });

    $input.on('change', function(e) {
        handleFiles(this.files);
    });

    $restartBtn.on('click', function() {
        restartUpload();
    });

    $form.on('submit', function(e) {
        if ($form.hasClass('is-uploading')) return false;

        $form.addClass('is-uploading').removeClass('is-error');

        if (isAdvancedUpload) {
            e.preventDefault();
            var ajaxData = new FormData($form.get(0));
            if (droppedFiles) {
                $.each(droppedFiles, function(i, file) {
                    ajaxData.append($input.attr('name'), file);
                });
            }
            uploadFiles(ajaxData);
        }
    });
}

function handleFiles(files) {
    var validFiles = validateFiles(files);
    if (validFiles.length > 0) {
        showPreview(validFiles);
        $form.addClass('is-ready');
    } else {
        showError('No valid files were selected.');
    }
}

function validateFiles(files) {
    var validFiles = [];
    var maxFileSize = 5 * 1024 * 1024; // 5MB
    var allowedTypes = ['image/jpeg', 'image/png', 'application/pdf'];

    for (var i = 0; i < files.length; i++) {
        var file = files[i];
        if (file.size <= maxFileSize && allowedTypes.includes(file.type)) {
            validFiles.push(file);
        } else {
            showError('File ' + file.name + ' is either too large or not an allowed type.');
        }
    }
    return validFiles;
}

function showPreview(files) {
    $label.text(files.length > 1 ? (files.length + ' files selected') : files[0].name);
    // You can add more detailed preview here, like thumbnails for images
}

function uploadFiles(formData) {
    $.ajax({
        url: $form.attr('action'),
        type: 'POST',
        data: formData,
        dataType: 'json',
        cache: false,
        contentType: false,
        processData: false,
        complete: function() {
            $form.removeClass('is-uploading');
        },
        success: function(data) {
            $form.addClass(data.success ? 'is-success' : 'is-error');
            if (!data.success) showError(data.error);
        },
        error: function() {
            showError('An error occurred during upload. Please try again.');
        }
    });
}

function showError(error) {
    $errorMsg.text(error).show();
    $form.addClass('is-error');
    $restartBtn.show();
}

function restartUpload() {
    $form.removeClass('is-error is-success is-ready');
    $input.val('');
    $label.text('Choose a file or drag it here');
    $errorMsg.hide();
    $restartBtn.hide();
    droppedFiles = false;
}

