# coding=utf-8
import logging


from mycodo.utils.constraints_pass import constraints_pass_positive_value

logger = logging.getLogger(__name__)

WIDGET_INFORMATION = {
    'widget_name_unique': 'html5-qrcode scanner',
    'widget_name': 'QR Code Scanner',
    'widget_library': '',
    'no_class': True,

    'url_manufacturer': '',
    'url_datasheet': '',
    'url_product_purchase': [
    ],
    'url_additional': '',

    'endpoints': [
    ],

    'message': 'This widget can scan a QR code and sets the text of any focused text box',

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
        },
        {
            'id': 'scanner_width',
            'type': 'float',
            'default_value': 400,
            'constraints_pass': constraints_pass_positive_value,
            'name': 'Width',
            'phrase': 'Width of the QR Code scanner'
        }
    ],

    'widget_dashboard_head': """""",
    'widget_dashboard_title_bar': """<span style="padding-right:
    0.5em; font-size:
    {{each_widget.font_em_name}}em">{{each_widget.name}}</span>""",
    'widget_dashboard_body': """
    <script src="https://unpkg.com/html5-qrcode" type="text/javascript"></script>
    <script src="https://code.jquery.com/jquery-3.2.1.min.js"></script>
    <div id='reader'></div>
   <style>
    #reader{
    width: {{widget_options['scanner_width']}}px;
    visibility: visible;
    }
    <div id="reader"></div>
   </style>
    <script>
    function onScanSuccess(decodedText, decodedResult) {
    // handle the scanned code as you like, for example:
    console.log(`Code matched = ${decodedText}`, decodedResult);
    $(":focus").val(decodedResult.decodedText)
    }
    function onScanFailure(error) {
    // handle scan failure, usually better to ignore and keep scanning.
    // for example:
    console.warn(`Code scan error = ${error}`);
    }
    let html5QrcodeScanner = new Html5QrcodeScanner(
    "reader",
    { fps: 10, qrbox: {width: 250, height: 250}},
    /* verbose= */ false);
    html5QrcodeScanner.render(onScanSuccess, onScanFailure);

    </script>

    """,
    'widget_dashboard_js': """<!-- No JS content -->""",
    'widget_dashboard_js_ready': """<!-- No JS ready content -->""",
    'widget_dashboard_js_ready_end': """<!-- No JS ready end content -->"""
}
