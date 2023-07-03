# coding=utf-8
import logging

from mycodo.utils.constraints_pass import constraints_pass_positive_value
from mycodo.user_python_code import mushr_neomodel
from neomodel import db

logger = logging.getLogger(__name__)


def mushr_available_legacy_fruiting_hole_uids():
    """Returns a list of fruiting holes which have flushes currently
    fruiting through them (for legacy substrate)"""

    available_fruiting_holes, meta = db.cypher_query("MATCH (fh:FruitingHole)<-[r1:FRUITS_THROUGH]-(:Flush)-[:FRUITS_FROM]->(sub) WHERE not exists(r1.end) and not (sub)-[:IS_CONTAINED_BY]->(:SubstrateContainer) return fh.uid, sub.composition", {})

    available_fruiting_hole_uids = [row[0] for row in available_fruiting_holes]
    available_fruiting_hole_substrate_composition = [
        row[1] for row in available_fruiting_holes]

    return {"uids": available_fruiting_hole_uids,
            "composition": available_fruiting_hole_substrate_composition}


def mushr_harvest_legacy(legacy_fruiting_hole_uid, weight):
    """
    """

    fruiting_hole = mushr_neomodel.FruitingHole.nodes.get_or_none(
        uid=legacy_fruiting_hole_uid)

    if ((not fruiting_hole) or (legacy_fruiting_hole_uid not in
                                mushr_available_legacy_fruiting_hole_uids()["uids"])):
        return {"success": False,
                "error": """FruitingHole UID is not representative of
                a FruitingHole with a currently fruiting Flush"""}

    flush, meta = db.cypher_query("MATCH (fl:Flush)-[r1:FRUITS_THROUGH]->(fh:FruitingHole) WHERE not exists(r1.end) and fh.uid=$fruiting_hole_uid return fl",
                                  {"fruiting_hole_uid": fruiting_hole.uid})

    if len(flush[0]) > 1:
        return {"success": False,
                "error": """FruitingHole erroneously has multiple
                Flushes fruiting through"""}

    if len(flush[0]) == 0:
        return {"success": False,
                "error": """FruitingHole does not have any flushes currently fruiting through"""}

    flush = mushr_neomodel.Flush.inflate(flush[0][0])

    substrate = flush.fruits_from.all()

    if not substrate:
        return {"success": False,
                "error": """Selected Flush is erroneously not fruiting
                from any Substrates"""}

    if len(substrate) > 1:
        return {"success": False,
                "error": """Selected Flush is erroneously fruiting
                multiple Substrates"""}

    mushroom_harvest = mushr_neomodel.MushroomHarvest(weight=weight)

    with db.transaction:
        rel = flush.fruits_through.relationship(fruiting_hole)
        rel.end = mushr_neomodel.currenttime()
        rel.save()
        mushroom_harvest.save()
        mushroom_harvest.is_harvested_from.connect(flush)

    return {"success": True}


WIDGET_INFORMATION = {
    'widget_name_unique': 'mushr_harvest_legacy',
    'widget_name': 'MushR Harvesting Widget for legacy MushR spreadsheet compatibility (Does not require a SubstrateContainer)',
    'widget_library': '',
    'no_class': True,

    'url_manufacturer': '',
    'url_datasheet': '',
    'url_product_purchase': [
    ],
    'url_additional': '',

    'endpoints': [
        # Route URL, route endpoint name, view function, methods
        ("/mushr_harvest_legacy/<legacy_fruiting_hole_uid>/<weight>",
         "mushr_harvest_legacy",
         mushr_harvest_legacy, ["GET"]),
        ("/mushr_available_legacy_fruiting_hole_uids",
         "mushr_available_legacy_fruiting_hole_uids",
         mushr_available_legacy_fruiting_hole_uids, ["GET"])
    ],

    'message': 'This widget fascilitates Harvesting of Flushes for MushR (Legacy Substrate)',

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
    'widget_dashboard_body': """<form id='harvest_legacy_form'>

  <label for='legacy_fruiting_hole_uid'>FruitingHole UID:</label><br>

  <select id='legacy_fruiting_hole_uid'></select>

  <label for='legacy_harvest_weight'>Weight of Harvest (in grams):</label><br>
  <input type='number' id='legacy_harvest_weight' name='legacy_harvest_weight'><br>
  <br><br>
  <input type='button' value='Submit' onclick='harvest_legacy_submit()'>
</form>
    <div id="status_mushr_harvest_legacy"></div>
<script>

function fill_select_available_legacy_fruiting_hole_uids(){
    var xhr = new XMLHttpRequest();
    xhr.open('GET', '/mushr_available_legacy_fruiting_hole_uids', true);
  xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
  xhr.onreadystatechange = () => {

    data = JSON.parse(xhr.response);
    console.log(data);
    if (data.uids.length){
        $('#legacy_fruiting_hole_uid').html('');
    for (var i=0; i<data.uids.length; i++)
        $('#legacy_fruiting_hole_uid').append('<option value="'+data.uids[i]+'">'+data.composition[i]+'</option>');
    }
    else
        console.log("Error filling select");
    }
  xhr.send();
    }

function harvest_legacy_submit() {
  // Get the values of the form elements
  var legacy_fruiting_hole_uid = document.getElementById('legacy_fruiting_hole_uid').value;
  var legacy_harvest_weight = document.getElementById('legacy_harvest_weight').value;

  // Create an AJAX request
  var xhr = new XMLHttpRequest();
    xhr.open('GET', '/mushr_harvest_legacy/'+encodeURIComponent(legacy_fruiting_hole_uid)+'/'+encodeURIComponent(legacy_harvest_weight), true);
  xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
  xhr.onreadystatechange = () => {
    data = JSON.parse(xhr.response);
    if (data.success)
       document.getElementById('status_mushr_harvest_legacy').innerHTML='<div class="alert alert-success">'+xhr.response+'</div>';
    else
       document.getElementById('status_mushr_harvest_legacy').innerHTML='<div class="alert alert-danger">'+xhr.response+'</div>';
    }
  xhr.send();
}

fill_select_available_legacy_fruiting_hole_uids();

</script>
""",
    'widget_dashboard_js': """<!-- No JS content -->""",
    'widget_dashboard_js_ready': """<!-- No JS ready content -->""",
    'widget_dashboard_js_ready_end': """<!-- No JS ready end content -->"""
}
