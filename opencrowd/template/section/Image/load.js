if (type == 'image') {
    for (var image_idx = 0; image_idx < section['urls'].length; image_idx++) {
        $("#" + id + "_" + image_idx).attr('src', section['urls'][image_idx]);
    }
    if (!(section.hidden)) {
        $("#div_" + id).show();
    }

}