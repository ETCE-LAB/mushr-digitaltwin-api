# coding=utf-8
import logging


from mycodo.utils.constraints_pass import constraints_pass_positive_value
from mycodo.user_python_code import mushr_neomodel
from neomodel import db

logger = logging.getLogger(__name__)


def mushr_grow_chamber_create(name,
                              description):
    """
    """
    gc = mushr_neomodel.GrowChamber(name=name, description=description)
    with db.transaction:
        gc.save()

    return {"success": True}


WIDGET_INFORMATION = {
    'widget_name_unique': 'mushr_grow_chamber_create',
    'widget_name': 'MushR GrowChamber Creation Widget',
    'widget_library': '',
    'no_class': True,

    'url_manufacturer': '',
    'url_datasheet': '',
    'url_product_purchase': [
    ],
    'url_additional': '',

    'endpoints': [
        # Route URL, route endpoint name, view function, methods
        ("/mushr_grow_chamber_create/<name>/<description>",
         "mushr_grow_chamber_create",
         mushr_grow_chamber_create, ["GET"])
    ],

    'message': 'This widget creates GrowChambers for MushR',

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
    'widget_dashboard_body': """<form id='grow_chamber_create_form'>
  <label for='growchamber_name'>Name:</label><br>
  <input type='text' id='growchamber_name' name='growchamber_name'><br>
  <label for='growchamber_description'>Description:</label><br>
  <textarea id='growchamber_description' name='growchamber_description'></textarea><br><br>
  <br><br>
  <input type='button' value='Submit' onclick='submit_grow_chamber_create()'>
</form>
    <div id="status_mushr_grow_chamber_create"></div>
<script>
function submit_grow_chamber_create() {
  // Get the values of the form elements
  var growchamber_name = document.getElementById('growchamber_name').value;
  var growchamber_description= document.getElementById('growchamber_description').value;

  // Create an AJAX request
  var xhr = new XMLHttpRequest();
    xhr.open('GET', '/mushr_grow_chamber_create/'+encodeURIComponent(growchamber_name)+'/'+encodeURIComponent(growchamber_description), true);
  xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
  xhr.onreadystatechange = () => {
    if (xhr.response.success)
       document.getElementById('status_mushr_grow_chamber_create').innerHTML='<div class="alert alert-success">'+xhr.response+'</div>';
    else
       document.getElementById('status_mushr_grow_chamber_create').innerHTML='<div class="alert alert-danger">'+xhr.response+'</div>';
    }
  xhr.send();
}

</script>
""",
    'widget_dashboard_js': """<!-- No JS content -->""",
    'widget_dashboard_js_ready': """<!-- No JS ready content -->""",
    'widget_dashboard_js_ready_end': """<!-- No JS ready end content -->"""
}
