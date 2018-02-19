function generate_textbox(TextBox, opencrowd_id){
    var textbox_html = "";
    textbox_html += ('<div id="' + opencrowd_id + '"');
    textbox_html += (' class="arch_groups row animated fadeInUp bs-callout bs-callout-' + TextBox.callout_type + '">');
    if(TextBox.main_title){
        textbox_html += ('<h4>' + TextBox.main_title + '</h4>');
    }
    for(var idx = 0; idx < TextBox.text.length; idx++){
        textbox_html += ('<p>' + TextBox.text[idx] + '</p>');
    }
    textbox_html += ('</div>');
    return textbox_html;
}
