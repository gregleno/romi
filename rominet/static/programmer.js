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
    $("#Play_Note").jqxButton({ width: 50, height: 50, imgWidth: 40, imgHeight: 40,
                                 imgSrc: "static/images/double-note-300px.png" });
    $("#Erase_Program").jqxButton({ width: 50, height: 50, imgWidth: 40, imgHeight: 40,
                                 imgSrc: "static/images/Delete-Button-300px.png" });
    $("#Play_Program").jqxButton({ width: 50, height: 50, imgWidth: 40, imgHeight: 40,
                                 imgSrc: "static/images/round-green-play-button-on-300px.png" });
    $("#Stop_Program").jqxButton({ width: 50, height: 50, imgWidth: 40, imgHeight: 40,
                                 imgSrc: "static/images/Stop-Sign-300px.png" });

    var fields = [
              { name: "resourceId", type: "number" },
              { name: "status", map: "state", type: "string"},
              { name: "id", type: "string" },
    ];
    var source =
     {
         localData: [
                  { state: "new", resourceId: "up", id : 0},
         ],
         dataType: "array",
         dataFields: fields
     };
    var dataAdapter = new $.jqx.dataAdapter(source);
    var resourcesAdapterFunc = function () {
        var resourcesSource =
        {
            localData: [
                  { id: "up", name: "Move Forward", image: "static/images/arrow-orange-up-300px.png"},
                  { id: "down", name: "Move Backward", image: "static/images/arrow-orange-down-300px.png" },
                  { id: "left", name: "Turn Left", image: "static/images/arrow-go-left-300px.png" },
                  { id: "right", name: "Turn Right", image: "static/images/arrow-go-right-300px.png" },
                  { id: "note", name: "Play Note", image: "static/images/double-note-300px.png" },
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

     $('#kanban1').jqxKanban({
        template: "<div class='jqx-kanban-item' id='' >"
                          + "<div class='jqx-kanban-item-avatar'></div>"
                          + "</div>",
        width: '100%',
        height: '600',
        resources: resourcesAdapterFunc(),
        source: dataAdapter,
        columns: [
            { text: "Program", dataField: "new",  maxItems: 7 }
        ]
    });
    $("#Move_Forward").click(function () {
                    $('#kanban1').jqxKanban('addItem', { status: "new", resourceId: "up"});
                });
    $("#Move_Backward").click(function () {
                    $('#kanban1').jqxKanban('addItem', { status: "new", resourceId: "down"});
                });
    $("#Turn_Left").click(function () {
                    $('#kanban1').jqxKanban('addItem', { status: "new", resourceId: "left"});
                });
    $("#Turn_Right").click(function () {
                    $('#kanban1').jqxKanban('addItem', { status: "new", resourceId: "right"});
                });
    $("#Play_Note").click(function () {
                    $('#kanban1').jqxKanban('addItem', { status: "new", resourceId: "note"});
                });
    $("#Erase_Program").click(function () {
                    var items = $('#kanban1').jqxKanban('getItems');
                    items.forEach(function(entry) {
                        if(entry)
                            $('#kanban1').jqxKanban('removeItem', entry.id);
                      });
                });
}