function generate_inputgroup(InputGroup, opencrowd_id){

    var column_size = 6;
    if (InputGroup.options.length >= 6){
      column_size = 4;
    }
    if (InputGroup.options.length >= 12){
      column_size = 3;
    }
    
    var inputgroup_html = "";

    inputgroup_html += ('<div id="' + opencrowd_id + '"');
    inputgroup_html += (' class="arch_groups row animated fadeInUp">');
    for(var option_index in InputGroup.options){
        var option_key = InputGroup.options[option_index];
        var option = data[i][option_key];

      inputgroup_html += ('<div class="col-md-' + column_size + '">');
      inputgroup_html += ('<label class="btn btn-default" ');
      inputgroup_html += ('data-toggle="tooltip" data-placement="right" title="' + option.on_hover + '">');
      inputgroup_html += ('<input type="' + InputGroup.input_type  + '"');

      inputgroup_html += (' id="' + option_key + '" name="' + opencrowd_id  + '"');
      if(option.children){
          inputgroup_html += (' data-children=\'[')
          for(var child_idx = 0; child_idx < option.children.length; child_idx++){
              var child = option.children[child_idx];
              inputgroup_html += ('"' + child + '"');
              if(child_idx < option.children.length - 1){
                  inputgroup_html += ',';
              }
          }
          inputgroup_html += (']\'')
      }
//      if(option.children.length){
//        inputgroup_html += (' onclick=\'showDiv(this, $(this).data("children"),"' + opencrowd_id +'")\'')
//      }
      inputgroup_html += (' value="' + option.value  + '"> ')
      inputgroup_html += (option.text)
      inputgroup_html += ('</label></div>')
    }
    inputgroup_html += ('</div>');
    return inputgroup_html;
}
