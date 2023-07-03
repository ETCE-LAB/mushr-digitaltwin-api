# coding=utf-8
import logging


from mycodo.utils.constraints_pass import constraints_pass_positive_value
from mycodo.user_python_code import mushr_neomodel
from neomodel import db

logger = logging.getLogger(__name__)


def mushr_location_uids():
    """Returns a list of Location uids

    """

    locations, meta = db.cypher_query("MATCH (loc:Location) return loc.uid", {})

    locations = [uidl[0] for uidl in locations]

    return {"uids": locations}


def mushr_container_uids():
    """Returns a list of SubstrateContainer and SpawnContainer uids"""

    containers, meta = db.cypher_query("MATCH (con) WHERE (con:SubstrateContainer or con:SpawnContainer) return con.uid", {})

    containers = [uidl[0] for uidl in containers]

    return {"uids": containers}


def mushr_change_storage_location(container_uid,
                                  new_location_uid):

    container = (
        mushr_neomodel.SpawnContainer.nodes.get_or_none(uid=container_uid) or
        mushr_neomodel.SubstrateContainer.nodes.get_or_none(uid=container_uid))

    if not container:
        return {"success": False,
                "error": """Container UID is not representative of a
                SpawnContainer or SubstrateContainer"""}

    new_loc = container.change_storage_location(new_location_uid,
                                                transaction=True)

    if new_loc:
        return {"success": True}
    else:
        return {"success": False}


WIDGET_INFORMATION = {
    'widget_name_unique': 'mushr_change_storage_location',
    'widget_name': 'MushR Change Storage Location Widget',
    'widget_library': '',
    'no_class': True,

    'url_manufacturer': '',
    'url_datasheet': '',
    'url_product_purchase': [
    ],
    'url_additional': '',

    'endpoints': [
        # Route URL, route endpoint name, view function, methods
        ("/mushr_change_storage_location/<container_uid>/<new_location_uid>/",
         "mushr_change_storage_location",
         mushr_change_storage_location, ["GET"]),
        ("/mushr_location_uids",
         "mushr_location_uids",
         mushr_location_uids, ["GET"]),
        ("/mushr_container_uids",
         "mushr_container_uids",
         mushr_container_uids, ["GET"])

    ],

    'message': 'This widget changes storage locations of SpawnContainers and SubstrateContainers for MushR',

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
    'widget_dashboard_body': """<form id='change_storage_location_form'>

    <datalist id='container_uids'></datalist>

  <label for='container_uid'>Container UID:</label><br>
  <input autocomplete='off' list='container_uids' type='text' id='container_uid' name='container_uid'><br>

    <datalist id='location_uids'></datalist>

  <label for='location_uid'>New Location UID:</label><br>
  <input autocomplete='off' list='location_uids' type='text' id='new_location_uid' name='location_uid'><br>
  <br><br>
  <input type='button' value='Submit' onclick='change_storage_location_submit()'>
</form>
    <div id="status_mushr_change_storage_location"></div>
<script>

function fill_datalist_location_uids(){
    var xhr = new XMLHttpRequest();
    xhr.open('GET', '/mushr_location_uids', true);
  xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
  xhr.onreadystatechange = () => {

    data = JSON.parse(xhr.response);
    console.log(data);

    if (data.uids.length){
        $('#location_uids').html('');
    for (var i=0; i<data.uids.length; i++)
        $('#location_uids').append('<option>'+data.uids[i]+'</option>');
    }
    else
        console.log("Error filling datalist");
    }
  xhr.send();
    }

function fill_datalist_container_uids(){
    var xhr = new XMLHttpRequest();
    xhr.open('GET', '/mushr_container_uids', true);
  xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
  xhr.onreadystatechange = () => {

    data = JSON.parse(xhr.response);
    console.log(data);

    if (data.uids.length){
        $('#container_uids').html('');
    for (var i=0; i<data.uids.length; i++)
        $('#container_uids').append('<option>'+data.uids[i]+'</option>');
    }
    else
        console.log("Error filling datalist");
    }
  xhr.send();
    }
fill_datalist_location_uids();
fill_datalist_container_uids();

function change_storage_location_submit() {
  // Get the values of the form elements
  var container_uid = document.getElementById('container_uid').value;
  var new_location_uid = document.getElementById('new_location_uid').value;

  // Create an AJAX request
  var xhr = new XMLHttpRequest();
    xhr.open('GET', '/mushr_change_storage_location/'+encodeURIComponent(container_uid)+'/'+encodeURIComponent(new_location_uid), true);
  xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
  xhr.onreadystatechange = () => {
    data = JSON.parse(xhr.response);
    if (data.success)
       document.getElementById('status_mushr_change_storage_location').innerHTML='<div class="alert alert-success">'+xhr.response+'</div>';
    else
       document.getElementById('status_mushr_change_storage_location').innerHTML='<div class="alert alert-danger">'+xhr.response+'</div>';
    }
  xhr.send();
}

</script>
""",
    'widget_dashboard_js': """<!-- No JS content -->""",
    'widget_dashboard_js_ready': """<!-- No JS ready content -->""",
    'widget_dashboard_js_ready_end': """<!-- No JS ready end content -->"""
}
