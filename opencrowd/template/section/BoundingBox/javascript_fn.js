
function killBoundingBoxes(i){
    var sections = data[i];
    for(var idx = 0; idx < sections.length; idx++) {
        var type = sections[idx]['type'];
        if(type == 'bounding_box'){
                for (var id in jcrop_apis) {
                    jcrop_apis[id].destroy();
                }
                break;
        }
    }
}
