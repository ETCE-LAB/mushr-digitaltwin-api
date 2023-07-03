# coding=utf-8
import logging


from mycodo.utils.constraints_pass import constraints_pass_positive_value
from mycodo.user_python_code import mushr_neomodel
from neomodel import db
import datetime

logger = logging.getLogger(__name__)


def mushr_free_spawn_container_uids():
    """Returns a list of SpawnContainer uids which currently are
    not containing any spawn.
    """

    free_spawn_containers, meta = db.cypher_query(
        "MATCH (subc:SpawnContainer) WHERE (:Spawn)-[:IS_CONTAINED_BY]->(subc) WITH subc MATCH (:Spawn)-[R:IS_CONTAINED_BY]->(subc) WITH subc, collect(R) as Rcoll WHERE all(r in Rcoll WHERE exists(r.end)) return distinct(subc.uid)",
        {"timestamp": datetime.datetime.now().timestamp()})

    new_spawn_containers, meta = db.cypher_query(
        "MATCH (subc:SpawnContainer) WHERE NOT (subc)<-[:IS_CONTAINED_BY]-(:Spawn) RETURN subc.uid"
    )

    free_spawn_containers = [uidl[0] for uidl in free_spawn_containers]
    new_spawn_containers = [uidl[0] for uidl in new_spawn_containers]

    return {"uids": free_spawn_containers + new_spawn_containers}


def mushr_spawn_create(weight,
                       composition,
                       spawn_container_uid):
    """
    """

    s = mushr_neomodel.Spawn(weight=float(weight),
                             composition=composition)

    spawn_container = mushr_neomodel.SpawnContainer.nodes.get_or_none(
        uid=spawn_container_uid)

    if not spawn_container:
        return {"success": False,
                "error": "UID for spawn container seems invalid"}

    if spawn_container_uid not in mushr_free_spawn_container_uids()["uids"]:
        return {"success": False,
                "error": "SpawnContainer is currently occupied"}

    with db.transaction:
        s.save()
        s.is_contained_by.connect(spawn_container)

    return {"success": True}


WIDGET_INFORMATION = {
    'widget_name_unique': 'mushr_spawn_create',
    'widget_name': 'MushR Spawn Creation Widget',
    'widget_library': '',
    'no_class': True,

    'url_manufacturer': '',
    'url_datasheet': '',
    'url_product_purchase': [
    ],
    'url_additional': '',

    'endpoints': [
        # Route URL, route endpoint name, view function, methods
        ("/mushr_spawn_create/<weight>/<composition>/<spawn_container_uid>",
         "mushr_spawn_create",
         mushr_spawn_create, ["GET"]),
        ("/mushr_free_spawn_container_uids",
         "mushr_free_spawn_container_uids",
         mushr_free_spawn_container_uids, ["GET"])

    ],

    'message': 'This widget creates spawn for MushR',

    # Any dependencies required by the output module. An empty list means no dependencies are required.
    'dependencies_module': [],

    # A message to be displayed on the dependency install page
    'dependencies_message': 'Are you sure you want to install these dependencies? They require...',

    'widget_width': 8,
    'widget_height': 8,

    'custom_options': [
        {
            'id': 'neo4j_username',
            'type': 'text',
            'default_value': "neo4j",
            'name': 'Neo4j Username',
            'phrase': 'Username for neo4j'
        },
        {
            'id': 'neo4j_password',
            'type': 'text',
            'default_value': "neo4j",
            'name': 'Neo4j Password',
            'phrase': 'Username for neo4j'
        },
        {
            'id': 'neo4j_host_url',
            'type': 'text',
            'default_value': "localhost:7687",
            'name': 'Neo4j Host URL',
            'phrase': 'The host URL for neo4j'
        },
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
    'widget_dashboard_body': """<form id='spawn_create_form'>
  <label for='spawn_weight'>Weight:</label><br>
  <input type='number' id='spawn_weight' name='spawn_weight'><br>
  <label for='spawn_composition'>Composition:</label><br>
  <textarea id='spawn_composition' name='spawn_composition'></textarea><br>
  <label for='spawn_container_uid'>Container UID</label><br>

    <datalist id='free_spawn_containers'></datalist>

  <input autocomplete='off', list='free_spawn_containers' type='text' id='spawn_container_uid' name='spawn_container_uid'><br>

  <br><br>
  <input type='button' value='Submit' onclick='spawn_create_submit()'>
</form>
    <div id="status_mushr_spawn_create"></div>
<script>

function fill_datalist_spawn_containers(){
    var xhr = new XMLHttpRequest();
    xhr.open('GET', '/mushr_free_spawn_container_uids', true);
  xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
  xhr.onreadystatechange = () => {

    data = JSON.parse(xhr.responseText);
    console.log(data);

    if (data.uids.length){
        $('#free_spawn_containers').html('');
    for (var i=0; i<data.uids.length; i++)
        $('#free_spawn_containers').append('<option>'+data.uids[i]+'</option>');
    }
    else
        console.log("Error filling datalist");
    }
  xhr.send();
    }

function spawn_create_submit() {
  // Get the values of the form elements
  var weight = document.getElementById('spawn_weight').value;
  var composition = document.getElementById('spawn_composition').value;
  var spawn_container_uid = document.getElementById('spawn_container_uid').value;

  // Create an AJAX request
  var xhr = new XMLHttpRequest();
    xhr.open('GET', '/mushr_spawn_create/'+encodeURIComponent(weight)+'/'+encodeURIComponent(composition)+'/'+encodeURIComponent(spawn_container_uid), true);
  xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
  xhr.onreadystatechange = () => {
    data = JSON.parse(xhr.response);
    if (data.success)
       document.getElementById('status_mushr_spawn_create').innerHTML='<div class="alert alert-success">'+xhr.response+'</div>';
    else
       document.getElementById('status_mushr_spawn_create').innerHTML='<div class="alert alert-danger">'+xhr.response+'</div>';
    }
  xhr.send();
}

fill_datalist_spawn_containers();
</script>
""",
    'widget_dashboard_js': """<!-- No JS content -->""",
    'widget_dashboard_js_ready': """<!-- No JS ready content -->""",
    'widget_dashboard_js_ready_end': """<!-- No JS ready end content -->"""
}
