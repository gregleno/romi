"use strict";

function keypad_init() {
    $("#Move_Forward").jqxButton({
        width: 50, height: 50, imgWidth: 40, imgHeight: 40,
        imgSrc: "static/images/arrow-orange-up-300px.png"
    });

    $("#Move_Backward").jqxButton({
        width: 50, height: 50, imgWidth: 40, imgHeight: 40,
        imgSrc: "static/images/arrow-orange-down-300px.png"
    });

    $("#Turn_Left").jqxButton({
        width: 50, height: 50, imgWidth: 40, imgHeight: 40,
        imgSrc: "static/images/arrow-go-left-300px.png"
    });

    $("#Turn_Right").jqxButton({
        width: 50, height: 50, imgWidth: 40, imgHeight: 40,
        imgSrc: "static/images/arrow-go-right-300px.png"
    });

    $("#Play_Note").jqxButton({
        width: 50, height: 50, imgWidth: 40, imgHeight: 40,
        imgSrc: "static/images/double-note-300px.png"
    });

    $("#Stop").jqxButton({
        width: 50, height: 50, imgWidth: 40, imgHeight: 40,
        imgSrc: "static/images/Stop-Sign-300px.png"
    });

    $("#Move_Forward").click(function () {
        $.ajax({
            url: "rominet/api/move_forward",
            type: 'PUT',
            data: JSON.stringify({ distance: 20 }),
            dataType: 'json',
            contentType: 'application/json; charset=utf-8'
        });
    });

    $("#Move_Backward").click(function () {
        $.ajax({
            url: "rominet/api/move_forward",
            type: 'PUT',
            data: JSON.stringify({ distance: -20 }),
            dataType: 'json',
            contentType: 'application/json; charset=utf-8'
        });
    });

    $("#Turn_Left").click(function () {
        $.ajax({
            url: "rominet/api/rotate",
            type: 'PUT',
            data: JSON.stringify({ speed: 20, angle: -90 }),
            dataType: 'json',
            contentType: 'application/json; charset=utf-8'
        });
    });

    $("#Turn_Right").click(function () {
        $.ajax({
            url: "rominet/api/rotate",
            type: 'PUT',
            data: JSON.stringify({ speed: 20, angle: 90 }),
            dataType: 'json',
            contentType: 'application/json; charset=utf-8'
        });
    });

    $("#Play_Note").click(function () {
    });

    $("#Stop").click(function () {
        $.ajax({
            url: "rominet/api/motors",
            type: 'PUT',
            data: JSON.stringify({ left: 0, right: 0 }),
            dataType: 'json',
            contentType: 'application/json; charset=utf-8'
        });
    });
}