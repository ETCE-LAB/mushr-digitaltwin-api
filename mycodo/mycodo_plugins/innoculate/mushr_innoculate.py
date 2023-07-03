# coding=utf-8
import logging


from mycodo.utils.constraints_pass import constraints_pass_positive_value
from mycodo.user_python_code import mushr_neomodel
from neomodel import db

logger = logging.getLogger(__name__)


def mushr_available_innoculant_uids():
    """Returns a list of SpawnContainer uids of currently available
    Spawn, and Strain uids.

    """

    available_spawn_containers, meta = db.cypher_query("MATCH (sp:Spawn)-[R:IS_CONTAINED_BY]->(spc:SpawnContainer) WHERE NOT exists(R.end) RETURN spc.uid", {})

    available_strain, meta = db.cypher_query("MATCH (st:Strain) return st.uid",
                                             {})

    available_spawn_containers = [uidl[0] for uidl in available_spawn_containers]
    available_strain = [uidl[0] for uidl in available_strain]

    return {"uids": available_spawn_containers + available_strain}


def mushr_available_recipient_container_uids():
    """Returns a list of currently un-innoculated Spawn/Substrate Container
    uids.

    """

    available_recipient_containers, meta = db.cypher_query("MATCH (sp)-[R:IS_CONTAINED_BY]->(spc) WHERE NOT exists(R.end) AND (sp:Spawn OR sp:Substrate) AND NOT exists((sp)-[:IS_INNOCULATED_FROM]->()) return spc.uid", {})

    available_recipient_containers = [uidl[0] for uidl in available_recipient_containers]

    return {"uids": available_recipient_containers}


def mushr_innoculate(innoculant_uid,
                     recipient_container_uid,
                     amount):

    # innoculant_uid might be Strain.uid or SpawnContainer.uid

    innoculant = mushr_neomodel.Strain.nodes.get_or_none(uid=innoculant_uid)

    if not innoculant: # then it is not Strain
        available_spawn, meta = db.cypher_query("MATCH (sp:Spawn)-[R:IS_CONTAINED_BY]->(spc:SpawnContainer) WHERE spc.uid=$spawn_container_uid AND NOT exists(R.end) RETURN sp",
                                                {"spawn_container_uid": innoculant_uid})

        if len(available_spawn[0]) > 1:
            return {"success": False,
                    "error": "SpawnContainer erroneously contains multiple Spawn"}

        if len(available_spawn[0]) == 0:
            return {"success": False,
                    "error": "UID for innoculant is not representative of Strain or SpawnContainer"}

        innoculant = mushr_neomodel.Spawn.inflate(available_spawn[0][0])

    recipient, meta = db.cypher_query("MATCH (sp)-[R:IS_CONTAINED_BY]->(spc) WHERE NOT exists(R.end) AND (sp:Spawn OR sp:Substrate) AND NOT exists((sp)-[:IS_INNOCULATED_FROM]->()) AND spc.uid=$recipient_container_uid RETURN sp",
                                      {"recipient_container_uid": recipient_container_uid})

    if len(recipient[0]) > 1:
        return {"success": False,
                "error": """Recipient Container erroneously contains
                multiple spawn/substrate"""}

    if len(recipient[0]) == 0:
        return {"success": False,
                "error": """UID for Recipient Container does not
                contain any (available and uninnoculated) Spawn or
                Substrate"""}

    if "Spawn" in recipient[0][0].labels:
        recipient = mushr_neomodel.Spawn.inflate(recipient[0][0])
    elif "Substrate" in recipient[0][0].labels:
        recipient = mushr_neomodel.Substrate.inflate(recipient[0][0])
    else:
        return {"success": False,
                "error": """Recipient is neither Spawn nor Substrate"""}

    with db.transaction:
        recipient.is_innoculated_from.connect(innoculant,
                                              {"amount": float(amount)})

    return {"success": True}


WIDGET_INFORMATION = {
    'widget_name_unique': 'mushr_innoculate',
    'widget_name': 'MushR Innoculation Widget',
    'widget_library': '',
    'no_class': True,

    'url_manufacturer': '',
    'url_datasheet': '',
    'url_product_purchase': [
    ],
    'url_additional': '',

    'endpoints': [
        # Route URL, route endpoint name, view function, methods
        ("/mushr_innoculate/<innoculant_uid>/<recipient_container_uid>/<amount>",
         "mushr_innoculate",
         mushr_innoculate, ["GET"]),
        ("/mushr_available_innoculant_uids",
         "mushr_available_innoculant_uids",
         mushr_available_innoculant_uids, ["GET"]),
        ("/mushr_available_recipient_container_uids",
         "mushr_available_recipient_container_uids",
         mushr_available_recipient_container_uids, ["GET"])
    ],

    'message': 'This widget handles innoculation for MushR',

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
    'widget_dashboard_body': """<form id='innoculate_form'>

    <datalist id='available_innoculant_uids'></datalist>

  <label for='innoculant_uid'>Innoculant UID:</label><br>
  <input autocomplete='off' list='available_innoculant_uids' type='text' id='innoculant_uid' name='innoculant_uid'><br>

    <datalist id='available_recipient_container_uids'></datalist>

  <label for='recipient_container_uid'>Recipient Container UID:</label><br>
  <input autocomplete='off' list='available_recipient_container_uids' type='text' id='recipient_container_uid' name='recipient_container_uid'><br>
  <label for='innoculation_amount'>Innocuation Amount:</label><br>
  <input type='number' id='innoculation_amount' name='innoculation_amount'><br>
  <br><br>
  <input type='button' value='Submit' onclick='innoculate_submit()'>
</form>
    <div id="status_mushr_innoculate"></div>
<script>

function fill_datalist_available_innoculant_uids(){
    var xhr = new XMLHttpRequest();
    xhr.open('GET', '/mushr_available_innoculant_uids', true);
  xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
  xhr.onreadystatechange = () => {

    data = JSON.parse(xhr.response);
    console.log(data);

    if (data.uids.length){
        $('#available_innoculant_uids').html('');
    for (var i=0; i<data.uids.length; i++)
        $('#available_innoculant_uids').append('<option>'+data.uids[i]+'</option>');
    }
    else
        console.log("Error filling datalist");
    }
  xhr.send();
    }

function fill_datalist_available_recipient_container_uids(){
    var xhr = new XMLHttpRequest();
    xhr.open('GET', '/mushr_available_recipient_container_uids', true);
  xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
  xhr.onreadystatechange = () => {

    data = JSON.parse(xhr.response);
    console.log(data);

    if (data.uids.length){
        $('#available_recipient_container_uids').html('');
    for (var i=0; i<data.uids.length; i++)
        $('#available_recipient_container_uids').append('<option>'+data.uids[i]+'</option>');
    }
    else
        console.log("Error filling datalist");
    }
  xhr.send();
    }

function innoculate_submit() {
  // Get the values of the form elements
  var innoculant_uid = document.getElementById('innoculant_uid').value;
  var recipient_container_uid = document.getElementById('recipient_container_uid').value;
  var innoculation_amount = document.getElementById('innoculation_amount').value;

  // Create an AJAX request
  var xhr = new XMLHttpRequest();
    xhr.open('GET', '/mushr_innoculate/'+encodeURIComponent(innoculant_uid)+'/'+encodeURIComponent(recipient_container_uid)+'/'+encodeURIComponent(innoculation_amount), true);
  xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
  xhr.onreadystatechange = () => {
    data = JSON.parse(xhr.response);
    if (data.success)
       document.getElementById('status_mushr_innoculate').innerHTML='<div class="alert alert-success">'+xhr.response+'</div>';
    else
       document.getElementById('status_mushr_innoculate').innerHTML='<div class="alert alert-danger">'+xhr.response+'</div>';
    }
  xhr.send();
}

fill_datalist_available_innoculant_uids();
fill_datalist_available_recipient_container_uids();

</script>
""",
    'widget_dashboard_js': """<!-- No JS content -->""",
    'widget_dashboard_js_ready': """<!-- No JS ready content -->""",
    'widget_dashboard_js_ready_end': """<!-- No JS ready end content -->"""
}
