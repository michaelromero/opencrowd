var data = {{ HIT.generate_dags() }};
var i = 0;
var answers = [];
var coordinates = {};
var jcrop_apis = {};

$(document).ready(function () {
    init();

    $("#next-button").on("click", function () {
        document.getElementById("site-header").scrollIntoView();
        saveData(i);
        clear_html()
        killBoundingBoxes(i)
        i += 1;
        buttonRefresh(i);
        resetFormat();
        reorderDivs(i);
        loadQuestionFormat(i);
    });
    $("#back-button").on("click", function () {
        document.getElementById("site-header").scrollIntoView();
        //saveData();
        clear_html()
        killBoundingBoxes(i)
        i -= 1;
        buttonRefresh(i);
        resetFormat();
        reorderDivs(i);
        loadQuestionFormat(i);
    });
    $('#mturk_form').submit(function () {
        saveData(i);
        getAmazonData();
        return true;
    });

    // radio handlers
    $(document).on('click', 'input[type="radio"]', function () {
        // have to delete all the DAGs to prevent reclicking from generating more dags
        var children = $(this).data("children");
        for (var child_idx = 0; child_idx < children.length; child_idx++) {
            deleteDag(children[child_idx]);
        }


        // Processing only those that match the name attribute of the currently clicked button...
        $('input[name="' + $(this).attr('name') + '"]').not($(this)).trigger('deselect'); // Every member of the current radio group except the clicked one...
        var children = $(this).data("children");
        var parent_id = $(this).attr('name');
        for (var child_idx = 0; child_idx < children.length; child_idx++) {
            dynamicGenerateGraph(data[i], children[child_idx], parent_id)
        }
    });

    $(document).on('deselect', 'input[type="radio"]', function () {
        var id = $(this).attr('name');
        var children = $(this).data("children");
        for(var child_idx = 0; child_idx < children.length; child_idx++) {
                deleteDag(children[child_idx]);
            }

    })

    $(document).on('change', 'input[type="checkbox"]', function () {
        var check = $(this).prop("checked");
        var children = $(this).data("children");
        var button_id = $(this).attr('id');
        var parent_id = $(this).attr('name');
        if(check){
            for(var child_idx = 0; child_idx < children.length; child_idx++){
                dynamicGenerateGraph(data[i], children[child_idx], parent_id)
            }
        }
        else{
            for(var child_idx = 0; child_idx < children.length; child_idx++) {
                deleteDag(children[child_idx]);
            }
        }
    });
});

function deleteDag(button_id){
    var node = data[i][button_id];
    if(node.type == "BoundingBox"){
        delete coordinates[button_id]
    }
    if("children" in node) {
        for (var child_idx in node.children) {
            var child_id = node.children[child_idx];
            deleteDag(child_id);
        }
    }
    if("options" in node){
        for (var child_idx in node.options) {
            var child_id = node.options[child_idx];
            deleteDag(child_id);
        }

    }
    $("#"+button_id).remove();
//    if (button_id != 'anchor') {
//        $(this).remove();
//    }

}


function getAmazonData() {
    var answers_wrapper = {};
    var items = [];
    var para = window.location.search.substr(1).split("&");
    for (var j = 0; j < para.length; j++) {
        var key = para[j].split("=")[0];
        var val = para[j].split("=")[1];
        items[key] = val;
    }
    document.getElementById("assignmentId").value = items["assignmentId"];
    document.getElementById("hitId").value = items["hitId"];
    answers_wrapper["assignment"] = answers;
    if ($("#suggestion_text").val().length > 0) {
        answers_wrapper["suggestion"] = $("#suggestion_text").val();
    }
    //answers_wrapper["assignment_id"] = items["assignmentId"];
    //answers_wrapper["worker_id"] = items["workerId"];
    //answers_wrapper["hit_id"] = items["hitId"];
    document.getElementById("jsonObject").value = JSON.stringify(answers_wrapper);
}

function saveInputs(current_answer) {
    $(":input:checked").each(function () {
        $(this).prop('checked', false);
        var this_id = $(this).attr('name');
        if (!(this_id in current_answer)) {
            current_answer[this_id] = {}
        }
        if ($(this).is(':checkbox')) {
            if (!('checkbox' in current_answer[this_id])) {
                current_answer[this_id]['checkbox'] = []
            }
            current_answer[this_id]['checkbox'].push($(this).val())
        }
        if ($(this).is(':radio')) {
            current_answer[this_id]['radio'] = $(this).val()
        }
    });
}
function saveData(i) {
    var current_answer = {};
    {% set logics=[] %}
    {% for question in HIT.questions%}
    {% for section in question.sections %}
    {% if section.to_json().type not in logics %}
    {{ section.call_save_function() }}
    {% if logics.append(section.to_json().type) %}{% endif %}{# necessary jinja hack to modify a var inside inner loops (which are 'out of scope') #}
    {% endif %}
    {% endfor %}
    {% endfor %}
    coordinates = {};
    current_answer['question_id'] = data[i].question_id
    //end dirty check
    if ((isEmptyObject(current_answer))) {
        answers[i] = null;
    }
    else {
        answers[i] = current_answer;
    }
}

function buttonRefresh(i) {
    $("#submit-button").hide();
    $("#next-button").show();
    $("#back-button").hide();
    $("#suggestion_box").hide();
    if (i > 0) {
        $("#back-button").show();
    }
    if (data.length == 1 || i == data.length - 1) {
        $("#next-button").hide();
        $("#submit-button").show();
        $("#suggestion_box").show();
    }

}
function initializeTooltips() {
    $('[data-toggle="tooltip"]').tooltip(); //initializes the tooltips
    if ($("[data-toggle=tooltip]").length) {
        $("[data-toggle=tooltip]").tooltip();
    }

}
function resetFormat() {
    $(".arch_groups").hide();
}

function loadQuestionFormat(i) {
    $('.question_counter').text(data.length - i - 1 + " questions left");
}

function reorderDivs(i) {
    var dag = data[i];
    var root_id = dag.root;
    dynamicGenerateGraph(dag, root_id, "anchor")
}

function dynamicGenerateGraph(dag, root_id, anchor_id) {
    var node = dag[root_id];
    {% set logics=[] %}
    {% for question in HIT.questions%}
    {% for section in question.sections %}
    {% if section.to_json().type not in logics %}
    {{ section.dynamicGenerateGraphLogic() }}
    {% if logics.append(section.to_json().type) %}{% endif %}
    {% endif %}
    {% endfor %}
    {% endfor %}
    if (node.hidden) {
        $("#" + anchor_id).hide();
    }

    var prior_child_id = root_id;

    if (node.children) {
        for (var child_node_idx in node.children) {
            dynamicGenerateGraph(dag, node.children[child_node_idx], prior_child_id);
            prior_child_id = node.children[child_node_idx];

        }
    }
}

function output(inp) {
    document.body.appendChild(document.createElement('pre')).innerHTML = inp;
}

function syntaxHighlight(json) {
    json = json.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    return json.replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g, function (match) {
        var cls = 'number';
        if (/^"/.test(match)) {
            if (/:$/.test(match)) {
                cls = 'key';
            } else {
                cls = 'string';
            }
        } else if (/true|false/.test(match)) {
            cls = 'boolean';
        } else if (/null/.test(match)) {
            cls = 'null';
        }
        return '<span class="' + cls + '">' + match + '</span>';
    });
}

function init() {
    buttonRefresh(i);
    initializeTooltips();
    resetFormat();
    reorderDivs(i);
    //dynamicGenerateGraph(data[i])
    loadQuestionFormat(i);
}


function isEmptyObject(obj) {
    for (var prop in obj) {
        if (Object.prototype.hasOwnProperty.call(obj, prop)) {
            return false;
        }
    }
    return true;
}

function set_html(elementID, html) {
    $("#" + elementID).innerHTML(html)
}

function clear_html() {
    $("#dynamic").children().each(function () {
        if ($(this).attr('id') != 'anchor') {
            $(this).remove();
        }
    });
}

{% set logics=[] %}
{% for question in HIT.questions%}
{% for section in question.sections %}
{% if section.to_json().type not in logics %}
{{ section.staticGenerateGraphLogic() }}
{{ section.generate_save_function() }}
{% if logics.append(section.to_json().type) %}{% endif %}{# necessary jinja hack to modify a var inside inner loops (which are 'out of scope') #}
{% endif %}
{% endfor %}
{% endfor %}
