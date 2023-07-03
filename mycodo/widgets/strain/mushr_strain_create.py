# coding=utf-8
import logging


from mycodo.utils.constraints_pass import constraints_pass_positive_value
from mycodo.user_python_code import mushr_neomodel
from neomodel import db

logger = logging.getLogger(__name__)


def mushr_strain_create(weight,
                        source,
                        species,
                        mushroomCommonName):
    """
    """

    s = mushr_neomodel.Strain(weight=float(weight),
                              source=source,
                              species=species,
                              mushroomCommonName=mushroomCommonName)
    with db.transaction:
        s.save()

    return {"success": True}


WIDGET_INFORMATION = {
    'widget_name_unique': 'mushr_strain_create',
    'widget_name': 'MushR Strain Creation Widget',
    'widget_library': '',
    'no_class': True,

    'url_manufacturer': '',
    'url_datasheet': '',
    'url_product_purchase': [
    ],
    'url_additional': '',

    'endpoints': [
        # Route URL, route endpoint name, view function, methods
        ("/mushr_strain_create/<weight>/<source>/<species>/<mushroomCommonName>",
         "mushr_strain_create",
         mushr_strain_create, ["GET"])
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
    'widget_dashboard_body': """<form id='strain_create_form'>
  <label for='strain_weight'>Weight:</label><br>
  <input type='number' id='strain_weight' name='strain_'><br>
  <label for='strain_source'>Source:</label><br>
  <input type='text' id='strain_source' name='strain_source'><br>
  <label for='strain_species'>Species:</label><br>
  <input type='text' id='strain_species' name='strain_species'><br>
  <label for='strain_mushroom_common_name'>Mushroom Common Name:</label><br>
  <input type='text' id='strain_mushroom_common_name' name='strain_mushroom_common_name'><br><br><br>
  <input type='button' value='Submit' onclick='strain_create_submit()'>
</form>
    <div id="status_mushr_strain_create"></div>
<script>
function strain_create_submit() {
  // Get the values of the form elements
  var weight = document.getElementById('strain_weight').value;
  var source = document.getElementById('strain_source').value;
  var species = document.getElementById('strain_species').value;
  var mushroomCommonName = document.getElementById('strain_mushroom_common_name').value;

  // Create an AJAX request
  var xhr = new XMLHttpRequest();
    xhr.open('GET', '/mushr_strain_create/'+encodeURIComponent(weight)+'/'+encodeURIComponent(source)+'/'+encodeURIComponent(species)+'/'+encodeURIComponent(mushroomCommonName), true);
  xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
  xhr.onreadystatechange = () => {
    data = JSON.parse(xhr.response);
    if (data.success)
       document.getElementById('status_mushr_strain_create').innerHTML='<div class="alert alert-success">'+xhr.response+'</div>';
    else
       document.getElementById('status_mushr_strain_create').innerHTML='<div class="alert alert-danger">'+xhr.response+'</div>';
    }
  xhr.send();
}

</script>
""",
    'widget_dashboard_js': """<!-- No JS content -->""",
    'widget_dashboard_js_ready': """<!-- No JS ready content -->""",
    'widget_dashboard_js_ready_end': """<!-- No JS ready end content -->"""
}
