# coding=utf-8
import logging


from mycodo.utils.constraints_pass import constraints_pass_positive_value
from mycodo.user_python_code import mushr_neomodel
from neomodel import db

logger = logging.getLogger(__name__)


def mushr_occupied_spawn_container_uids():
    """Returns a list of SpawnContainer uids which currently are
    containing spawn.
    """

    occupied_spawn_containers, meta = db.cypher_query("MATCH \
    (sp:Spawn)-[R:IS_CONTAINED_BY]->(spc:SpawnContainer) \
    WHERE NOT exists(R.end) RETURN spc.uid", {})

    occupied_spawn_containers = [uidl[0] for uidl in occupied_spawn_containers]

    return {"uids": occupied_spawn_containers}


def mushr_spawn_discard(spawn_container_uid):
    """
    """

    spawn_container = mushr_neomodel.SpawnContainer.nodes.get_or_none(
        uid=spawn_container_uid)

    if not spawn_container:
        return {"success": False,
                "error": "SpawnContainer not found"}

    # Fetch the spawn contained by the spawn container

    results, meta = db.cypher_query("MATCH \
    (n:Spawn)-[R:IS_CONTAINED_BY]->(n2:SpawnContainer) \
    WHERE n2.uid=$spawn_container_uid AND NOT exists(R.end) return n",
                                    {"spawn_container_uid":
                                     spawn_container_uid})

    if len(results[0]) > 1:
        return {"success": False,
                "error": "SpawnContainer erroneously contains multiple Spawns"}

    spawn = mushr_neomodel.Spawn.inflate(results[0][0])
    rel = spawn.is_contained_by.relationship(spawn_container)

    with db.transaction:
        rel.end = mushr_neomodel.currenttime()
        rel.save()

    return {"success": True}


WIDGET_INFORMATION = {
    'widget_name_unique': 'mushr_spawn_discard',
    'widget_name': 'MushR Spawn Discard Widget',
    'widget_library': '',
    'no_class': True,

    'url_manufacturer': '',
    'url_datasheet': '',
    'url_product_purchase': [
    ],
    'url_additional': '',

    'endpoints': [
        # Route URL, route endpoint name, view function, methods
        ("/mushr_spawn_discard/<spawn_container_uid>",
         "mushr_spawn_discard",
         mushr_spawn_discard, ["GET"]),
        ("/mushr_occupied_spawn_container_uids",
         "mushr_occupied_spawn_container_uids",
         mushr_occupied_spawn_container_uids, ["GET"])
    ],

    'message': 'This widget discard spawn for MushR',

    # Any dependencies required by the output module. An empty list means no dependencies are required.
    'dependencies_module': [],

    # A message to be displayed on the dependency install page
    'dependencies_message': 'Are you sure you want to install these dependencies? They require...',

    'widget_width': 8,
    'widget_height': 8,

    'custom_options': [
        {
            'id': 'font_em_body',
            'type': 'float',
            'default_value': 1.5,
            'constraints_pass': constraints_pass_positive_value,
            'name': 'Body Font Size (em)',
            'phrase': 'The font size of the body text'
        }
    ],

    'widget_dashboard_head': """<!-- No head content -->""",
    'widget_dashboard_title_bar': """<span style="padding-right: 0.5em; font-size: {{each_widget.font_em_name}}em">{{each_widget.name}}</span>""",
    'widget_dashboard_body': """<form id='spawn_discard_form'>
  <label for='spawn_container_uid'>Container UID</label><br>

    <datalist id='occupied_spawn_containers'></datalist>

  <input autocomplete='off', list='occupied_spawn_containers' type='text' id='dis_spawn_container_uid' name='dis_spawn_container_uid'><br>

  <br><br>
  <input type='button' value='Submit' onclick='spawn_discard_submit()'>
</form>
    <div id="status_mushr_spawn_discard"></div>
<script>

function fill_datalist_occupied_spawn_containers(){
    var xhr = new XMLHttpRequest();
    xhr.open('GET', '/mushr_occupied_spawn_container_uids', true);
  xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
  xhr.onreadystatechange = () => {

    data = JSON.parse(xhr.responseText);
    console.log(data);

    if (data.uids.length){
        $('#occupied_spawn_containers').html('');
    for (var i=0; i<data.uids.length; i++)
        $('#occupied_spawn_containers').append('<option>'+data.uids[i]+'</option>');
    }
    else
        console.log("Error filling datalist");
    }
  xhr.send();
    }

function spawn_discard_submit() {
  // Get the values of the form elements
  var dis_spawn_container_uid = document.getElementById('dis_spawn_container_uid').value;

  // Create an AJAX request
  var xhr = new XMLHttpRequest();
    xhr.open('GET', '/mushr_spawn_discard/'+encodeURIComponent(dis_spawn_container_uid), true);
  xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
  xhr.onreadystatechange = () => {
    data = JSON.parse(xhr.response);
    if (data.success)
       document.getElementById('status_mushr_spawn_discard').innerHTML='<div class="alert alert-success">'+xhr.response+'</div>';
    else
       document.getElementById('status_mushr_spawn_discard').innerHTML='<div class="alert alert-danger">'+xhr.response+'</div>';
    }
  xhr.send();
}

fill_datalist_occupied_spawn_containers();
</script>
""",
    'widget_dashboard_js': """<!-- No JS content -->""",
    'widget_dashboard_js_ready': """<!-- No JS ready content -->""",
    'widget_dashboard_js_ready_end': """<!-- No JS ready end content -->"""
}
