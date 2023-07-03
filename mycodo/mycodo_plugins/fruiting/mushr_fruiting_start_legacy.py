# coding=utf-8
import logging


from mycodo.utils.constraints_pass import constraints_pass_positive_value
from mycodo.user_python_code import mushr_neomodel
from neomodel import db

logger = logging.getLogger(__name__)


def mushr_available_legacy_substrate_uids():
    """Returns a list of Substrate uids of Substrate that does not
    have a SubstrateContainer

    """

    legacy_substrate, meta = db.cypher_query("MATCH (sub:Substrate) WHERE NOT (sub)-[:IS_CONTAINED_BY]->(:SubstrateContainer) return sub.uid, sub.composition", {})

    legacy_substrate_uids = [row[0] for row in legacy_substrate]
    legacy_substrate_composition = [row[1] for row in legacy_substrate]

    return {"uids": legacy_substrate_uids,
            "composition": legacy_substrate_composition}


def mushr_fruiting_start_legacy(legacy_substrate_uid):
    """
    """

    fruiting_hole = mushr_neomodel.FruitingHole()  # Create a dummy fruiting hole

    substrate = mushr_neomodel.Substrate.nodes.get_or_none(uid=legacy_substrate_uid)

    if ((not substrate) or (legacy_substrate_uid not in
                            mushr_available_legacy_substrate_uids()["uids"])):

        return {"success": False,
                "error": """Substrate UID is not associated with any
                legacy Substrate"""}

    flush = mushr_neomodel.Flush()

    db.begin()
    try:

        flush.save()
        fruiting_hole.save()
        flush.fruits_from.connect(substrate)
        flush.fruits_through.connect(fruiting_hole)
        db.commit()

    except Exception as E:
        db.rollback()
        return {"success": False,
                "error": str(E)}

    return {"success": True}


WIDGET_INFORMATION = {
    'widget_name_unique': 'mushr_fruiting_start_legacy',
    'widget_name': 'MushR Fruiting Start Widget for legacy MushR spreadsheet compatibility (Does not require a SubstrateContainer)',
    'widget_library': '', 'no_class': True,

    'url_manufacturer': '',
    'url_datasheet': '',
    'url_product_purchase': [
    ],
    'url_additional': '',

    'endpoints': [
        # Route URL, route endpoint name, view function, methods
        ("/mushr_fruiting_start_legacy/<legacy_substrate_uid>",
         "mushr_fruiting_start_legacy",
         mushr_fruiting_start_legacy, ["GET"]),
        ("/mushr_available_legacy_substrate_uids",
         "mushr_available_legacy_substrate_uids",
         mushr_available_legacy_substrate_uids, ["GET"])
    ],

    'message': 'This widget fascilites fruiting start for legacy MushR Substrates (Substrates that are not associated with a substrate container)',

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
    'widget_dashboard_body': """<form id='fruiting_legacy_form'>

  <label for='legacy_substrate_uid'>Legacy Substrate UID:</label><br>
  <select id='legacy_substrate_uid' name='legacy_substrate_uid'></select>

  <br><br>
  <input type='button' value='Submit' onclick='fruiting_legacy_submit()'>
</form>
    <div id="status_mushr_fruiting_start_legacy"></div>
<script>

function fill_select_available_legacy_substrate_uids(){
    var xhr = new XMLHttpRequest();
    xhr.open('GET', '/mushr_available_legacy_substrate_uids', true);
  xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
  xhr.onreadystatechange = () => {

    data = JSON.parse(xhr.response);
    console.log(data);

    if (data.uids.length){
        $('#legacy_substrate_uid').html('');
    for (var i=0; i<data.uids.length; i++)
        $('#legacy_substrate_uid').append('<option value="'+data.uids[i]+'">'+data.composition[i]+'</option>');
    }
    else
        console.log("Error filling select");
    }
    xhr.send();
    }
fill_select_available_legacy_substrate_uids();

function fruiting_legacy_submit() {
  // Get the values of the form elements
  var legacy_substrate_uid = document.getElementById('legacy_substrate_uid').value;

  // Create an AJAX request
  var xhr = new XMLHttpRequest();
    xhr.open('GET', '/mushr_fruiting_start_legacy/'+encodeURIComponent(legacy_substrate_uid), true);
  xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
  xhr.onreadystatechange = () => {
    data = JSON.parse(xhr.response);
    if (data.success)
       document.getElementById('status_mushr_fruiting_start_legacy').innerHTML='<div class="alert alert-success">'+xhr.response+'</div>';
    else
       document.getElementById('status_mushr_fruiting_start_legacy').innerHTML='<div class="alert alert-danger">'+xhr.response+'</div>';
    }
  xhr.send();
}

</script>
""",
    'widget_dashboard_js': """<!-- No JS content -->""",
    'widget_dashboard_js_ready': """<!-- No JS ready content -->""",
    'widget_dashboard_js_ready_end': """<!-- No JS ready end content -->"""
}
