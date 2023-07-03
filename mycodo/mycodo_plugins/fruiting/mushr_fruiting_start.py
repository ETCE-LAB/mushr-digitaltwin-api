# coding=utf-8
import logging


from mycodo.utils.constraints_pass import constraints_pass_positive_value
from mycodo.user_python_code import mushr_neomodel
from neomodel import db

logger = logging.getLogger(__name__)


def mushr_grow_chamber_uids():
    """Returns a list of GrowChamber uids

    """

    grow_chambers, meta = db.cypher_query("MATCH (gc:GrowChamber) return gc.uid", {})

    grow_chambers = [uidl[0] for uidl in grow_chambers]

    return {"uids": grow_chambers}


def mushr_available_fruiting_hole_uids():
    """Returns a list of FruitingHole uids of currently available
    SubstrateContainers that contain Substrate

    """

    unused_fruiting_holes, meta = db.cypher_query("MATCH (fh:FruitingHole)-[r1:IS_PART_OF]->(subc:SubstrateContainer)<-[r2:IS_CONTAINED_BY]-(sub:Substrate)-[r3:IS_INNOCULATED_FROM]->(ms) WHERE NOT exists(r2.end) and NOT (fh)<-[:FRUITS_THROUGH]-(:Flush) RETURN distinct(fh.uid)", {})

    unused_fruiting_holes = [uidl[0] for uidl in unused_fruiting_holes]

    available_fruiting_holes, meta = db.cypher_query("MATCH (fh:FruitingHole)-[r1:IS_PART_OF]->(subc:SubstrateContainer)<-[r2:IS_CONTAINED_BY]-(sub:Substrate)-[r3:IS_INNOCULATED_FROM]->(ms) WHERE NOT exists(r2.end) WITH fh MATCH (fh)<-[R:FRUITS_THROUGH]-(:Flush) WITH fh, collect(R) as Rcoll WHERE all(r in Rcoll WHERE exists(r.end)) RETURN distinct(fh.uid)", {})

    available_fruiting_holes = [uidl[0] for uidl in available_fruiting_holes]

    return {"uids": available_fruiting_holes + unused_fruiting_holes}


def mushr_fruiting_start(fruiting_hole_uid,
                         grow_chamber_uid):
    """
    """

    fruiting_hole = mushr_neomodel.FruitingHole.nodes.get_or_none(
        uid=fruiting_hole_uid)

    if not fruiting_hole:
        return {"success": False,
                "error": """UID for FruitingHole does not match an
                existing FruitingHole"""}

    if fruiting_hole_uid not in mushr_available_fruiting_hole_uids["uids"]:
        return {"success": False,
                "error": """FruitingHole is currently unavailable"""}

    substrate_container = fruiting_hole.is_part_of.all()

    if not substrate_container:
        return {"success": False,
                "error": """FruitingHole is not associated with any
                existing SubstrateContainer"""}

    if len(substrate_container) > 1:
        return {"success": False,
                "error": """FruitingHole is erroneously associated
                with multiple SubstrateContainers"""}

    substrate_container = substrate_container[0]
    # since substrate_container is a list of substrate_containers with
    # just one entry

    substrate = substrate_container.current_substrate()

    if not substrate:
        return {"success": False,
                "error": """Associated SubstrateContainer does not
                actively contain any Substrate"""}

    if len(substrate) > 1:
        return {"success": False,
                "error": """Associated SubstrateContainer erroneously
                contains two Substrates"""}

    substrate = substrate[0]
    # since substrate is a list of substrates with just one entry

    grow_chamber = mushr_neomodel.GrowChamber.nodes.get_or_none(uid=grow_chamber_uid)

    if not grow_chamber:
        return {"success": False,
                "error": """UID for GrowChamber does not match en
                existing GrowChamber"""}

    flush = mushr_neomodel.Flush()

    db.begin()
    try:
        flush.save()
        flush.fruits_from.connect(substrate)
        flush.fruits_through.connect(fruiting_hole)
        substrate_container.change_storage_location(grow_chamber_uid,
                                                    transaction=False)
        db.commit()

    except Exception as E:
        db.rollback()
        return {"success": False,
                "error": str(E)}

    return {"success": True}


WIDGET_INFORMATION = {
    'widget_name_unique': 'mushr_fruiting_start',
    'widget_name': 'MushR Fruiting Start Widget',
    'widget_library': '',
    'no_class': True,

    'url_manufacturer': '',
    'url_datasheet': '',
    'url_product_purchase': [
    ],
    'url_additional': '',

    'endpoints': [
        # Route URL, route endpoint name, view function, methods
        ("/mushr_fruiting_start/<fruiting_hole_uid>/<grow_chamber_uid>/",
         "mushr_fruiting_start",
         mushr_fruiting_start, ["GET"]),
        ("/mushr_available_fruiting_hole_uids",
         "mushr_available_fruiting_hole_uids",
         mushr_available_fruiting_hole_uids, ["GET"]),
        ("/mushr_grow_chamber_uids",
         "mushr_grow_chamber_uids",
         mushr_grow_chamber_uids, ["GET"])

    ],

    'message': 'This widget fascilites fruiting start for MushR',

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
    'widget_dashboard_body': """<form id='fruiting_form'>


    <datalist id='available_fruiting_hole_uids'></datalist>

  <label for='fruiting_hole_uid'>FruitingHole UID:</label><br>
  <input autocomplete='off' list='available_fruiting_hole_uids' type='text' id='fruiting_hole_uid' name='fruiting_hole_uid'><br>

    <datalist id='grow_chamber_uids'></datalist>

  <label for='grow_chamber_uid'>GrowChamber UID:</label><br>
  <input autocomplete='off' list='grow_chamber_uids' type='text' id='grow_chamber_uid' name='grow_chamber_uid'><br>
  <br><br>
  <input type='button' value='Submit' onclick='fruiting_submit()'>
</form>
    <div id="status_mushr_fruiting_start"></div>
<script>

function fill_datalist_grow_chamber_uids(){
    var xhr = new XMLHttpRequest();
    xhr.open('GET', '/mushr_grow_chamber_uids', true);
  xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
  xhr.onreadystatechange = () => {

    data = JSON.parse(xhr.response);
    console.log(data);

    if (data.uids.length){
        $('#grow_chamber_uids').html('');
    for (var i=0; i<data.uids.length; i++)
        $('#grow_chamber_uids').append('<option>'+data.uids[i]+'</option>');
    }
    else
        console.log("Error filling datalist");
    }
  xhr.send();
    }

function fill_datalist_available_fruiting_hole_uids(){
    var xhr = new XMLHttpRequest();
    xhr.open('GET', '/mushr_available_fruiting_hole_uids', true);
  xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
  xhr.onreadystatechange = () => {

    data = JSON.parse(xhr.response);
    console.log(data);

    if (data.uids.length){
        $('#available_fruiting_hole_uids').html('');
    for (var i=0; i<data.uids.length; i++)
        $('#available_fruiting_hole_uids').append('<option>'+data.uids[i]+'</option>');
    }
    else
        console.log("Error filling datalist");
    }
  xhr.send();
    }
fill_datalist_grow_chamber_uids();
fill_datalist_available_fruiting_hole_uids();

function fruiting_submit() {
  // Get the values of the form elements
  var fruiting_hole_uid = document.getElementById('fruiting_hole_uid').value;
  var grow_chamber_uid = document.getElementById('grow_chamber_uid').value;

  // Create an AJAX request
  var xhr = new XMLHttpRequest();
    xhr.open('GET', '/mushr_fruiting_start/'+encodeURIComponent(fruiting_hole_uid)+'/'+encodeURIComponent(grow_chamber_uid), true);
  xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
  xhr.onreadystatechange = () => {
    data = JSON.parse(xhr.response);
    if (data.success)
       document.getElementById('status_mushr_fruiting_start').innerHTML='<div class="alert alert-success">'+xhr.response+'</div>';
    else
       document.getElementById('status_mushr_fruiting_start').innerHTML='<div class="alert alert-danger">'+xhr.response+'</div>';
    }
  xhr.send();
}

</script>
""",
    'widget_dashboard_js': """<!-- No JS content -->""",
    'widget_dashboard_js_ready': """<!-- No JS ready content -->""",
    'widget_dashboard_js_ready_end': """<!-- No JS ready end content -->"""
}
