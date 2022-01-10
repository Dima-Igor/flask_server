$(document).ready(function() {
    const socket = io.connect('http://127.0.0.1:5000');

    $('.stats-card').hide();

    $('.handle-form').submit(function(event) {
        event.preventDefault();
        handle = $('.input-handle').val();
        socket.send({ 'handle': handle });
    });


    function drawStats(stats) {
        $('.solved-tasks').text(stats.handle);
        $('.unsolved-tasks').text(stats.handle);
    };

    function calcStats(data) {

    };

    socket.on('message', function(data) {
        console.log(data);
        //2 типа смс
        //1 - что-то посчитать 
        //2 - результат статы
        drawStats(data);
        $('.stats-card').show();
    });

});