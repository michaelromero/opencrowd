function generate_CollapsePanel(CollapsePanel, opencrowd_id){
    var CollapsePanel_html = "\
    <div id=\"" + opencrowd_id + "\"class=\"panel-group\">\
        <div class=\"panel panel-default\">\
            <div class=\"panel-heading\">\
                <h4 class=\"panel-title\">\
                <a data-toggle=\"collapse\" href=\"#collapse1\">" + CollapsePanel.title+ "</a>\
                </h4>\
            </div>\
            <div id=\"collapse1\" class=\"panel-collapse collapse\">\
                <div class=\"panel-body\">" + CollapsePanel.body + "</div>\
                <div class=\"panel-footer\">" + CollapsePanel.footer + "</div>\
            </div>\
        </div>\
    </div>";
    return CollapsePanel_html;
}