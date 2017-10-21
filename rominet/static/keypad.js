"use strict";

function keypad_init(){
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
    $("#Stop_Program").jqxButton({ width: 50, height: 50, imgWidth: 40, imgHeight: 40,
                                 imgSrc: "static/images/Stop-Sign-300px.png" });

    $("#Move_Forward").click(function () {
                });
    $("#Move_Backward").click(function () {
                });
    $("#Turn_Left").click(function () {
                });
    $("#Turn_Right").click(function () {
                });
    $("#Play_Note").click(function () {
                });
    $("#Erase_Program").click(function () {
    });
}