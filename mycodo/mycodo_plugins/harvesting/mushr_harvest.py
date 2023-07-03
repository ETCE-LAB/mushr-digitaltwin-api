# coding=utf-8
import logging

from mycodo.utils.constraints_pass import constraints_pass_positive_value
from mycodo.user_python_code import mushr_neomodel
from neomodel import db

logger = logging.getLogger(__name__)


def mushr_harvestable_fruiting_hole_uids():
    """Returns a list of fruiting holes which have flushes currently
    fruiting through them"""

    available_fruiting_hole_uids, meta = db.cypher_query("MATCH (fh:FruitingHole)<-[r1:FRUITS_THROUGH]-(:Flush) WHERE not exists(r1.end) return fh.uid", {})

    available_fruiting_hole_uids = [uidl[0] for uidl in available_fruiting_hole_uids]

    return {"uids": available_fruiting_hole_uids}


def mushr_harvest(fruiting_hole_uid, weight):
    """
    """

    fruiting_hole = mushr_neomodel.FruitingHole.nodes.get_or_none(uid=fruiting_hole_uid)

    if ((not fruiting_hole) or (fruiting_hole_uid not in
                                mushr_harvestable_fruiting_hole_uids()["uids"])):
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
    'widget_name_unique': 'mushr_harvest',
    'widget_name': 'MushR Harvesting Widget',
    'widget_library': '',
    'no_class': True,

    'url_manufacturer': '',
    'url_datasheet': '',
    'url_product_purchase': [
    ],
    'url_additional': '',

    'endpoints': [
        # Route URL, route endpoint name, view function, methods
        ("/mushr_harvest/<fruiting_hole_uid>/<weight>",
         "mushr_harvest",
         mushr_harvest, ["GET"]),
        ("/mushr_harvestable_fruiting_hole_uids",
         "mushr_harvestable_fruiting_hole_uids",
         mushr_harvestable_fruiting_hole_uids, ["GET"])
    ],

    'message': 'This widget fascilitates Harvesting of Flushes for MushR',

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
    'widget_dashboard_body': """<form id='harvest_form'>

    <datalist id='available_fruiting_hole_uids'></datalist>

  <label for='fruiting_hole_uid'>FruitingHole UID:</label><br>
  <input autocomplete='off' list='available_fruiting_hole_uids' type='text' id='fruiting_hole_uid' name='fruiting_hole_uid'><br>
  <label for='harvest_weight'>Weight of Harvest (in grams):</label><br>
  <input type='number' id='harvest_weight' name='harvest_weight'><br>
  <br><br>
  <input type='button' value='Submit' onclick='harvest_submit()'>
</form>
    <div id="status_mushr_harvest"></div>
<script>

function fill_datalist_available_fruiting_hole_uids(){
    var xhr = new XMLHttpRequest();
    xhr.open('GET', '/mushr_harvestable_fruiting_hole_uids', true);
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

function harvest_submit() {
  // Get the values of the form elements
  var fruiting_hole_uid = document.getElementById('fruiting_hole_uid').value;
  var harvest_weight = document.getElementById('harvest_weight').value;

  // Create an AJAX request
  var xhr = new XMLHttpRequest();
    xhr.open('GET', '/mushr_harvest/'+encodeURIComponent(fruiting_hole_uid)+'/'+encodeURIComponent(harvest_weight), true);
  xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
  xhr.onreadystatechange = () => {
    data = JSON.parse(xhr.response);
    if (data.success)
       document.getElementById('status_mushr_harvest').innerHTML='<div class="alert alert-success">'+xhr.response+'</div>';
    else
       document.getElementById('status_mushr_harvest').innerHTML='<div class="alert alert-danger">'+xhr.response+'</div>';
    }
  xhr.send();
}

fill_datalist_available_fruiting_hole_uids();

</script>
""",
    'widget_dashboard_js': """<!-- No JS content -->""",
    'widget_dashboard_js_ready': """<!-- No JS ready content -->""",
    'widget_dashboard_js_ready_end': """<!-- No JS ready end content -->"""
}
