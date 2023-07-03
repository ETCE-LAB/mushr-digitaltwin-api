# coding=utf-8
import logging


from mycodo.utils.constraints_pass import constraints_pass_positive_value

logger = logging.getLogger(__name__)

WIDGET_INFORMATION = {
    'widget_name_unique': 'barcode_generator',
    'widget_name': 'Barcode Generator',
    'widget_library': '',
    'no_class': True,

    'url_manufacturer': '',
    'url_datasheet': '',
    'url_product_purchase': [
    ],
    'url_additional': '',

    'endpoints': [
    ],

    'message': 'This widget can generate a barcode',

    # Any dependencies required by the output module. An empty list means no dependencies are required.
    'dependencies_module': [],

    # A message to be displayed on the dependency install page
    'dependencies_message': 'Are you sure you want to install these dependencies? They require...',

    'widget_width': 20,
    'widget_height': 20,

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

    'widget_dashboard_head': """""",
    'widget_dashboard_title_bar': """<span style="padding-right:
    0.5em; font-size:
    {{each_widget.font_em_name}}em">{{each_widget.name}}</span>""",
    'widget_dashboard_body': """
    <script src="https://cdn.jsdelivr.net/jsbarcode/3.3.20/JsBarcode.all.min.js"></script>
    <script>

    var gen_QR = function(){

    barcode_string = $("#barcode_string").val()
    $("#barcodes").append("<canvas id='"+barcode_string+"'></canvas><br>")

    $("#"+barcode_string).JsBarcode(barcode_string)
    
    }
    
    </script>
    <input type="text" id="barcode_string" placeholder="Put some text here"/><input type="button" onclick="gen_QR()" value="Generate" />
    <div id='barcodes'></div>
   <style>
    #barcodes{
    width: 100%;
    height: 100%;
    visibility: visible;
    }
   </style>
    """,
    'widget_dashboard_js': """<!-- No JS content -->""",
    'widget_dashboard_js_ready': """<!-- No JS ready content -->""",
    'widget_dashboard_js_ready_end': """<!-- No JS ready end content -->"""
}
