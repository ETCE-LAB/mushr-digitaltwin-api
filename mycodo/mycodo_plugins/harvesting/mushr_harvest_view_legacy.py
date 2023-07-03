# coding=utf-8
import logging
import os

from mycodo.utils.constraints_pass import constraints_pass_positive_value

logger = logging.getLogger(__name__)

WIDGET_INFORMATION = {
    'widget_name_unique': 'mushr_harvest_view_legacy',
    'widget_name': 'MushR Harvest View Widget (For Only Legacy Substrate)',
    'widget_library': '',
    'no_class': True,

    'url_manufacturer': '',
    'url_datasheet': '',
    'url_product_purchase': [
    ],
    'url_additional': '',

    'endpoints': [
    ],

    'message': 'This widget views Harvest history (and fascilitates harvesting for legacy Substrate) for MushR',

    # Any dependencies required by the output module. An empty list means no dependencies are required.
    'dependencies_module': [],

    # A message to be displayed on the dependency install page
    'dependencies_message': 'Are you sure you want to install these dependencies? They require...',

    'widget_width': 20,
    'widget_height': 20,

    'custom_options': [
        {
            'id': 'neo4j_username',
            'type': 'text',
            'default_value': "neo4j",
            'name': 'Neo4j Username',
            'phrase': 'Username for neo4j'
        },
        {
            'id': 'neo4j_password',
            'type': 'text',
            'default_value': "neo4j",
            'name': 'Neo4j Password',
            'phrase': 'Password for neo4j'
        },
        {
            'id': 'neo4j_host_url',
            'type': 'text',
            'default_value': "localhost:7687",
            'name': 'Neo4j Host URL',
            'phrase': 'The host URL for neo4j'
        },
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
<html>
  <body>
<style type="text/css">
  #viz_harvest_legacy {
      width: 100%;
      height: 90%;
      border: 1px solid lightgray;
      font: 22pt arial;
  }
</style>
<script src="https://code.jquery.com/jquery-3.2.1.min.js"></script>
<script src="https://unpkg.com/neovis.js@2.0.2"></script>
<script type="text/javascript">
  var viz_harvest_legacy;

  function draw_harvest_legacy(datetime) {
      posix_epoch = datetime.getTime()/1000;

      var initial_cypher = "MATCH (mh:MushroomHarvest)-[r1:IS_HARVESTED_FROM]->(fl) WHERE mh.dateHarvested <= "+posix_epoch+" RETURN mh,r1,fl";

      var update_cyphers_harvest_legacy = [

    "MATCH (fl)-[r1:FRUITS_THROUGH]->(fh) WHERE r1.start <= "+posix_epoch+" AND r1.start >= 1667430000.00 AND (not exists(r1.end) or r1.end >= "+posix_epoch+") WITH fl, fh, r1 MATCH (fl)-[r2:FRUITS_FROM]->(sub:Substrate) WHERE sub.dateCreated >= 1667430000.00 and not (sub)-[:IS_CONTAINED_BY]->(:SubstrateContainer) RETURN sub, fl, fh, r1, r2" // Get currently fruiting legacy flushes

    ];


    var CustomTitleHTML = function(neo4jObject, titleProperties)  {

	const title=document.createElement("div");

        titleHTML = ""
	console.log(neo4jObject);

	if (neo4jObject.labels) // It's a node
	{

	for(i=0; i<neo4jObject.labels.length;i++) {
	    titleHTML += '<span style="padding-right:0.5em"><u>'+neo4jObject.labels[i]+'</u></span>'
	}

	}
	else { // It's a relation

	    titleHTML += '<span class="label label-success">'+neo4jObject.type+'</span>'
	    
	} 

	if (Object.keys( neo4jObject.properties ).length > 0){
	titleHTML += '<br>'
	titleHTML += '<br>'

	for(var propt in neo4jObject.properties){

	    if (["dateCreated", "start", "end", "dateHarvested", "timestamp", "dateSterilized"].includes(propt,0))
		titleHTML += '<b>'+propt+'</b> : '+(new Date(neo4jObject.properties[propt]*1000))+'<br>'
	    else
		titleHTML += '<b>'+propt+'</b> : '+neo4jObject.properties[propt]+'<br>'
	}
	    
	}

	title.innerHTML = titleHTML;

	return title

    };



      console.log(initial_cypher);
      var config = {
	  containerId: "viz_harvest_legacy",
	  neo4j: {
	      serverUrl: "bolt://{{widget_options['neo4j_host_url']}}",
	      serverUser: "{{widget_options['neo4j_username']}}",
	      serverPassword: "{{widget_options['neo4j_password']}}"
	  },
	  visConfig: {
	      edges: {
		  arrows: {to: {enabled:true}}
	      }
	  },
          labels: {
	      GrowChamber: {
		  label: "name",
		  title: "GrowChamber",
		  [NeoVis.NEOVIS_ADVANCED_CONFIG]: {
		      static: {
			  color: "#657b83",
		      },
		      function: {
			  title: CustomTitleHTML
		      }
		  }
	      },
	      StorageLocation: {
		  label: "name",
		  [NeoVis.NEOVIS_ADVANCED_CONFIG]: {
		      static: {
			  color: "#657b83",
		      },
		      function: {
			  title: CustomTitleHTML
		      }
		  }
	      },
	      Strain: {
		  label: "species",
		  value: "weight",
		  [NeoVis.NEOVIS_ADVANCED_CONFIG]: {
		      static: {
			  color: "#859900",
			  shape: "dot",
		      },
		      function: {
			  title: CustomTitleHTML
		      }
		  }
	      },
	      SpawnContainer: {
		  label: "name",
		  value: "volume",
		  [NeoVis.NEOVIS_ADVANCED_CONFIG]: {
		      static: {
			  color: "#eee8d5",
			  shape: "dot"
		      },
		      function: {
			  title: CustomTitleHTML
		      }
		  }
	      },
	      MyceliumSample: {
		  [NeoVis.NEOVIS_ADVANCED_CONFIG]: {
		      static: {
			  color: "#b58900",
		      },
		      function: {
			  title: CustomTitleHTML
		      }
		  }
	      },
	      Spawn: {
		  [NeoVis.NEOVIS_ADVANCED_CONFIG]: {
		      static: {
			  color: "#b58900",
		      },
		      function: {
			  title: CustomTitleHTML
		      }
		  }
	      },
	      SubstrateContainer: {
		  label: "name",
		  value: "volume",
		  [NeoVis.NEOVIS_ADVANCED_CONFIG]: {
		      static: {
			  color: "#fdf6e3"
		      },
		      function: {
			  title: CustomTitleHTML
		      }
		  }
	      },
	      Substrate: {
		  label: "name",
		  value: "weight",
		  [NeoVis.NEOVIS_ADVANCED_CONFIG]: {
		      static: {
			  color: "#d33682",
		      },
		      function: {
			  title: CustomTitleHTML
		      }
		  }
	      },
	      FruitingHole: {
		  [NeoVis.NEOVIS_ADVANCED_CONFIG]: {
		      static: {
			  color: "#586e75",
			  shape: "dot",
			  size: 10
		      },
		      function: {
			  title: CustomTitleHTML
		      }
		  }
	      },
	      Flush: {
		  [NeoVis.NEOVIS_ADVANCED_CONFIG]: {
		      static: {
			  color: "#268bd2",
			  shape: "star"
		      },
		      function: {
			  title: CustomTitleHTML
		      }
		  }
	      },
	      MushroomHarvest: {
		  value: "weight",
		  [NeoVis.NEOVIS_ADVANCED_CONFIG]: {
		      static: {
			  color: "#2aa198",
			  shape: "star"
		      },
		      function: {
			  title: CustomTitleHTML
		      }
		  }
	      },
	      Sensor: {
		  label: "sensorType",
		  [NeoVis.NEOVIS_ADVANCED_CONFIG]: {
		      static: {
			  shape: "star",
			  size: 10
		      },
		      function: {
			  title: CustomTitleHTML
		      }
		  }
	      }
	  },
	  relationships: {
	      IS_LOCATED_AT: {
		  [NeoVis.NEOVIS_ADVANCED_CONFIG]: {
		      static: {
			  label: "IS_LOCATED_AT",
		      },
		      function: {
			  title: CustomTitleHTML
		      },
		  }
	      },
	      IS_INNOCULATED_FROM: {
		  [NeoVis.NEOVIS_ADVANCED_CONFIG]: {
		      static: {
			  label: "IS_INNOCULATED_FROM",
		      },
		      function: {
			  title: CustomTitleHTML
		      },
		  }
	      },
	      IS_PART_OF: {
		  [NeoVis.NEOVIS_ADVANCED_CONFIG]: {
		      static: {
			  label: "IS_PART_OF",
		      },
		      function: {
			  title: CustomTitleHTML
		      },
		  }
	      },
	      IS_CONTAINED_BY: {
		  [NeoVis.NEOVIS_ADVANCED_CONFIG]: {
		      static: {
			  label: "IS_CONTAINED_BY",
		      },
		      function: {
			  title: CustomTitleHTML
		      },
		  }
	      },
	      FRUITS_FROM: {
		  [NeoVis.NEOVIS_ADVANCED_CONFIG]: {
		      static: {
			  label: "FRUITS_FROM",
		      },
		      function: {
			  title: CustomTitleHTML
		      },
		  }
	      },
	      FRUITS_THROUGH: {
		  [NeoVis.NEOVIS_ADVANCED_CONFIG]: {
		      static: {
			  label: "FRUITS_THROUGH",
		      },
		      function: {
			  title: CustomTitleHTML
		      },
		  }
	      },
	      IS_HARVESTED_FROM: {
		  [NeoVis.NEOVIS_ADVANCED_CONFIG]: {
		      static: {
			  label: "IS_HARVESTED_FROM",
		      },
		      function: {
			  title: CustomTitleHTML
		      },
		  }
	      },
	      IS_SENSING_IN: {
		  [NeoVis.NEOVIS_ADVANCED_CONFIG]: {
		      static: {
			  label: "IS_SENSING_IN",
		      },
		      function: {
			  title: CustomTitleHTML
		      },
		  }
	      }
          },
    initialCypher: initial_cypher};

      viz_harvest_legacy = new NeoVis.default(config);
      viz_harvest_legacy.render();
    for(var i = 0; i<update_cyphers_harvest_legacy.length;i++)
    {
    console.log(update_cyphers_harvest_legacy[i]);
    viz_harvest_legacy.updateWithCypher(update_cyphers_harvest_legacy[i]);
    }
  }
  $("document").ready(function(){
      draw_harvest_legacy(new Date())
  });
</script>

<div id="viz_harvest_legacy"> </div>
<div class="input-group">
  <input id="datetime_viz_harvest_legacy" type="datetime-local" class="form-control" placeholder="Datetime" aria-label="Visualization DateTime" aria-describedby="basic-addon2">
  <div class="input-group-append">
    <button id="datetime_viz_harvest_legacy_button" class="btn btn-outline-secondary" type="button">R</button>
  </div>
</div>

<script type="text/javascript">
  $("#datetime_viz_harvest_legacy_button").click(function(){
      draw_harvest_legacy(new Date($("#datetime_viz_harvest_legacy").val()))
  });

  date = new Date()

  offset = date.getTimezoneOffset()

document.querySelector('input[type="datetime-local"]').value = new Date(date.getTime()-60*offset*1000).toISOString().slice(0,-1);
</script>
    </html>
    """,
    'widget_dashboard_js': """<!-- No JS content -->""",
    'widget_dashboard_js_ready': """<!-- No JS ready content -->""",
    'widget_dashboard_js_ready_end': """<!-- No JS ready end content -->"""
}
