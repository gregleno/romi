"use strict";

function programmer_init() {
    $("#Prog_Move_Forward").jqxButton({
        width: 50, height: 50, imgWidth: 40, imgHeight: 40,
        imgSrc: "static/images/arrow-orange-up-300px.png"
    });
    $("#Prog_Move_Backward").jqxButton({
        width: 50, height: 50, imgWidth: 40, imgHeight: 40,
        imgSrc: "static/images/arrow-orange-down-300px.png"
    });
    $("#Prog_Turn_Left").jqxButton({
        width: 50, height: 50, imgWidth: 40, imgHeight: 40,
        imgSrc: "static/images/arrow-go-left-300px.png"
    });
    $("#Prog_Turn_Right").jqxButton({
        width: 50, height: 50, imgWidth: 40, imgHeight: 40,
        imgSrc: "static/images/arrow-go-right-300px.png"
    });
    $("#Prog_Play_Note").jqxButton({
        width: 50, height: 50, imgWidth: 40, imgHeight: 40,
        imgSrc: "static/images/double-note-300px.png"
    });
    $("#Prog_Erase_Program").jqxButton({
        width: 50, height: 50, imgWidth: 40, imgHeight: 40,
        imgSrc: "static/images/Delete-Button-300px.png"
    });
    $("#Prog_Play_Program").jqxButton({
        width: 50, height: 50, imgWidth: 40, imgHeight: 40,
        imgSrc: "static/images/round-green-play-button-on-300px.png"
    });
    $("#Prog_Stop_Program").jqxButton({
        width: 50, height: 50, imgWidth: 40, imgHeight: 40,
        imgSrc: "static/images/Stop-Sign-300px.png"
    });

    var fields = [
        { name: "resourceId", type: "number" },
        { name: "status", map: "state", type: "string" },
        { name: "id", type: "string" },
    ];
    var source =
        {
            localData: [
                { state: "new", resourceId: "up", id: "0"},
            ],
            dataType: "array",
            dataFields: fields
        };
    var dataAdapter = new $.jqx.dataAdapter(source);
    var resourcesAdapterFunc = function () {
        var resourcesSource =
            {
                localData: [
                    { id: "up", name: "Move Forward", image: "static/images/arrow-orange-up-300px.png" },
                    { id: "down", name: "Move Backward", image: "static/images/arrow-orange-down-300px.png"},
                    { id: "left", name: "Turn Left", image: "static/images/arrow-go-left-300px.png"},
                    { id: "right", name: "Turn Right", image: "static/images/arrow-go-right-300px.png"},
                    { id: "note", name: "Play Note", image: "static/images/double-note-300px.png"},
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
            { text: "Program", dataField: "new", maxItems: 12 }
        ]
    });
    $("#Prog_Move_Forward").click(function () {
        $('#kanban1').jqxKanban('addItem', { status: "new", resourceId: "up" });
    });
    $("#Prog_Move_Backward").click(function () {
        $('#kanban1').jqxKanban('addItem', { status: "new", resourceId: "down" });
    });
    $("#Prog_Turn_Left").click(function () {
        $('#kanban1').jqxKanban('addItem', { status: "new", resourceId: "left" });
    });
    $("#Prog_Turn_Right").click(function () {
        $('#kanban1').jqxKanban('addItem', { status: "new", resourceId: "right" });
    });
    $("#Prog_Play_Note").click(function () {
        $('#kanban1').jqxKanban('addItem', { status: "new", resourceId: "note" });
    });
    $("#Prog_Erase_Program").click(function () {
        interrupted = true;
        stop_robot();
        var items = $('#kanban1').jqxKanban('getItems');
        items.forEach(function (entry) {
            if (entry)
                $('#kanban1').jqxKanban('removeItem', entry.id);
        });
    });

    $("#Prog_Play_Program").click(function () {
        if(!$('#Prog_Play_Program').jqxButton('disabled')){
            play_program(0);
        }
    });
    $("#Prog_Stop_Program").click(function () {
        interrupted = true;
        stop_robot();
    });

}
var interrupted = false;

function play_program(index) {
    console.log("play index " + index);
    var items = $('#kanban1').jqxKanban('getItems');
    if(items.length > index - 1){
        //$('#kanban1').jqxKanban('updateItem', items[index-1].id, { enabled: false });
    }
    if(interrupted) {
        $("#Prog_Play_Program").jqxButton({disabled: false});   
        interrupted = false 
        return;
    }
    if(index == 0){
        $("#Prog_Play_Program").jqxButton({
            disabled: true
        });    
    }
    if(items.length > index){
        console.log(items[index]);
        do_action(items[index].resourceId);
        //$('#kanban1').jqxKanban('updateItem', items[index].id, { enabled: true });
        setTimeout(play_program, 4000, index+1);
    } else {
        $("#Prog_Play_Program").jqxButton({disabled: false});   
    }
}

function do_action(resourceId) {
    if(resourceId == "up"){
        move_forward();
    } else if(resourceId == "down"){
        move_backward();
    } else if(resourceId == "left"){
        turn_left();
    } else if(resourceId == "right"){
        turn_right();
    } else if(resourceId == "note"){
    }
}    

function turn_left() {
    $.ajax({
        url: "rominet/api/rotate",
        type: 'PUT',
        data: JSON.stringify({ speed: 60, angle: -90 }),
        dataType: 'json',
        contentType: 'application/json; charset=utf-8'
    });
}

function turn_right() {
    $.ajax({
        url: "rominet/api/rotate",
        type: 'PUT',
        data: JSON.stringify({ speed: 60, angle: 90 }),
        dataType: 'json',
        contentType: 'application/json; charset=utf-8'
    });
}

function move_forward() {
    $.ajax({
        url: "rominet/api/move_forward",
        type: 'PUT',
        data: JSON.stringify({ distance: 0.25, speed: 30 }),
        dataType: 'json',
        contentType: 'application/json; charset=utf-8'
    });
}

function move_backward() {
    $.ajax({
        url: "rominet/api/move_forward",
        type: 'PUT',
        data: JSON.stringify({ distance: -0.25, speed: 30 }),
        dataType: 'json',
        contentType: 'application/json; charset=utf-8'
    });
}

function stop_robot() {
    $.ajax({
        url: "rominet/api/motors",
        type: 'PUT',
        data: JSON.stringify({ left: 0, right: 0 }),
        dataType: 'json',
        contentType: 'application/json; charset=utf-8'
    });
}