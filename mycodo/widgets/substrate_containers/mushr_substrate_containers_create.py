# coding=utf-8
import logging

from mycodo.utils.constraints_pass import constraints_pass_positive_value
from mycodo.user_python_code import mushr_neomodel
from neomodel import db

logger = logging.getLogger(__name__)


def mushr_substrate_container_create(volume, description, fruiting_hole_count):
    """
    """

    s = mushr_neomodel.SubstrateContainer(volume=volume,
                                          description=description)
    fhs = []
    for i in range(int(fruiting_hole_count)):
        fhs.append(mushr_neomodel.FruitingHole())

    with db.transaction:
        s.save()
        for fh in fhs:
            fh.save()
            fh.is_part_of.connect(s)

    return {"success": True,
            "substrate_container": {"uid": s.uid,
                                    "fruiting_holes":
                                    [{"uid": fh.uid} for fh in fhs]}}


WIDGET_INFORMATION = {
    'widget_name_unique': 'mushr_substrate_container_create',
    'widget_name': 'MushR SubstrateContainer Creation Widget',
    'widget_library': '',
    'no_class': True,

    'url_manufacturer': '',
    'url_datasheet': '',
    'url_product_purchase': [
    ],
    'url_additional': '',

    'endpoints': [
        # Route URL, route endpoint name, view function, methods
        ("/mushr_substrate_container_create/<volume>/<description>/<fruiting_hole_count>",
         "mushr_substrate_container_create",
         mushr_substrate_container_create, ["GET"])
    ],

    'message': 'This widget creates SubstrateContainers for MushR',

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
    'widget_dashboard_body': """<form id='substrate_container_create_form'>
  <label for='substrate_container_volume'>Volume:</label><br>
  <input type='number' id='substrate_container_volume' name='substrate_container_volume'><br>
  <label for='substrate_container_description'>Description:</label><br>
  <textarea id='substrate_container_description' name='substrate_container_description'></textarea><br>
  <label for='fruiting_hole_count'>No. of Fruiting Holes</label><br>
  <input type='number' id='fruiting_hole_count' name='fruiting_hole_count'><br>
  <br><br>
  <input type='button' value='Submit' onclick='substrate_container_create_submit()'>
</form>
    <div id="status_mushr_substrate_container_create"></div>
<script>
function substrate_container_create_submit() {
  // Get the values of the form elements
  var volume = document.getElementById('substrate_container_volume').value;
  var description = document.getElementById('substrate_container_description').value;
  var fh = document.getElementById('fruiting_hole_count').value;

  // Create an AJAX request
  var xhr = new XMLHttpRequest();
    xhr.open('GET', '/mushr_substrate_container_create/'+encodeURIComponent(volume)+'/'+encodeURIComponent(description)+'/'+encodeURIComponent(fh), true);
  xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
  xhr.onload = () => {
    data = JSON.parse(xhr.response)
    if (data.success){
    document.getElementById('status_mushr_substrate_container_create').innerHTML='<div class="alert alert-success">'+xhr.response+'</div>';
    generate_substrate_qrcodes(data.substrate_container)
    }
    else
       document.getElementById('status_mushr_substrate_container_create').innerHTML='<div class="alert alert-danger">'+xhr.response+'</div>';
    }
  xhr.send();
}

function generate_substrate_qrcodes(substrate_container){
    $("#qrcodes").append("<div style='outline:solid 1px;'>")
    $("#qrcodes").append("<label style='font-size: 13px;' for='"+substrate_container.uid+"'>SubC: "+substrate_container.uid+"</label><br>")
    $("#qrcodes").append("<div id='"+substrate_container.uid+"'></div><br>")
    qrcode = new QRCode(substrate_container.uid, substrate_container.uid)

    for(i=0;i<substrate_container.fruiting_holes.length;i++){
    $("#qrcodes").append("<label style='font-size: 13px;' for='"+substrate_container.fruiting_holes[i].uid+"'>FH: "+substrate_container.fruiting_holes[i].uid+"</label><br>")
    $("#qrcodes").append("<div id='"+substrate_container.fruiting_holes[i].uid+"'></div><br>")
    qrcode = new QRCode(substrate_container.fruiting_holes[i].uid, substrate_container.fruiting_holes[i].uid)

    }

    $("#qrcodes").append("</div>")
    }

</script>
""",
    'widget_dashboard_js': """<!-- No JS content -->""",
    'widget_dashboard_js_ready': """<!-- No JS ready content -->""",
    'widget_dashboard_js_ready_end': """<!-- No JS ready end content -->"""
}
