# coding=utf-8
import logging


from mycodo.utils.constraints_pass import constraints_pass_positive_value
from mycodo.user_python_code import mushr_neomodel
from neomodel import db

logger = logging.getLogger(__name__)


def mushr_occupied_substrate_container_uids():
    """Returns a list of SubstrateContainer uids which currently are
    containing substrate.
    """

    occupied_substrate_containers, meta = db.cypher_query("MATCH \
    (sp:Substrate)-[R:IS_CONTAINED_BY]->(spc:SubstrateContainer) \
    WHERE NOT exists(R.end) RETURN spc.uid", {})

    occupied_substrate_containers = [uidl[0]
                                     for uidl in occupied_substrate_containers]

    return {"uids": occupied_substrate_containers}


def mushr_substrate_discard(substrate_container_uid):
    """WARNING: ALSO Discards Flushes that were fruiting from the
    contained substrate

    """

    substrate_container = mushr_neomodel.SubstrateContainer.nodes.get_or_none(
        uid=substrate_container_uid)

    if not substrate_container:
        return {"success": False,
                "error": "SubstrateContainer not found"}

    # Fetch the substrate contained by the substrate container

    results, meta = db.cypher_query("MATCH \
    (n:Substrate)-[R:IS_CONTAINED_BY]->(n2:SubstrateContainer) \
    WHERE n2.uid=$substrate_container_uid AND NOT exists(R.end) return n",
                                    {"substrate_container_uid":
                                     substrate_container_uid})

    if len(results[0]) > 1:
        return {"success": False,
                "error": """SubstrateContainer erroneously contains
                            multiple Substrates"""}

    elif len(results[0]) == 0:
        return {"success": False,
                "error": """SubstrateContainer does not contain any
                substrate"""}

    substrate = mushr_neomodel.Substrate.inflate(results[0][0])
    rel = substrate.is_contained_by.relationship(substrate_container)

    # Fetch Flushes that are currently fruiting from the Substrate,
    # then find the fruiting hole it is fruiting through

    results, meta = db.cypher_query("MATCH \
    (n:Flush)-[r:FRUITS_FROM]->(sub:Substrate) \
    WHERE sub.uid=$substrate_uid AND NOT exists(r.end) \
    WITH n \
    MATCH (n)-[r:FRUITS_THROUGH]->(fh:FruitingHole)-[:IS_PART_OF]->(subc) \
    WHERE subc:SubstrateContainer AND subc.uid=$substrate_container_uid \
    RETURN n,fh", {"substrate_uid": substrate.uid,
                   "substrate_container_uid": substrate_container.uid})

    fruits_through_rels = []

    # Inflate the raw Flush and FruitingHole objects to their
    # respective neomodels, and fetch the fruits_through neomodel

    for result in results:

        raw_fruiting_flush_obj = result[0]
        raw_fruiting_hole_obj = result[1]

        flush = mushr_neomodel.Flush.inflate(
            raw_fruiting_flush_obj)
        fruiting_hole = mushr_neomodel.FruitingHole.inflate(
            raw_fruiting_hole_obj)

        fruits_through_rels.append(
            flush.fruits_through.relationship(fruiting_hole))

    with db.transaction:
        # Pre-compute the current time so that all the following
        # relations are updated with the same timestamp

        # Discard the Substrate
        current_time = mushr_neomodel.currenttime()
        rel.end = current_time
        rel.save()

        # For every flush, end the fruiting period
        for fruits_through in fruits_through_rels:
            fruits_through.end = current_time
            fruits_through.save()

    return {"success": True}


WIDGET_INFORMATION = {
    'widget_name_unique': 'mushr_substrate_discard',
    'widget_name': 'MushR Substrate Discard Widget',
    'widget_library': '',
    'no_class': True,

    'url_manufacturer': '',
    'url_datasheet': '',
    'url_product_purchase': [
    ],
    'url_additional': '',

    'endpoints': [
        # Route URL, route endpoint name, view function, methods
        ("/mushr_substrate_discard/<substrate_container_uid>",
         "mushr_substrate_discard",
         mushr_substrate_discard, ["GET"]),
        ("/mushr_occupied_substrate_container_uids",
         "mushr_occupied_substrate_container_uids",
         mushr_occupied_substrate_container_uids, ["GET"])
    ],

    'message': 'This widget discard substrate for MushR',

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
    'widget_dashboard_body': """<form id='substrate_discard_form'>
  <label for='substrate_container_uid'>Container UID</label><br>

    <datalist id='occupied_substrate_containers'></datalist>

  <input autocomplete='off', list='occupied_substrate_containers' type='text' id='dis_substrate_container_uid' name='dis_substrate_container_uid'><br>

  <br><br>
  <input type='button' value='Submit' onclick='substrate_discard_submit()'>
</form>
    <div id="status_mushr_substrate_discard"></div>
<script>

function fill_datalist_occupied_substrate_containers(){
    var xhr = new XMLHttpRequest();
    xhr.open('GET', '/mushr_occupied_substrate_container_uids', true);
  xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
  xhr.onreadystatechange = () => {

    data = JSON.parse(xhr.responseText);
    console.log(data);

    if (data.uids.length){
        $('#occupied_substrate_containers').html('');
    for (var i=0; i<data.uids.length; i++)
        $('#occupied_substrate_containers').append('<option>'+data.uids[i]+'</option>');
    }
    else
        console.log("Error filling datalist");
    }
  xhr.send();
    }

function substrate_discard_submit() {
  // Get the values of the form elements
  var dis_substrate_container_uid = document.getElementById('dis_substrate_container_uid').value;

  // Create an AJAX request
  var xhr = new XMLHttpRequest();
    xhr.open('GET', '/mushr_substrate_discard/'+encodeURIComponent(dis_substrate_container_uid), true);
  xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
  xhr.onreadystatechange = () => {
    data = JSON.parse(xhr.response);
    if (data.success)
       document.getElementById('status_mushr_substrate_discard').innerHTML='<div class="alert alert-success">'+xhr.response+'</div>';
    else
       document.getElementById('status_mushr_substrate_discard').innerHTML='<div class="alert alert-danger">'+xhr.response+'</div>';
    }
  xhr.send();
}

fill_datalist_occupied_substrate_containers();
</script>
""",
    'widget_dashboard_js': """<!-- No JS content -->""",
    'widget_dashboard_js_ready': """<!-- No JS ready content -->""",
    'widget_dashboard_js_ready_end': """<!-- No JS ready end content -->"""
}
