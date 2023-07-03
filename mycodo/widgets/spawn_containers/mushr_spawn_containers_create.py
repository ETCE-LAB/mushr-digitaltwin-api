# coding=utf-8
import logging

from mycodo.utils.constraints_pass import constraints_pass_positive_value
from mycodo.user_python_code import mushr_neomodel
from neomodel import db

logger = logging.getLogger(__name__)


def mushr_spawn_container_create(name, description, volume):
    """
    """

    s = mushr_neomodel.SpawnContainer(name=name,
                                      description=description,
                                      volume=float(volume))
    with db.transaction:
        s.save()

    return {"success": True}


WIDGET_INFORMATION = {
    'widget_name_unique': 'mushr_spawn_container_create',
    'widget_name': 'MushR SpawnContainer Creation Widget',
    'widget_library': '',
    'no_class': True,

    'url_manufacturer': '',
    'url_datasheet': '',
    'url_product_purchase': [
    ],
    'url_additional': '',

    'endpoints': [
        # Route URL, route endpoint name, view function, methods
        ("/mushr_spawn_container_create/<name>/<description>/<volume>",
         "mushr_spawn_container_create",
         mushr_spawn_container_create, ["GET"])
    ],

    'message': 'This widget creates StorageLocations for MushR',

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
    'widget_dashboard_body': """<form id='spawn_container_create_form'>
  <label for='spawn_container_name'>Name:</label><br>
  <input type='text' id='spawn_container_name' name='spawn_container_name'><br>
  <label for='spawn_container_description'>Description:</label><br>
  <textarea id='spawn_container_description' name='spawn_container_description'></textarea><br>
  <label for='spawn_container_volume'>Volume of Spawn Container</label><br>
  <input type='number' id='spawn_container_volume' name='spawn_container_volume'><br>
  <br><br>
  <input type='button' value='Submit' onclick='spawn_container_create_submit()'>
</form>
    <div id="status_mushr_spawn_container_create"></div>
<script>
function spawn_container_create_submit() {
  // Get the values of the form elements
  var name = document.getElementById('spawn_container_name').value;
  var description = document.getElementById('spawn_container_description').value;
  var volume = document.getElementById('spawn_container_volume').value;

  // Create an AJAX request
  var xhr = new XMLHttpRequest();
    xhr.open('GET', '/mushr_spawn_container_create/'+encodeURIComponent(name)+'/'+encodeURIComponent(description)+'/'+encodeURIComponent(volume), true);
  xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
  xhr.onreadystatechange = () => {
    data = JSON.parse(xhr.response);
    if (data.success)
       document.getElementById('status_mushr_spawn_container_create').innerHTML='<div class="alert alert-success">'+xhr.response+'</div>';
    else
       document.getElementById('status_mushr_spawn_container_create').innerHTML='<div class="alert alert-danger">'+xhr.response+'</div>';
    }
  xhr.send();
}

</script>
""",
    'widget_dashboard_js': """<!-- No JS content -->""",
    'widget_dashboard_js_ready': """<!-- No JS ready content -->""",
    'widget_dashboard_js_ready_end': """<!-- No JS ready end content -->"""
}
