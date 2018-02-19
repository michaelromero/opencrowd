function generate_boundingbox(BoundingBox, opencrowd_id){
    var boundingbox_html = "";
    boundingbox_html += ('<div id="' + opencrowd_id + '"');
    boundingbox_html += (' class="arch_groups row bounding_box animated fadeInUp">');
    boundingbox_html += (' <img id="img_' + opencrowd_id + '" src="' + BoundingBox.url + '"/>');
    boundingbox_html += ('</div>');
    return boundingbox_html;
}

function generate_bounding_box(id) {
    $('#img_' + id).Jcrop({
        multi: 'true',
        canDrag: 'true',
        linked: 'true',
        minSize: [18, 18],
        bgOpacity: 0.6,
        boxWidth: 1000,
        boxHeight: 1000
    }, function () {
        coordinates[id] = {};
        var numSelections = 0;
        jcrop_apis[id] = this;
        var container = jcrop_apis[id].container;
//        $('.selection_counter').text(numSelections);

        // event, selection, coords
        container.on('cropcreate', function (e, s, c) {
            s.myNumber = numSelections++;
            coordinates[id][s.myNumber] = c;
//            $('.selection_counter').text(numSelections);

        });
        //c no longer exists on crop remove
        container.on('cropremove', function (e, s, c) {
            delete coordinates[id][s.myNumber];
//            $('.selection_counter').text(numSelections);
        });

        container.on('cropstart', function (e, s, c) {
            coordinates[id][s.myNumber] = c;
        });
        container.on('cropmove', function (e, s, c) {
            coordinates[id][s.myNumber] = c;
        });
        container.on('cropend', function (e, s, c) {
            coordinates[id][s.myNumber] = c;
        });

//        $('#unhook').click(function (e) {
//            jcrop_api.destroy();
//            coordinates = [];
//            numSelections = 0;
//            $('.selection_counter').text(numSelections + " bounding boxes have been drawn");
//            reset();
//            return false;
//        });
    });
}


function saveBoundingBox(current_answer){
    //dirty check for bounding box type
    var sections = data[i];
    //cleanse
    for(var key in sections){
        if(sections.hasOwnProperty(key, sections[key])){
            if(sections[key].type=="BoundingBox"){
                //save
                if(key in coordinates){
                    if('undefined' in coordinates[key]){
                        delete coordinates[key]['undefined'];
                    }
                }
                current_answer[key] = coordinates[key];
            }
        }
    }

//    for(var idx = 0; idx < sections.length; idx++) {
//        var type = sections[idx]['type'];
//        console.log("type:")
//        console.log(type)
//        if(type == 'BoundingBox'){
//            for(var bounding_box_object in coordinates){
//                if(!(isEmptyObject(coordinates[bounding_box_object]))){
//                    if (!('BoundingBox' in current_answer)) {
//                        current_answer['BoundingBox'] = {}
//                    }
//                    if('undefined' in coordinates[bounding_box_object]){
//                        delete coordinates[bounding_box_object]['undefined'];
//                    }
//                    console.log("saving")
//                    current_answer['BoundingBox'][bounding_box_object] = coordinates[bounding_box_object];
//                }
//            }
//        }
//    }
}

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