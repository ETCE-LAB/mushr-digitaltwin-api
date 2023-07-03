# coding=utf-8
import logging


from mycodo.utils.constraints_pass import constraints_pass_positive_value
from mycodo.user_python_code import mushr_neomodel
from neomodel import db
import datetime

logger = logging.getLogger(__name__)


def mushr_free_substrate_container_uids():
    """Returns a list of SubstrateContainer uids which currently are
    not containing any Substrate.
    """

    free_substrate_containers, meta = db.cypher_query(
        "MATCH (subc:SubstrateContainer) WHERE (:Substrate)-[:IS_CONTAINED_BY]->(subc) WITH subc MATCH (:Substrate)-[R:IS_CONTAINED_BY]->(subc) WITH subc, collect(R) as Rcoll WHERE all(r in Rcoll WHERE exists(r.end)) return distinct(subc.uid)",
        {})

    new_substrate_containers, meta = db.cypher_query(
        "MATCH (subc:SubstrateContainer) WHERE NOT (subc)<-[:IS_CONTAINED_BY]-(:Substrate) RETURN subc.uid"
    )

    free_substrate_containers = [uidl[0] for uidl in free_substrate_containers]
    new_substrate_containers = [uidl[0] for uidl in new_substrate_containers]

    return {"uids": free_substrate_containers + new_substrate_containers}


def mushr_substrate_create(weight,
                           composition,
                           substrate_container_uid):
    """
    """

    s = mushr_neomodel.Substrate(weight=float(weight),
                                 composition=composition)
    substrate_container = mushr_neomodel.SubstrateContainer.nodes.get_or_none(
        uid=substrate_container_uid)

    if not substrate_container:
        return {"success": False,
                "error": "UID for substrate container seems invalid"}

    if substrate_container_uid not in mushr_free_substrate_container_uids()["uids"]:
        return {"success": False,
                "error": "SubstrateContainer is currently occupied"}

    with db.transaction:
        s.save()
        s.is_contained_by.connect(substrate_container)

    return {"success": True}


WIDGET_INFORMATION = {
    'widget_name_unique': 'mushr_substrate_create',
    'widget_name': 'MushR Substrate Creation Widget',
    'widget_library': '',
    'no_class': True,

    'url_manufacturer': '',
    'url_datasheet': '',
    'url_product_purchase': [
    ],
    'url_additional': '',

    'endpoints': [
        # Route URL, route endpoint name, view function, methods
        ("/mushr_substrate_create/<weight>/<composition>/<substrate_container_uid>",
         "mushr_substrate_create",
         mushr_substrate_create, ["GET"]),
        ("/mushr_free_substrate_container_uids",
         "mushr_free_substrate_container_uids",
         mushr_free_substrate_container_uids, ["GET"])
    ],

    'message': 'This widget creates Substrate for MushR',

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
    'widget_dashboard_body': """<form id='substrate_create_form'>
  <label for='substrate_weight'>Weight:</label><br>
  <input type='number' id='substrate_weight' name='substrate_weight'><br>
  <label for='substrate_composition'>Composition:</label><br>
  <textarea id='substrate_composition' name='substrate_composition'></textarea><br>
  <label for='substrate_container_uid'>Container UID</label><br>

    <datalist id='free_substrate_containers'></datalist>

  <input autocomplete='off' list='free_substrate_containers' type='text' id='substrate_container_uid' name='substrate_container_uid'><br>
  <br><br>
  <input type='button' value='Submit' onclick='substrate_create_submit()'>
</form>
    <div id="status_mushr_substrate_create"></div>
<script>

function fill_datalist_substrate_containers(){
    var xhr = new XMLHttpRequest();
    xhr.open('GET', '/mushr_free_substrate_container_uids', true);
  xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
  xhr.onreadystatechange = () => {

    data = JSON.parse(xhr.responseText);
    console.log(data);

    if (data.uids.length){
        $('#free_substrate_containers').html('');
    for (var i=0; i<data.uids.length; i++)
        $('#free_substrate_containers').append('<option>'+data.uids[i]+'</option>');
    }
    else
        console.log("Error filling datalist");
    }
  xhr.send();
    }
function substrate_create_submit() {
  // Get the values of the form elements
  var weight = document.getElementById('substrate_weight').value;
  var composition = document.getElementById('substrate_composition').value;
  var substrate_container_uid = document.getElementById('substrate_container_uid').value;

  // Create an AJAX request
  var xhr = new XMLHttpRequest();
    xhr.open('GET', '/mushr_substrate_create/'+encodeURIComponent(weight)+'/'+encodeURIComponent(composition)+'/'+encodeURIComponent(substrate_container_uid), true);
  xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
  xhr.onreadystatechange = () => {
    data = JSON.parse(xhr.response);
    if (data.success)
       document.getElementById('status_mushr_substrate_create').innerHTML='<div class="alert alert-success">'+xhr.response+'</div>';
    else
       document.getElementById('status_mushr_substrate_create').innerHTML='<div class="alert alert-danger">'+xhr.response+'</div>';
    }
  xhr.send();
}

fill_datalist_substrate_containers();

</script>
""",
    'widget_dashboard_js': """<!-- No JS content -->""",
    'widget_dashboard_js_ready': """<!-- No JS ready content -->""",
    'widget_dashboard_js_ready_end': """<!-- No JS ready end content -->"""
}
