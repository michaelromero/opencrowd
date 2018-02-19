function generate_image(Image, opencrowd_id){
    var column_size;
    if(Image.urls.length == 1){
        column_size = 12
    }
    else if(Image.urls.length == 2){
        column_size = 6
    }
    else if(Image.urls.length == 3){
        column_size = 4
    }
    else if(Image.urls.length == 6){
        column_size = 2
    }
    else{
        column_size = 3
    }
    var image_html = "";
    image_html += ('<div id="' + opencrowd_id + '"');
//    image_html += ('style="padding-left: 0; padding-right: 0;min-height:100%"');
        image_html += ('style="padding-left: 0; padding-right: 0; min-height:100%;"');

    image_html += ('class="row arch_groups animated fadeInUp">');
    for(var url in Image.urls){
        image_html += ('<div class="col-md-' + column_size +' center-block"><a class="thumbnail">');
        image_html += ('<img id="' + opencrowd_id + '_' + url + '" style="max-height: 400px; width: auto;" class="image-responsive" src="' + Image.urls[url] + '"/></a>');
        image_html += ('</div>')
    }
    image_html += ('</div>');
    return image_html;
}
