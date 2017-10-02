
$(function(){

    var client_width = $("body")[0].clientWidth;

    function float_row_translate(float_board, re_start) {
        var board_width = float_board[0].scrollWidth;

        if (re_start) {
            float_board.find(".float_row").each(function() {
                $(this).css("left", Math.random() * 380);
            });
            float_board.css("transition", "none").css("left", client_width);
        }

        float_board[0].style.transition = "left " + (board_width + float_board.position().left) * 0.012 + 's linear';
        float_board[0].style.left = '-' + board_width + "px";
    }

    $("#float_board").find(".float_row").each(function() {
        $(this).css("left", Math.random() * 380);
    });
    $("#float_board").css("left", $("body")[0].clientWidth).show();

    float_row_translate($("#float_board"));

    $("#float_board").hover(function() {
        $(this).css("left", $(this).css("left"));
    }, function() {
        float_row_translate($(this));
    });

    $("#float_board").on($.support.transition.end, function() {
        float_row_translate($(this), true);
    });

});
