"use strict";
function programmer_init(){
    $("#Move_Forward").jqxButton({ width: 50, height: 50, imgWidth: 40, imgHeight: 40,
                                    imgSrc: "static/images/arrow-orange-up-300px.png" });
    $("#Move_Backward").jqxButton({ width: 50, height: 50, imgWidth: 40, imgHeight: 40,
                                    imgSrc: "static/images/arrow-orange-down-300px.png" });
    $("#Turn_Left").jqxButton({ width: 50, height: 50, imgWidth: 40, imgHeight: 40,
                                imgSrc: "static/images/arrow-go-left-300px.png" });
    $("#Turn_Right").jqxButton({ width: 50, height: 50, imgWidth: 40, imgHeight: 40,
                                 imgSrc: "static/images/arrow-go-right-300px.png" });

    var fields = [
              { name: "resourceId", type: "number" },
              { name: "status", map: "state", type: "string" },
              { name: "tags", type: "string" },
              { name: "text", map: "label", type: "string" }

    ];
    var source =
     {
         localData: [
                  { state: "new", resourceId: 3, tags: " ", label: "r " },
                  { state: "new", resourceId: 1, tags: " ", label: "r " },
                  { state: "new", resourceId: 3, tags: " ", label: "r " },
                  { state: "new", resourceId: 0, tags: " ", label: " " },
         ],
         dataType: "array",
         dataFields: fields
     };
    var dataAdapter = new $.jqx.dataAdapter(source);
    var resourcesAdapterFunc = function () {
        var resourcesSource =
        {
            localData: [
                  { id: 0, name: "Move Forward", image: "static/images/arrow-orange-up-300px.png"},
                  { id: 1, name: "Move Backward", image: "static/images/arrow-orange-down-300px.png" },
                  { id: 2, name: "Turn Left", image: "static/images/arrow-go-left-300px.png" },
                  { id: 3, name: "Turn Right", image: "static/images/arrow-go-right-300px.png" },
            ],
            dataType: "array",
            dataFields: [
                 { name: "id", type: "number" },
                 { name: "name", type: "string" },
                 { name: "image", type: "string" },
            ]
        };
        var resourcesDataAdapter = new $.jqx.dataAdapter(resourcesSource);
        return resourcesDataAdapter;
    }

     var templateContent = { status: "new", text: "", content: "", tags: "", color: "green", resourceId: 0, className: ""}
     //$('#kanban1').jqxKanban({ templateContent: templateContent });
     $('#kanban1').jqxKanban({
        template: "<div class='jqx-kanban-item' id=''>"
                             + "<div class='jqx-kanban-item-color-status'></div>"
                             + "<div style='display: none;' class='jqx-kanban-item-avatar'></div>"
                             + "<div class='jqx-icon jqx-icon-close-white jqx-kanban-item-template-content jqx-kanban-template-icon'></div>"
                             + "<div class='jqx-kanban-item-text'></div>"
                             + "<div style='display: none;' class='jqx-kanban-item-footer'></div>"
                     + "</div>",
        width: '50%',
        height: '600',
        resources: resourcesAdapterFunc(),
        source: dataAdapter,
        connectWith: "#kanban2, #kanban3",
        columns: [
            { text: "Backlog", dataField: "new",  maxItems: 10 }
        ],
        columnRenderer: function (element, collapsedElement, column) {
            var columnItems = $("#kanban1").jqxKanban('getColumnItems', column.dataField).length;
            element.find(".jqx-kanban-column-header-status").html(" (" + columnItems + "/" + column.maxItems + ")");
            collapsedElement.find(".jqx-kanban-column-header-status").html(" (" + columnItems + "/" + column.maxItems + ")");
        }
    });
}